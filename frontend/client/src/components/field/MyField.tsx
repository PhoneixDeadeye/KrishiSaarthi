import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslation } from "@/hooks/useTranslation";
import MapView from "./MapView";

export function MyField() {
  const { t } = useTranslation();
  const [selectedCrop, setSelectedCrop] = useState("");
  const [selectedIrrigation, setSelectedIrrigation] = useState("");
  const [selectedSoil, setSelectedSoil] = useState("");

  const crops = [
    { value: "rice", label: "Rice / चावल / അരി" },
    { value: "coconut", label: "Coconut / नारियल / തേങ്ങ" },
    { value: "banana", label: "Banana / केला / വാഴപ്പഴം" },
    { value: "black_pepper", label: "Black Pepper / काली मिर्च / കുരുമുളക്" },
    { value: "cardamom", label: "Cardamom / इलायची / ഏലക്ക" },
    { value: "coffee", label: "Coffee / कॉफ़ी / കോഫി" },
    { value: "tea", label: "Tea / चाय / ചായ" },
    { value: "rubber", label: "Rubber / रबड़ / റബ്ബർ" },
    { value: "arecanut", label: "Arecanut / सुपारी / അടക്ക" },
    { value: "tapioca", label: "Tapioca / कसावा / കപ്പ" },
    { value: "ginger", label: "Ginger / अदरक / ഇഞ്ചി" },
    { value: "turmeric", label: "Turmeric / हल्दी / മഞ്ഞൾ" },
  ];

  const soilTypes = [
    { value: "loamy", label: "Loamy / दोमट / ലോമി" },
    { value: "clay", label: "Clay / मिट्टी / മണ്ണ്" },
    { value: "laterite", label: "Laterite / लेटराइट / ലാറ്ററൈറ്റ്" },
    { value: "sandy", label: "Sandy / रेतीला / മണൽ" },
    { value: "peaty", label: "Peaty / पीटी / പീറ്റി" },
  ];

  const irrigationTypes = [
    { value: "drip", label: "Drip / ड्रिप / ഡ്രിപ്പ്" },
    { value: "sprinkler", label: "Sprinkler / स्प्रिंकलर / സ്‌പ്രിങ്ക്ലർ" },
    { value: "flood", label: "Flood / बाढ़ / വെള്ളപ്പൊക്കം" },
    { value: "manual", label: "Manual / मैनुअल / മാനുവൽ" },
    { value: "basin", label: "Basin / बेसिन / ബേസിൻ" },
  ];

  return (
    <div className="relative h-[calc(100vh-4rem)] w-full overflow-hidden flex flex-col lg:flex-row">
      {/* Full Screen Map */}
      <div className="absolute inset-0 z-0">
        <MapView
          cropType={selectedCrop}
          soilType={selectedSoil}
          irrigationType={selectedIrrigation}
        />
      </div>

      {/* Floating Control Panel */}
      <div className="absolute right-0 top-0 bottom-0 pointer-events-none p-3 sm:p-4 z-10 w-full lg:w-[420px] flex flex-col justify-end lg:justify-start">
        <div className="pointer-events-auto bg-white/95 dark:bg-zinc-950/95 backdrop-blur-xl border border-border shadow-2xl rounded-2xl overflow-hidden max-h-[55vh] lg:max-h-[calc(100vh-6rem)] flex flex-col">
          {/* Panel Header */}
          <div className="p-5 pb-4 border-b border-border/40">
            <div className="flex items-center gap-3 mb-2">
              <div className="size-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary text-xl">landscape</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">{t("my_field")}</h1>
                <p className="text-xs text-muted-foreground">Configure field details</p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Draw your field boundary on the map to get started. Select your crop details below for accurate analysis.
            </p>
          </div>

          {/* Form Selectors */}
          <div className="p-5 space-y-4 overflow-y-auto flex-1">
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <span className="text-base">🌾</span>
                {t("crop_type")}
              </label>
              <Select value={selectedCrop} onValueChange={setSelectedCrop}>
                <SelectTrigger data-testid="select-crop-type" className="bg-white/50 dark:bg-zinc-900/50 border-border h-11">
                  <SelectValue placeholder={t("select_crop")} />
                </SelectTrigger>
                <SelectContent>
                  {crops.map((crop) => (
                    <SelectItem key={crop.value} value={crop.value}>{crop.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <span className="text-base">🪨</span>
                {t("soil_type")}
              </label>
              <Select value={selectedSoil} onValueChange={setSelectedSoil}>
                <SelectTrigger data-testid="select-soil-type" className="bg-white/50 dark:bg-zinc-900/50 border-border h-11">
                  <SelectValue placeholder={t("soil_placeholder")} />
                </SelectTrigger>
                <SelectContent>
                  {soilTypes.map((soil) => (
                    <SelectItem key={soil.value} value={soil.value}>{soil.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <span className="text-base">💧</span>
                {t("irrigation_type")}
              </label>
              <Select value={selectedIrrigation} onValueChange={setSelectedIrrigation}>
                <SelectTrigger data-testid="select-irrigation-type" className="bg-white/50 dark:bg-zinc-900/50 border-border h-11">
                  <SelectValue placeholder={t("irrigation_placeholder")} />
                </SelectTrigger>
                <SelectContent>
                  {irrigationTypes.map((item) => (
                    <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
