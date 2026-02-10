"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslation } from "@/hooks/useTranslation";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { EEData } from "./EEData";
import MapView from "./MapView";
import { apiFetch } from "@/lib/api";
import { HealthScoreResponse } from "@/types/field";
import { cn } from "@/lib/utils";

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

  const [weather, setWeather] = useState<any>(null);
  const [forecast, setForecast] = useState<any[]>([]);
  const [isLoadingWeather, setIsLoadingWeather] = useState(true);

  const [healthData, setHealthData] = useState<HealthScoreResponse | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(false);

  // Soil State
  type SoilInputs = { N: string; P: string; K: string; pH: string; };
  const [soilInputs, setSoilInputs] = useState<SoilInputs>({ N: "120", P: "45", K: "180", pH: "6.8" });
  const [soilSubmitted, setSoilSubmitted] = useState(true);

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

  // Fetch Health
  useEffect(() => {
    const fetchHealth = async () => {
      if (!token) return;
      setLoadingHealth(true);
      try {
        let endpoint = '/field/healthscore';
        if (selectedField) endpoint += `?field_id=${selectedField.id}`;
        const data = await apiFetch<HealthScoreResponse>(endpoint);
        setHealthData(data);
      } catch (err) { console.error(err); }
      finally { setLoadingHealth(false); }
    };
    fetchHealth();
  }, [token, selectedField]);

  // Fetch Weather
  useEffect(() => {
    const fetchWeather = async () => {
      if (!token) { setIsLoadingWeather(false); return; }
      try {
        let coordEndpoint = '/field/coord';
        if (selectedField) coordEndpoint += `?field_id=${selectedField.id}`;
        const coordData = await apiFetch<any>(coordEndpoint);
        const coord = coordData?.coord || coordData?.location || null;
        let lon: number | undefined, lat: number | undefined;
        if (Array.isArray(coord)) { [lon, lat] = coord; }
        else if (coord && typeof coord === "object") { lon = coord.lon ?? coord.x; lat = coord.lat ?? coord.y; }

        if (lat === undefined || lon === undefined) { setIsLoadingWeather(false); return; }

        const weatherData = await apiFetch<any>(`/field/weather?lat=${lat}&lon=${lon}`);
        setWeather(weatherData.current);
        setForecast(weatherData.forecast?.slice(0, 5) || []);
      } catch (err) { console.error(err); }
      finally { setIsLoadingWeather(false); }
    };
    fetchWeather();
  }, [token, selectedField]);

  const handlePDFDownload = () => { window.print(); };

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
          value={selectedField?.area ? `${selectedField.area} Ac` : "24.5 Ac"}
          icon="straighten"
        />
        <StatCard
          title="Crop Health"
          value={healthData ? `${healthData.score_percent}%` : "87%"}
          subtitle={healthData?.rating || "Good"}
          icon="monitoring"
          iconColor="text-primary"
        />
        <StatCard
          title="Active Alerts"
          value="2"
          subtitle="1 High Priority"
          icon="notifications_active"
          iconColor="text-amber-500"
        />
        <StatCard
          title="Days to Harvest"
          value="15"
          subtitle="Wheat (Rabi)"
          icon="calendar_today"
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
                        strokeDasharray={`${healthData?.score_percent || 87}, 100`}
                        strokeLinecap="round"
                        strokeWidth="3"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center flex-col">
                      <span className="text-2xl font-bold">{healthData?.score_percent || 87}%</span>
                      <span className="text-xs text-muted-foreground">Health</span>
                    </div>
                  </div>
                </div>

                {/* Insights */}
                <div className="md:col-span-2 space-y-3">
                  <div className="p-3 rounded-lg bg-primary/5 border border-primary/20">
                    <p className="text-sm font-medium text-primary">✓ Vegetation index is healthy</p>
                    <p className="text-xs text-muted-foreground mt-1">NDVI shows optimal growth patterns across field.</p>
                  </div>
                  <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
                    <p className="text-sm font-medium text-amber-700 dark:text-amber-400">⚠ Low moisture detected in Zone B</p>
                    <p className="text-xs text-muted-foreground mt-1">Consider irrigation within next 48 hours.</p>
                  </div>
                  {healthData?.recommendation && (
                    <p className="text-sm text-muted-foreground p-3 bg-muted rounded-lg">
                      {healthData.recommendation}
                    </p>
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
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm">Current Weather</p>
                  <p className="text-3xl font-bold mt-1">
                    {weather?.main?.temp ? `${Math.round(weather.main.temp)}°C` : "24°C"}
                  </p>
                </div>
                <span className="material-symbols-outlined text-5xl text-yellow-300">wb_sunny</span>
              </div>
              <div className="flex gap-4 mt-4 text-sm">
                <span className="flex items-center gap-1">
                  <span className="material-symbols-outlined text-base">water_drop</span>
                  {weather?.main?.humidity || 65}%
                </span>
                <span className="flex items-center gap-1">
                  <span className="material-symbols-outlined text-base">air</span>
                  {weather?.wind?.speed ? `${Math.round(weather.wind.speed * 3.6)} km/h` : "12 km/h"}
                </span>
              </div>
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
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Nitrogen (N)</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full" style={{ width: `${Math.min(+soilInputs.N / 2, 100)}%` }}></div>
                    </div>
                    <span className="text-sm font-medium w-12 text-right">{soilInputs.N}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Phosphorus (P)</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-orange-500 rounded-full" style={{ width: `${Math.min(+soilInputs.P, 100)}%` }}></div>
                    </div>
                    <span className="text-sm font-medium w-12 text-right">{soilInputs.P}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Potassium (K)</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-violet-500 rounded-full" style={{ width: `${Math.min(+soilInputs.K / 2, 100)}%` }}></div>
                    </div>
                    <span className="text-sm font-medium w-12 text-right">{soilInputs.K}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-2 border-t">
                  <span className="text-sm text-muted-foreground">pH Level</span>
                  <span className="text-sm font-bold text-primary">{soilInputs.pH}</span>
                </div>
              </div>
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
