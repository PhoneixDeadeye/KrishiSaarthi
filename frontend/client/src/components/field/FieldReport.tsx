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
  <Card>
    <CardContent className="p-5">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className={cn("size-10 rounded-lg bg-primary/10 flex items-center justify-center", iconColor)}>
          <span className="material-symbols-outlined">{icon}</span>
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
      console.error("Soil advice fetch error:", err);
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
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Field Report</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Comprehensive analysis for {selectedField ? selectedField.name : "All Fields"}
          </p>
        </div>
        <Button onClick={handlePDFDownload} className="gap-2">
          <span className="material-symbols-outlined text-lg">download</span>
          Export PDF
        </Button>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column - Map & Analysis */}
        <div className="lg:col-span-8 space-y-6">
          {/* Field Map */}
          <Card className="h-80 overflow-hidden relative">
            <div className="absolute inset-0">
              <MapView readOnly={true} />
            </div>
            {/* Map Overlay Controls */}
            <div className="absolute top-4 left-4 z-10 flex gap-2">
              <button className="px-3 py-1.5 bg-card/90 backdrop-blur-sm rounded-lg text-xs font-medium border shadow-sm hover:bg-card transition-colors">
                Satellite
              </button>
              <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-xs font-medium shadow-sm">
                NDVI Layer
              </button>
            </div>
          </Card>

          {/* AI Analysis Card */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined">psychology</span>
                </div>
                <div>
                  <h3 className="font-bold">AI Crop Analysis</h3>
                  <p className="text-sm text-muted-foreground">Powered by satellite imagery & ML models</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Health Score */}
                <div className="flex items-center justify-center">
                  <div className="relative size-32">
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
                      <span className="text-2xl font-bold">{healthData?.score_percent || "--"}%</span>
                      <span className="text-xs text-muted-foreground">Health</span>
                    </div>
                  </div>
                </div>

                {/* Insights */}
                <div className="md:col-span-2 space-y-3">
                  {healthData?.recommendation ? (
                    <div className="p-3 rounded-lg bg-primary/5 border border-primary/20">
                      <p className="text-sm font-medium text-primary">AI Analysis</p>
                      <p className="text-xs text-muted-foreground mt-1">{healthData.recommendation}</p>
                    </div>
                  ) : loadingHealth ? (
                    <div className="p-3 rounded-lg bg-muted flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm text-muted-foreground">Analyzing crop data...</span>
                    </div>
                  ) : (
                    <div className="p-3 rounded-lg bg-muted border border-dashed">
                      <p className="text-sm text-muted-foreground">Select a field to see AI-powered crop analysis.</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Widgets */}
        <div className="lg:col-span-4 space-y-6">
          {/* Weather Card */}
          <Card className="overflow-hidden">
            <div className="p-5 bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              {isLoadingWeather ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Loading weather...</span>
                </div>
              ) : weather ? (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100 text-sm">Current Weather</p>
                      <p className="text-3xl font-bold mt-1">
                        {weather.temp}°C
                      </p>
                    </div>
                    <span className="material-symbols-outlined text-5xl text-yellow-300">wb_sunny</span>
                  </div>
                  <div className="flex gap-4 mt-4 text-sm">
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-base">water_drop</span>
                      {weather.humidity}%
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-base">air</span>
                      {weather.wind} km/h
                    </span>
                  </div>
                </>
              ) : (
                <div className="text-center py-2">
                  <p className="text-blue-100 text-sm">{weatherError || "Weather data unavailable"}</p>
                  <p className="text-xs text-blue-200 mt-1">Save a field location to see weather</p>
                </div>
              )}
            </div>
            <CardContent className="p-4 space-y-2">
              {forecast.slice(0, 4).map((f, i) => (
                <div key={i} className="flex justify-between items-center text-sm py-2 border-b last:border-0">
                  <span className="text-muted-foreground">
                    {new Date(f.dt * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span className="font-medium">{Math.round(f.main.temp)}°C</span>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Soil Health Card */}
          <Card>
            <CardContent className="p-5">
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary">science</span>
                <h3 className="font-bold">Soil Nutrients</h3>
              </div>
              {soilSubmitted && (soilInputs.N || soilInputs.P || soilInputs.K || soilInputs.pH) ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Nitrogen (N)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${Math.min(+soilInputs.N / 2, 100)}%` }}></div>
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{soilInputs.N || "--"}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Phosphorus (P)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-orange-500 rounded-full" style={{ width: `${Math.min(+soilInputs.P, 100)}%` }}></div>
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{soilInputs.P || "--"}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Potassium (K)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-teal-500 rounded-full" style={{ width: `${Math.min(+soilInputs.K / 2, 100)}%` }}></div>
                      </div>
                      <span className="text-sm font-medium w-12 text-right">{soilInputs.K || "--"}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span className="text-sm text-muted-foreground">pH Level</span>
                    <span className="text-sm font-bold text-primary">{soilInputs.pH || "--"}</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">Enter soil nutrient values below to see analysis.</p>
              )}
              {aiSoilAdvice?.overall_status && (
                <div className="mt-4 p-3 rounded-lg bg-primary/10 text-sm">
                  {aiSoilAdvice.overall_status}
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
