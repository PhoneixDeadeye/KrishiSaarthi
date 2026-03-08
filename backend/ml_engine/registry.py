"""
ML Model Registry for KrishiSaarthi
=====================================
Provides centralized model versioning, metadata tracking, and health checks.
Ensures reproducibility and auditability of all ML model predictions.
"""
import os
import hashlib
import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(os.path.dirname(_MODULE_DIR), "ml_models")


@dataclass
class ModelMetadata:
    """Immutable metadata for a registered ML model."""
    name: str
    version: str
    architecture: str
    input_spec: str
    output_spec: str
    model_path: str
    file_hash: Optional[str] = None
    file_size_bytes: Optional[int] = None
    loaded_at: Optional[str] = None
    device: Optional[str] = None
    description: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """
    Singleton registry for all ML models used in the system.
    
    Provides:
    - Centralized model metadata and versioning
    - File integrity checks (SHA-256 hashes)
    - Model health status reporting
    - Lazy loading coordination
    
    Usage:
        from ml_engine.registry import registry
        
        # Check status of all models
        status = registry.status()
        
        # Get metadata for a specific model
        meta = registry.get("cnn_crop_health")
    """
    
    _instance: Optional["ModelRegistry"] = None
    
    def __new__(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._models: Dict[str, ModelMetadata] = {}
            cls._instance._loaders: Dict[str, Callable] = {}
            cls._instance._initialized = False
        return cls._instance
    
    def _ensure_initialized(self) -> None:
        """Register all known models on first access."""
        if self._initialized:
            return
        self._initialized = True
        
        # Register CNN model
        self._register_builtin(
            name="cnn_crop_health",
            version="2.0.0",
            architecture="MobileNetV2 (modified classifier → 1 output)",
            input_spec="RGB image 224x224, normalized ImageNet",
            output_spec="Sigmoid probability [0,1]: 1=Healthy, 0=Infested",
            model_path=os.path.join(_MODELS_DIR, "crop_health_model.pth"),
            description="Binary crop health classifier trained on pest/disease imagery.",
        )
        
        # Register LSTM model
        self._register_builtin(
            name="lstm_risk",
            version="2.0.0",
            architecture="LSTM(input=4, hidden=64, layers=2, dropout=0.1) → Linear(1) → Sigmoid",
            input_spec="Sequence of [NDVI, rainfall_mm, temp_C, soil_moisture], scaled",
            output_spec="Risk probability [0,1]: >0.7=High, 0.4-0.7=Medium, <0.4=Low",
            model_path=os.path.join(_MODELS_DIR, "risk_lstm_final.pth"),
            description="LSTM for crop pest/disease risk from NDVI and weather time series.",
            extra={"scaler_path": os.path.join(_MODELS_DIR, "risk_scaler.save")},
        )
        
        # Register scaler as a tracked artifact
        self._register_builtin(
            name="lstm_risk_scaler",
            version="2.0.0",
            architecture="sklearn.preprocessing.StandardScaler",
            input_spec="4-feature array [NDVI, rainfall, temp, humidity]",
            output_spec="Scaled 4-feature array",
            model_path=os.path.join(_MODELS_DIR, "risk_scaler.save"),
            description="Feature scaler for LSTM risk model inputs.",
        )
    
    def _register_builtin(self, name: str, version: str, architecture: str,
                          input_spec: str, output_spec: str, model_path: str,
                          description: str = "", extra: Optional[Dict] = None) -> None:
        """Register a built-in model with automatic file hash computation."""
        file_hash = None
        file_size = None
        
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path)
            # Only hash files under 500MB to avoid blocking startup
            if file_size < 500 * 1024 * 1024:
                file_hash = self._sha256(model_path)
        
        self._models[name] = ModelMetadata(
            name=name,
            version=version,
            architecture=architecture,
            input_spec=input_spec,
            output_spec=output_spec,
            model_path=model_path,
            file_hash=file_hash,
            file_size_bytes=file_size,
            description=description,
            extra=extra or {},
        )
    
    @staticmethod
    def _sha256(path: str) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    
    def get(self, name: str) -> Optional[ModelMetadata]:
        """Get metadata for a registered model."""
        self._ensure_initialized()
        return self._models.get(name)
    
    def list_models(self) -> Dict[str, ModelMetadata]:
        """Return all registered models."""
        self._ensure_initialized()
        return dict(self._models)
    
    def status(self) -> Dict[str, Any]:
        """
        Return health/status report for all registered models.
        
        Returns:
            Dict with model names as keys, each containing:
            - registered: True
            - file_exists: bool
            - file_hash: str or None
            - file_size_bytes: int or None
            - version: str
        """
        self._ensure_initialized()
        report: Dict[str, Any] = {}
        
        for name, meta in self._models.items():
            exists = os.path.exists(meta.model_path)
            report[name] = {
                "registered": True,
                "version": meta.version,
                "architecture": meta.architecture,
                "file_exists": exists,
                "file_hash": meta.file_hash,
                "file_size_bytes": meta.file_size_bytes,
                "model_path": meta.model_path,
            }
        
        return report
    
    def verify_integrity(self) -> Dict[str, bool]:
        """
        Verify file integrity of all registered models by re-computing hashes.
        
        Returns:
            Dict of {model_name: integrity_ok}
        """
        self._ensure_initialized()
        results: Dict[str, bool] = {}
        
        for name, meta in self._models.items():
            if not os.path.exists(meta.model_path):
                results[name] = False
                continue
            
            if meta.file_hash is None:
                # No hash recorded — can't verify, treat as OK
                results[name] = True
                continue
            
            current_hash = self._sha256(meta.model_path)
            results[name] = (current_hash == meta.file_hash)
            
            if not results[name]:
                logger.warning(
                    f"Model integrity check FAILED for {name}: "
                    f"expected {meta.file_hash[:16]}..., got {current_hash[:16]}..."
                )
        
        return results


# Singleton instance
registry = ModelRegistry()
