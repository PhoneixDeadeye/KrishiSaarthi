import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslation } from "@/hooks/useTranslation";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { EEData } from "./EEData";
import MapView from "./MapView";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";
import { useWeather } from "@/hooks/useWeather";
import { useHealthScore } from "@/hooks/useHealthScore";
import { Loader2, AlertCircle } from "lucide-react";

// Stat Card Component
const StatCard = ({
  title,
  value,
  subtitle,
  icon,
  iconColor = "text-primary"
}: {
  title: string;
  value: string;
  subtitle?: string;
  icon: string;
  iconColor?: string;
}) => (
  <Card className="hover:shadow-md transition-shadow">
    <CardContent className="p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-bold mt-2 leading-tight">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground mt-2">{subtitle}</p>}
        </div>
        <div className={cn("size-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0", iconColor)}>
          <span className="material-symbols-outlined text-lg">{icon}</span>
        </div>
      </div>
    </CardContent>
  </Card>
);

export function FieldReport() {
  const { t } = useTranslation();
  const { token } = useAuth();
  const { selectedField } = useField();

  const { weather, forecast, isLoading: isLoadingWeather, error: weatherError } = useWeather();
  const { healthData, isLoading: loadingHealth, error: healthError } = useHealthScore();

  // Soil State
  type SoilInputs = { N: string; P: string; K: string; pH: string; };
  const [soilInputs, setSoilInputs] = useState<SoilInputs>({ N: "", P: "", K: "", pH: "" });
  const [soilSubmitted, setSoilSubmitted] = useState(false);

  type SoilAdviceData = {
    overall_status: string;
    recommendations: string[];
    fertilizer_suggestion: string | null;
    timing: string | null;
    caution: string | null;
  };
  const [aiSoilAdvice, setAiSoilAdvice] = useState<SoilAdviceData | null>(null);
  const [loadingSoilAdvice, setLoadingSoilAdvice] = useState(false);
  const [mapLayer, setMapLayer] = useState<'satellite' | 'ndvi'>('ndvi');

  const handleSoilSubmit = async () => {
    setSoilSubmitted(true);
    setLoadingSoilAdvice(true);
    try {
      const response = await apiFetch<{ advice: SoilAdviceData }>('/field/soil-advice', {
        method: 'POST',
        body: JSON.stringify({
          N: parseFloat(soilInputs.N) || 0,
          P: parseFloat(soilInputs.P) || 0,
          K: parseFloat(soilInputs.K) || 0,
          pH: parseFloat(soilInputs.pH) || 7.0,
        }),
      });
      setAiSoilAdvice(response.advice);
    } catch (err) {
      logger.error("Soil advice fetch error:", err);
    } finally {
      setLoadingSoilAdvice(false);
    }
  };

  // Weather and health data are now fetched via shared hooks above

  const handlePDFDownload = () => {
    // Use browser print dialog for PDF export
    window.print();
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Field Report</h1>
          <p className="text-muted-foreground text-sm mt-2">
            Comprehensive analysis for {selectedField ? selectedField.name : "All Fields"}
          </p>
        </div>
        <Button onClick={handlePDFDownload} className="gap-2 whitespace-nowrap">
          <span className="material-symbols-outlined text-lg">download</span>
          Export PDF
        </Button>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Area"
          value={selectedField?.area ? `${selectedField.area} Ac` : "--"}
          icon="straighten"
        />
        <StatCard
          title="Crop Health"
          value={healthData ? `${healthData.score_percent}%` : loadingHealth ? "..." : "--"}
          subtitle={healthData?.rating || undefined}
          icon="monitoring"
          iconColor="text-primary"
        />
        <StatCard
          title="Crop Type"
          value={selectedField?.cropType || "--"}
          icon="eco"
          iconColor="text-green-500"
        />
        <StatCard
          title="Field Name"
          value={selectedField?.name || "--"}
          icon="location_on"
          iconColor="text-blue-500"
        />
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column - Map & Analysis */}
        <div className="lg:col-span-8 space-y-8">
          {/* Field Map */}
          <Card className="h-96 overflow-hidden relative shadow-md hover:shadow-lg transition-shadow">
            <div className="absolute inset-0">
              <MapView readOnly={true} externalMapType={mapLayer} />
            </div>
            {/* Map Overlay Controls */}
            <div className="absolute top-4 left-4 z-10 flex gap-2">
              <button
                onClick={() => setMapLayer('satellite')}
                className={cn(
                  "px-4 py-2 rounded-lg text-xs font-bold border shadow-md transition-all hover:scale-105",
                  mapLayer === 'satellite'
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-white/95 dark:bg-zinc-900/95 border-white/20 hover:bg-white dark:hover:bg-zinc-800"
                )}
              >
                Satellite
              </button>
              <button
                onClick={() => setMapLayer('ndvi')}
                className={cn(
                  "px-4 py-2 rounded-lg text-xs font-bold border shadow-md transition-all hover:scale-105",
                  mapLayer === 'ndvi'
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "bg-white/95 dark:bg-zinc-900/95 border-white/20 hover:bg-white dark:hover:bg-zinc-800"
                )}
              >
                NDVI Layer
              </button>
            </div>
          </Card>

          {/* AI Analysis Card */}
          <Card>
            <CardContent className="p-8">
              <div className="flex items-center gap-3 mb-8">
                <div className="size-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                  <span className="material-symbols-outlined text-xl">psychology</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold">AI Crop Analysis</h3>
                  <p className="text-sm text-muted-foreground">Powered by satellite imagery & ML models</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Health Score */}
                <div className="flex flex-col items-center justify-center gap-4">
                  <div className="flex items-center justify-center">
                    <div className="relative size-36">
                      <svg className="size-full -rotate-90" viewBox="0 0 36 36">
                        <path
                          className="text-muted"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="3"
                        />
                        <path
                          className="text-primary"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                          fill="none"
                          stroke="currentColor"
                          strokeDasharray={`${healthData?.score_percent || 0}, 100`}
                          strokeLinecap="round"
                          strokeWidth="3"
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center flex-col">
                        <span className="text-3xl font-bold">{healthData?.score_percent || "--"}%</span>
                        <span className="text-xs text-muted-foreground font-medium">Health</span>
                      </div>
                    </div>
                  </div>
                  {/* Fallback Badges */}
                  {healthData?.breakdown?.cnn?.status === "estimated_from_ndvi" && (
                    <div className="text-[10px] flex items-center gap-1 bg-amber-500/10 text-amber-600 px-3 py-1.5 rounded-full border border-amber-500/20">
                      <AlertCircle className="size-3" />
                      <span>Estimated</span>
                    </div>
                  )}
                  {healthData?.breakdown?.cnn?.status === "unavailable" && (
                    <div className="text-[10px] flex items-center gap-1 bg-red-500/10 text-red-600 px-3 py-1.5 rounded-full border border-red-500/20">
                      <AlertCircle className="size-3" />
                      <span>Model Offline</span>
                    </div>
                  )}
                </div>

                {/* Insights */}
                <div className="md:col-span-2 space-y-4">
                  {healthData?.recommendation ? (
                    <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 space-y-2">
                      <p className="text-sm font-bold text-primary">✓ AI Analysis</p>
                      <p className="text-sm text-foreground leading-relaxed">{healthData.recommendation}</p>
                    </div>
                  ) : loadingHealth ? (
                    <div className="p-4 rounded-lg bg-muted/50 flex items-center gap-2 min-h-20 justify-center">
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Analyzing crop data...</span>
                    </div>
                  ) : (
                    <div className="p-4 rounded-lg bg-muted/50 flex items-center gap-2 min-h-20 justify-center">
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Loading crop analysis...</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Widgets */}
        <div className="lg:col-span-4 space-y-8">
          {/* Weather Card */}
          <Card className="overflow-hidden shadow-md hover:shadow-lg transition-shadow">
            <div className="p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              {isLoadingWeather ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span className="text-sm font-medium">Loading weather...</span>
                </div>
              ) : weather ? (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100 text-xs font-medium uppercase tracking-wide">Current Weather</p>
                      <p className="text-4xl font-bold mt-2 leading-tight">
                        {weather.temp}°C
                      </p>
                    </div>
                    <span className="material-symbols-outlined text-7xl text-yellow-300">wb_sunny</span>
                  </div>
                  <div className="flex gap-4 mt-6 text-sm">
                    <span className="flex items-center gap-2 bg-white/20 px-3 py-1.5 rounded-lg">
                      <span className="material-symbols-outlined text-base">water_drop</span>
                      <span className="font-medium">{weather.humidity}%</span>
                    </span>
                    <span className="flex items-center gap-2 bg-white/20 px-3 py-1.5 rounded-lg">
                      <span className="material-symbols-outlined text-base">air</span>
                      <span className="font-medium">{weather.wind} km/h</span>
                    </span>
                  </div>
                </>
              ) : (
                <div className="text-center py-3">
                  <p className="text-blue-100 text-sm">{weatherError || "Loading weather..."}</p>
                </div>
              )}
            </div>
            <CardContent className="p-6">
              <h4 className="text-xs font-bold uppercase tracking-wide text-muted-foreground mb-3">24-Hour Forecast</h4>
              <div className="space-y-1">
                {forecast.slice(0, 4).map((f, i) => (
                  <div key={i} className="flex justify-between items-center text-sm py-2.5 px-3 hover:bg-muted/30 rounded transition-colors">
                    <span className="text-muted-foreground font-medium">
                      {new Date(f.dt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <span className="font-bold text-primary">{Math.round(f.main.temp)}°C</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Soil Health Card */}
          <Card className="shadow-md hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                  <span className="material-symbols-outlined">science</span>
                </div>
                <h3 className="font-bold text-lg">Soil Nutrients</h3>
              </div>
              {soilSubmitted && (soilInputs.N || soilInputs.P || soilInputs.K || soilInputs.pH) ? (
                <div className="space-y-5">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">Nitrogen (N)</span>
                      <span className="text-sm font-bold text-primary">{soilInputs.N || "--"}</span>
                    </div>
                    <div className="w-full h-2.5 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${Math.min(+soilInputs.N / 2, 100)}%` }}></div>
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">Phosphorus (P)</span>
                      <span className="text-sm font-bold text-orange-500">{soilInputs.P || "--"}</span>
                    </div>
                    <div className="w-full h-2.5 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-orange-500 rounded-full transition-all" style={{ width: `${Math.min(+soilInputs.P, 100)}%` }}></div>
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">Potassium (K)</span>
                      <span className="text-sm font-bold text-teal-500">{soilInputs.K || "--"}</span>
                    </div>
                    <div className="w-full h-2.5 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-teal-500 rounded-full transition-all" style={{ width: `${Math.min(+soilInputs.K / 2, 100)}%` }}></div>
                    </div>
                  </div>
                  <div className="pt-4 border-t space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-foreground">pH Level</span>
                      <span className="text-sm font-bold text-primary bg-primary/10 px-3 py-1 rounded-lg">{soilInputs.pH || "--"}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-6 bg-muted/30 rounded-lg">Enter soil nutrient values below to see analysis.</p>
              )}
              {aiSoilAdvice?.overall_status && (
                <div className="mt-5 p-4 rounded-lg bg-primary/10 border border-primary/20 space-y-2">
                  <p className="text-xs font-bold text-primary uppercase tracking-wide">Recommendation</p>
                  <p className="text-sm text-foreground leading-relaxed">{aiSoilAdvice.overall_status}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* EE Data Stats */}
          <EEData />
        </div>
      </div>
    </div>
  );
}
