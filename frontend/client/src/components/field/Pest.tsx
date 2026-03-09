
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiGet, apiPost, API_BASE_URL } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PestDetectionResult, PestReport, AgroAlert } from "@/types/field";
import { logger } from "@/lib/logger";

export function Pest() {
  const { token } = useAuth();
  const { selectedField } = useField();

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [detectionResult, setDetectionResult] = useState<PestDetectionResult | null>(null);
  const [pestPrediction, setPestPrediction] = useState<null | {
    risk_probability: number;
    risk_level: string;
  }>(null);
  const [predictionLoading, setPredictionLoading] = useState(true);
  const [pestHistory, setPestHistory] = useState<PestReport[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    const fetchPestPrediction = async () => {
      if (!token) { setPredictionLoading(false); return; }
      try {
        let url = '/field/pestpredict';
        if (selectedField) url += `?field_id=${selectedField.id}`;
        const pestData = await apiGet<{ risk_probability: number; risk_level: string }>(url);
        setPestPrediction(pestData);
      } catch (err) {
        logger.error("Pest prediction fetch error:", err);
      } finally {
        setPredictionLoading(false);
      }
    };
    fetchPestPrediction();
  }, [token, selectedField]);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!token) { setHistoryLoading(false); return; }
      try {
        const historyData = await apiGet<PestReport[]>('/field/pest/report');
        setPestHistory(historyData);
      } catch (err) {
        logger.error("History fetch error:", err);
      } finally {
        setHistoryLoading(false);
      }
    };
    fetchHistory();
  }, [token]);

  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const filesArray = Array.from(e.target.files);
    setSelectedFiles(filesArray);
    setPreviews(filesArray.map((file) => URL.createObjectURL(file)));
    setDetectionResult(null);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) { alert("Please select at least one file!"); return; }
    if (!token) { alert("Please log in to use pest detection"); return; }

    setUploading(true);
    setDetectionResult(null);

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("image", file));

    try {
      const data = await apiPost<PestDetectionResult>('/field/pest/report', formData);
      setDetectionResult(data);
      const historyData = await apiGet<PestReport[]>('/field/pest/report');
      setPestHistory(historyData);
    } catch (error: unknown) {
      const err = error as { message?: string; response?: { data?: { message?: string; detected?: string } } };
      const message = err.response?.data?.message || err.message || "Something went wrong";
      const detected = err.response?.data?.detected;
      setDetectionResult({
        error: message,
        detected: detected,
        class: "Error",
        confidence: 0
      });
    } finally {
      setUploading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "Low": return { bg: "bg-primary/10", text: "text-primary" };
      case "Medium": return { bg: "bg-amber-500/10", text: "text-amber-600" };
      case "High": return { bg: "bg-red-500/10", text: "text-red-600" };
      default: return { bg: "bg-muted", text: "text-muted-foreground" };
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <span className="material-symbols-outlined text-red-500">pest_control</span>
          Pest Detection
        </h1>
        <p className="text-muted-foreground text-sm mt-1">AI-powered pest detection and risk analysis</p>
      </div>

      {/* Detection + Prediction Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pest Detection */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-4 border-b">
            <span className="material-symbols-outlined text-primary">photo_camera</span>
            <CardTitle className="text-lg">Scan Crop</CardTitle>
          </CardHeader>
          <CardContent className="p-5">
            <div className="p-6 bg-primary/5 rounded-lg border border-dashed border-primary/20 text-center space-y-4">
              {/* Previews */}
              {previews.length > 0 && (
                <div className="flex flex-wrap gap-2 justify-center">
                  {previews.map((url, idx) => (
                    <img key={idx} src={url} alt={`Crop ${idx}`} className="size-20 object-cover rounded-lg border" />
                  ))}
                </div>
              )}

              {/* Upload Button */}
              <label className="cursor-pointer inline-flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors">
                <span className="material-symbols-outlined text-lg">add_photo_alternate</span>
                Select Photos
                <input type="file" accept="image/*" multiple onChange={handleFilesChange} className="hidden" />
              </label>

              {/* Scan Button */}
              <Button onClick={handleUpload} disabled={uploading || selectedFiles.length === 0} className="w-full gap-2">
                {uploading ? (
                  <span className="material-symbols-outlined text-lg animate-spin">progress_activity</span>
                ) : (
                  <span className="material-symbols-outlined text-lg">search</span>
                )}
                {uploading ? "Scanning..." : "Scan for Pests"}
              </Button>

              {/* Detection Result */}
              {detectionResult && (
                <div className={cn(
                  "p-4 rounded-lg text-left",
                  detectionResult.error ? "bg-red-500/10" :
                    detectionResult.class === "Healthy" ? "bg-primary/10" : "bg-amber-500/10"
                )}>
                  <p className="text-sm font-medium mb-1">Detection Result</p>
                  {detectionResult.error ? (
                    <div className="space-y-1">
                      <p className="text-sm text-red-600 font-medium">{detectionResult.error}</p>
                      {detectionResult.detected && (
                        <p className="text-xs text-muted-foreground">Detected: {detectionResult.detected}</p>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "material-symbols-outlined",
                        detectionResult.class === "Healthy" ? "text-primary" : "text-amber-600"
                      )}>
                        {detectionResult.class === "Healthy" ? "check_circle" : "warning"}
                      </span>
                      <span className={cn(
                        "font-bold",
                        detectionResult.class === "Healthy" ? "text-primary" : "text-amber-600"
                      )}>
                        {detectionResult.class}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Pest Prediction */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-4 border-b">
            <span className="material-symbols-outlined text-blue-500">analytics</span>
            <CardTitle className="text-lg">Pest Prediction</CardTitle>
          </CardHeader>
          <CardContent className="p-5">
            <div className="p-6 bg-blue-500/5 rounded-lg">
              {predictionLoading ? (
                <div className="flex justify-center items-center h-24">
                  <span className="material-symbols-outlined text-3xl animate-spin text-blue-500">progress_activity</span>
                </div>
              ) : pestPrediction ? (
                <div className="space-y-4">
                  {/* Risk Probability */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-muted-foreground">Risk Probability</span>
                      <span className="font-bold">{(pestPrediction.risk_probability * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-3 bg-muted rounded-full overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all duration-500",
                          pestPrediction.risk_level === "Low" ? "bg-primary" :
                            pestPrediction.risk_level === "Medium" ? "bg-amber-500" : "bg-red-500"
                        )}
                        style={{ width: `${pestPrediction.risk_probability * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Risk Level */}
                  <div className="flex items-center justify-between p-3 bg-card rounded-lg border">
                    <span className="text-sm font-medium">Risk Level</span>
                    <span className={cn(
                      "px-3 py-1 rounded-full text-xs font-bold",
                      getRiskColor(pestPrediction.risk_level).bg,
                      getRiskColor(pestPrediction.risk_level).text
                    )}>
                      {pestPrediction.risk_level}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground text-sm py-8">
                  <span className="material-symbols-outlined text-3xl mb-2">pin_drop</span>
                  <p>Save your field location in "My Field" to get pest predictions</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* History Section */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-4 border-b">
          <span className="material-symbols-outlined text-teal-500">history</span>
          <CardTitle className="text-lg">Recent Scans</CardTitle>
        </CardHeader>
        <CardContent className="p-5">
          {historyLoading ? (
            <div className="flex justify-center py-8">
              <span className="material-symbols-outlined text-3xl animate-spin text-teal-500">progress_activity</span>
            </div>
          ) : pestHistory.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
              {pestHistory.map((pest) => (
                <div key={pest.id} className="group relative rounded-lg overflow-hidden border hover:shadow-md transition-all">
                  <img
                    src={pest.image.startsWith('http') ? pest.image : `${API_BASE_URL}${pest.image}`}
                    alt="Scan"
                    className="w-full h-24 object-cover"
                  />
                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 backdrop-blur-sm p-1.5 text-[10px] text-white">
                    {new Date(pest.uploaded_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <span className="material-symbols-outlined text-3xl mb-2">photo_library</span>
              <p className="text-sm">No historical scans found</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
