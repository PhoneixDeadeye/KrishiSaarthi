import os, sys, time, json, glob, warnings
import torch
import numpy as np
import joblib
warnings.filterwarnings("ignore")

# ─── PATHS ────────────────────────────────────────────────────────────────────
BACKEND  = r"c:\Users\agarw\OneDrive\Desktop\Rohan\Crop (Capstone Project '26)\backend"
FRONTEND = r"c:\Users\agarw\OneDrive\Desktop\Rohan\Crop (Capstone Project '26)\frontend"
ML_DIR   = os.path.join(BACKEND, "ml_engine")
sys.path.insert(0, BACKEND)
sys.path.insert(0, ML_DIR)

# ─── OUTPUT FILE — saves next to the script ───────────────────────────────────
OUTPUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "krishisaarthi_results.txt"
)

SKIP_DIRS = {".venv","venv","node_modules","__pycache__",
             "migrations","site-packages",".git","dist","build"}

def safe_walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        yield dirpath, dirnames, filenames

# ─── TEE: write to both stdout and file ───────────────────────────────────────
class Tee:
    def __init__(self, path):
        self._file = open(path, "w", encoding="utf-8")
    def write(self, text):
        sys.__stdout__.write(text)
        self._file.write(text)
    def flush(self):
        sys.__stdout__.flush()
        self._file.flush()
    def close(self):
        self._file.close()

tee = Tee(OUTPUT_FILE)
sys.stdout = tee

from ml_engine.health_score import compute_health_score
from ml_engine.cc import calculate_carbon_metrics

DIVIDER = "\n" + "="*60 + "\n"

# ══════════════════════════════════════════════════════════════
# 1. HEALTH SCORE SCENARIOS
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "1. COMPOSITE HEALTH SCORE SCENARIOS")
print(f"  Formula : H = 0.40*CNN + 0.35*NDVI_norm + 0.25*(1 - risk_prob)")
print(f"  Source  : ml_engine/health_score.py\n")

def get_rating(s):
    if s>=0.8: return "Excellent"
    elif s>=0.6: return "Good"
    elif s>=0.4: return "Fair"
    elif s>=0.2: return "Poor"
    else: return "Critical"

scenarios = [
    ("A — Healthy crop, good weather",     0.85, 0.72, 0.18),
    ("B — Early pest risk, moderate NDVI", 0.42, 0.54, 0.64),
    ("C — High risk, poor NDVI",           0.22, 0.31, 0.82),
    ("D — CNN unavailable (NDVI proxy)",   0.66, 0.66, 0.30),
]
print(f"  {'Scenario':<38} {'CNN':>5} {'NDVI':>5} {'Risk':>5} {'H(0-1)':>7} {'H%':>6}  Rating")
print("  " + "-"*75)
for label, cnn, ndvi, risk in scenarios:
    H = compute_health_score(p_cnn_healthy=cnn, ndvi_raw=ndvi, risk_prob=risk,
                              w1=0.4, w2=0.35, w3=0.25)
    print(f"  {label:<38} {cnn:>5.2f} {ndvi:>5.2f} {risk:>5.2f} {H:>7.4f} {H*100:>5.1f}%  {get_rating(H)}")

# ══════════════════════════════════════════════════════════════
# 2. CARBON CREDIT CALCULATION
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "2. AWD CARBON CREDIT ESTIMATION")
print("  Source  : ml_engine/cc.py + ml_engine/awd.py")
print("  Inputs  : area=0.5 ha, crop_days=90, 3 AWD cycles, $15/tonne\n")

cc = calculate_carbon_metrics(
    area_hectare=0.5,
    ndwi_series=[0.4, 0.1, 0.4, 0.1, 0.4, 0.1, 0.4],
    crop_days=90,
    credit_price_inr=15 * 83
)
for k, v in cc.items():
    if k == "awd_result":
        print(f"  awd_result:")
        for ak, av in v.items():
            print(f"    {ak}: {av}")
    else:
        print(f"  {k}: {v}")

# ══════════════════════════════════════════════════════════════
# 3. CNN MODEL — SPECS & INFERENCE LATENCY
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "3. CNN MODEL (MobileNetV2) — SPECS & INFERENCE LATENCY")

CNN_PATH = os.path.join(ML_DIR, "crop_health_model.pth")
if os.path.exists(CNN_PATH):
    print(f"  File     : {CNN_PATH}")
    print(f"  Size     : {os.path.getsize(CNN_PATH)/1024**2:.2f} MB")
    try:
        import torchvision.models as tv
        ckpt  = torch.load(CNN_PATH, map_location="cpu", weights_only=True)
        state = ckpt.get("state_dict", ckpt) if isinstance(ckpt, dict) else ckpt

        model = tv.mobilenet_v2(weights=None)
        model.classifier[1] = torch.nn.Linear(model.last_channel, 1)
        try:
            model.load_state_dict(state, strict=True)
            print("  Load     : strict=True OK")
        except RuntimeError:
            model.load_state_dict(state, strict=False)
            print("  Load     : strict=False (minor head mismatch)")

        model.eval()
        total = sum(p.numel() for p in model.parameters())
        print(f"  Params   : {total:,}")

        dummy = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            for _ in range(5): model(dummy)   # warmup
        lats = []
        with torch.no_grad():
            for _ in range(100):
                t0 = time.perf_counter(); model(dummy)
                lats.append((time.perf_counter()-t0)*1000)
        lats = np.array(lats)
        print(f"  Latency  : {lats.mean():.1f} ± {lats.std():.1f} ms  "
              f"(P50={np.percentile(lats,50):.1f} ms, P95={np.percentile(lats,95):.1f} ms)")
    except Exception as e:
        print(f"  ERROR    : {e}")
else:
    print(f"  NOT FOUND: {CNN_PATH}")

# ══════════════════════════════════════════════════════════════
# 4. LSTM MODEL — SPECS & INFERENCE LATENCY
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "4. LSTM MODEL — SPECS & INFERENCE LATENCY")

LSTM_PATH   = os.path.join(ML_DIR, "risk_lstm_final.pth")
SCALER_PATH = os.path.join(ML_DIR, "risk_scaler.save")

if os.path.exists(LSTM_PATH):
    print(f"  File     : {LSTM_PATH}")
    print(f"  Size     : {os.path.getsize(LSTM_PATH)/1024:.1f} KB")
    sd = torch.load(LSTM_PATH, map_location="cpu", weights_only=True)
    if isinstance(sd, dict) and "state_dict" in sd:
        meta = {k:v for k,v in sd.items() if k!="state_dict"}
        if meta: print(f"  Metadata : {meta}")
        sd = sd["state_dict"]

    print("  Layers   :")
    for k,v in sd.items():
        if isinstance(v, torch.Tensor):
            print(f"    {k:48s} {list(v.shape)}")

    hh0 = [k for k in sd if "weight_hh" in k and "l0" in k]
    ih0 = [k for k in sd if "weight_ih" in k and "l0" in k]
    if hh0 and ih0:
        hidden = sd[hh0[0]].shape[1]
        inp    = sd[ih0[0]].shape[1]
        layers = len([k for k in sd if "weight_hh" in k])
        total  = sum(v.numel() for v in sd.values() if isinstance(v, torch.Tensor))
        print(f"\n  Arch     : input_size={inp}, hidden_size={hidden}, num_layers={layers}")
        print(f"  Params   : {total:,}")

        class _LSTM(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.lstm=torch.nn.LSTM(inp,hidden,num_layers=layers,batch_first=True)
                self.fc=torch.nn.Linear(hidden,1)
            def forward(self,x):
                o,_=self.lstm(x); return self.fc(o[:,-1,:])*100
        m=_LSTM(); m.load_state_dict(sd,strict=False); m.eval()
        seq=torch.randn(1,14,inp)
        with torch.no_grad():
            for _ in range(10): m(seq)
        lats=[]
        with torch.no_grad():
            for _ in range(500):
                t0=time.perf_counter(); m(seq)
                lats.append((time.perf_counter()-t0)*1000)
        lats=np.array(lats)
        print(f"  Latency  : {lats.mean():.3f} ± {lats.std():.3f} ms  "
              f"(P50={np.percentile(lats,50):.3f} ms, P95={np.percentile(lats,95):.3f} ms)")
else:
    print(f"  NOT FOUND: {LSTM_PATH}")

if os.path.exists(SCALER_PATH):
    scaler = joblib.load(SCALER_PATH)
    print(f"\n  Scaler   : {type(scaler).__name__}")
    if hasattr(scaler,"mean_"):
        print(f"  Features : {len(scaler.mean_)}")
        print(f"  Means    : {np.round(scaler.mean_,4).tolist()}")
        print(f"  Stds     : {np.round(scaler.scale_,4).tolist()}")
else:
    print(f"  Scaler   : NOT FOUND — {SCALER_PATH}")

# ══════════════════════════════════════════════════════════════
# 5. API ENDPOINT AUDIT
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "5. API ENDPOINT AUDIT")
total_ep = 0
for dirpath, _, files in safe_walk(BACKEND):
    if "urls.py" in files:
        uf = os.path.join(dirpath, "urls.py")
        mod_eps = []
        with open(uf, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s.startswith("path(") or s.startswith("re_path("):
                    mod_eps.append(s)
                    total_ep += 1
        if mod_eps:
            print(f"\n  [{os.path.relpath(uf, BACKEND)}]")
            for ep in mod_eps:
                print(f"    {ep}")
print(f"\n  >>> TOTAL endpoints: {total_ep}")

# ══════════════════════════════════════════════════════════════
# 6. EARTH ENGINE — INDEX FORMULAS & ANOMALY THRESHOLDS
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "6. EARTH ENGINE — INDEX FORMULAS & THRESHOLDS")
KEYWORDS = ["ndvi","evi","savi","ndwi","anomaly","std","threshold","b8","b4","b3","b2","1.5"]
for dirpath, _, files in safe_walk(BACKEND):
    for fname in files:
        if not fname.endswith(".py"): continue
        fpath = os.path.join(dirpath, fname)
        with open(fpath, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        hits = [(i+1,l.rstrip()) for i,l in enumerate(lines)
                if any(kw.lower() in l.lower() for kw in KEYWORDS)]
        if hits:
            print(f"\n  {os.path.relpath(fpath, BACKEND)}")
            for lineno, text in hits[:15]:
                print(f"    {lineno:4d}: {text}")

# ══════════════════════════════════════════════════════════════
# 7. HEALTH SCORE SOURCE
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "7. HEALTH SCORE SOURCE (ml_engine/health_score.py)")
hs = os.path.join(ML_DIR, "health_score.py")
if os.path.exists(hs):
    with open(hs, encoding="utf-8") as f: print(f.read())
else:
    print("  NOT FOUND")

# ══════════════════════════════════════════════════════════════
# 8. CARBON CREDIT SOURCE
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "8. CARBON CREDIT SOURCE (ml_engine/cc.py)")
cc_src = os.path.join(ML_DIR, "cc.py")
if os.path.exists(cc_src):
    with open(cc_src, encoding="utf-8") as f: print(f.read())
else:
    print("  NOT FOUND")

# ══════════════════════════════════════════════════════════════
# 9. DEPLOYMENT CONFIG
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "9. DEPLOYMENT CONFIG (Docker / Prometheus)")
PROJ = os.path.dirname(BACKEND)
CONF = ["docker-compose.yml","docker-compose.yaml",
        "docker-compose.prod.yml","docker-compose.dev.yml",
        "prometheus.yml","prometheus.yaml"]
for dirpath, _, files in safe_walk(PROJ):
    for fname in files:
        if fname in CONF:
            fpath = os.path.join(dirpath, fname)
            print(f"\n  [{fname}] → {fpath}")
            with open(fpath, encoding="utf-8") as f: print(f.read())

# ══════════════════════════════════════════════════════════════
# 10. FRONTEND AUDIT
# ══════════════════════════════════════════════════════════════
print(DIVIDER + "10. FRONTEND AUDIT")
if os.path.exists(FRONTEND):
    tsx = [f for f in glob.glob(os.path.join(FRONTEND,"**","*.tsx"),recursive=True)
           if "node_modules" not in f]
    ts  = [f for f in glob.glob(os.path.join(FRONTEND,"**","*.ts"), recursive=True)
           if "node_modules" not in f]
    print(f"  .tsx: {len(tsx)}   .ts: {len(ts)}   Total: {len(tsx)+len(ts)}")

    for cand in ["pages","views","modules","dashboard","screens","components"]:
        d = os.path.join(FRONTEND,"src",cand)
        if not os.path.exists(d):
            d = os.path.join(FRONTEND,"client","src",cand)
        if os.path.exists(d):
            items = sorted(os.listdir(d))
            print(f"\n  /src/{cand}/ ({len(items)} items):")
            for item in items: print(f"    - {item}")

    for dirpath, _, files in os.walk(FRONTEND):
        if "node_modules" in dirpath: continue
        for fname in files:
            if fname in ["i18n.ts","i18n.js","translations.ts"]:
                fpath = os.path.join(dirpath, fname)
                print(f"\n  i18n file: {fpath}")
                with open(fpath, encoding="utf-8", errors="ignore") as f:
                    print(f.read()[:800])

    for dirpath, _, files in os.walk(FRONTEND):
        if "node_modules" in dirpath: continue
        for fname in files:
            if "voice" in fname.lower() or "speech" in fname.lower():
                fpath = os.path.join(dirpath, fname)
                print(f"\n  Voice hook: {fpath}")
                with open(fpath, encoding="utf-8", errors="ignore") as f:
                    print(f.read()[:600])
else:
    parent = os.path.dirname(BACKEND)
    print(f"  NOT FOUND. Sibling dirs: {os.listdir(parent)}")

print(DIVIDER + f"EXTRACTION COMPLETE\nSaved to: {OUTPUT_FILE}")

sys.stdout = sys.__stdout__
tee.close()
print(f"\n✅ Results saved to: {OUTPUT_FILE}")