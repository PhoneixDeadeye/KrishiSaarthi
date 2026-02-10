"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useTranslation } from "@/hooks/useTranslation";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { Sprout, Plus, ArrowRight } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { HealthScoreResponse, PredictionData } from "@/types/field";
import { WeatherWidget } from "./WeatherWidget";
import { HealthGauge } from "./HealthGauge";

interface MarketData {
    crops_summary: {
        crop: string;
        modal_price: number;
        change: number;
        trend: string;
    }[] | null;
}

export function HomeDashboard({ onNavigate }: { onNavigate: (tab: string) => void }) {
    const { t } = useTranslation();
    const { user, token } = useAuth();
    const { selectedField, fields } = useField();

    const [weather, setWeather] = useState<any>(null);
    const [healthData, setHealthData] = useState<HealthScoreResponse | null>(null);
    const [marketPrices, setMarketPrices] = useState<any[]>([]);
    const [predictionData, setPredictionData] = useState<PredictionData | null>(null);

    // Fetch Weather
    useEffect(() => {
        const fetchWeather = async () => {
            if (!token) return;
            try {
                let coordEndpoint = '/field/coord';
                if (selectedField) coordEndpoint += `?field_id=${selectedField.id}`;
                const coordData = await apiFetch<any>(coordEndpoint);
                const coord = coordData?.coord || coordData?.location || null;
                let lon: number | undefined, lat: number | undefined;
                if (Array.isArray(coord)) { [lon, lat] = coord; }
                else if (coord && typeof coord === "object") { lon = coord.lon ?? coord.x; lat = coord.lat ?? coord.y; }

                if (lat === undefined || lon === undefined) {
                    setWeather({ temp: 24, condition: "Partly Cloudy", humidity: 65, wind: 12 });
                    return;
                }

                const weatherData = await apiFetch<any>(`/field/weather?lat=${lat}&lon=${lon}`);
                setWeather({
                    temp: Math.round(weatherData.current.main.temp),
                    condition: weatherData.current.weather[0].main,
                    humidity: weatherData.current.main.humidity,
                    wind: Math.round(weatherData.current.wind.speed * 3.6)
                });

            } catch (err) {
                console.error("Weather fetch error", err);
                setWeather({ temp: "--", condition: "Unavailable", humidity: 0, wind: 0 });
            }
        };
        fetchWeather();
    }, [selectedField, token]);

    // Fetch Health
    useEffect(() => {
        const fetchHealth = async () => {
            if (!token) return;
            try {
                let endpoint = '/field/healthscore';
                if (selectedField) endpoint += `?field_id=${selectedField.id}`;
                const data = await apiFetch<HealthScoreResponse>(endpoint);
                setHealthData(data);
            } catch (err) {
                console.error("Health fetch error", err);
                setHealthData(null);
            }
        };
        fetchHealth();
    }, [selectedField, token]);

    // Fetch Yield Prediction (NDVI)
    useEffect(() => {
        const fetchPrediction = async () => {
            if (!token || !selectedField) return;
            try {
                const data = await apiFetch<PredictionData>(`/field/yield-prediction?field_id=${selectedField.id}`);
                setPredictionData(data);
            } catch (err) {
                console.error("Prediction fetch error", err);
                setPredictionData(null);
            }
        };
        fetchPrediction();
    }, [selectedField, token]);


    // Fetch Market Prices
    useEffect(() => {
        const fetchMarket = async () => {
            try {
                const data = await apiFetch<MarketData>('/finance/market-prices?state=Punjab');
                if (data && data.crops_summary) {
                    const formatPrices = data.crops_summary.slice(0, 3).map(c => ({
                        commodity: c.crop,
                        price: c.modal_price,
                        change: `${c.change >= 0 ? '+' : ''}${c.change}%`
                    }));
                    setMarketPrices(formatPrices);
                }
            } catch (error) {
                console.error("Market fetch error", error);
            }
        };
        fetchMarket();
    }, []);

    if (!selectedField && fields.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 animate-in fade-in duration-500">
                <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center animate-bounce">
                    <Sprout className="w-10 h-10 text-primary" />
                </div>
                <div className="space-y-2 max-w-md">
                    <h1 className="text-3xl font-bold">Welcome to AgriSmart!</h1>
                    <p className="text-muted-foreground">
                        To get started, add your first field. We'll analyze satellite data to give you personalized insights.
                    </p>
                </div>
                <Button size="lg" onClick={() => onNavigate('my-field')}>
                    <Plus className="mr-2 h-5 w-5" /> Add Your First Field
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Top Grid: Weather & Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Weather Widget (Span 4) */}
                <div className="lg:col-span-4">
                    <WeatherWidget weather={weather} />
                </div>

                {/* Crop Status Cards (Span 8 -> 2x1 or 2x2 grid) */}
                <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <HealthGauge
                        score={healthData?.score_percent || 0}
                        rating={healthData?.rating || "Unknown"}
                        title={selectedField?.name || "Select Field"}
                    />
                    <HealthGauge
                        score={85}
                        rating="Good"
                        title="Winter Wheat"
                        accentColor="text-yellow-500"
                    />
                </div>
            </div>

            {/* Middle Section: Chart & Activity Feed */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Yield Prediction Chart (Span 8) */}
                <Card className="lg:col-span-8">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b">
                        <div className="space-y-1">
                            <CardTitle>Yield Prediction</CardTitle>
                            <CardDescription>Estimated output based on current conditions vs last year.</CardDescription>
                        </div>
                        <Button variant="outline" size="sm" className="h-8">
                            <span className="material-symbols-outlined text-sm mr-2">download</span> Export
                        </Button>
                    </CardHeader>
                    <CardContent className="p-6">
                        <div className="h-64 w-full">
                            {predictionData?.ndvi?.time_series ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={predictionData.ndvi.time_series}>
                                        <defs>
                                            <linearGradient id="colorNdvi" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                                                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.2} />
                                        <XAxis
                                            dataKey="date"
                                            tickFormatter={(date) => new Date(date).toLocaleDateString(undefined, { month: 'short' })}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'currentColor', fontSize: 12, opacity: 0.5 }}
                                        />
                                        <YAxis
                                            domain={[0, 1]}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'currentColor', fontSize: 12, opacity: 0.5 }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--background))', borderRadius: '8px', border: '1px solid hsl(var(--border))', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            labelFormatter={(date) => new Date(date).toLocaleDateString()}
                                            formatter={(value: number) => [value.toFixed(2), "NDVI"]}
                                        />
                                        <Area type="monotone" dataKey="ndvi" stroke="hsl(var(--primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorNdvi)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="flex h-full items-center justify-center text-muted-foreground bg-muted/50 rounded-lg border border-dashed">
                                    {selectedField ? "Loading chart..." : "Select a field to view growth trends."}
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Alerts Feed (Span 4) */}
                <Card className="lg:col-span-4 flex flex-col h-[450px]">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b">
                        <CardTitle className="text-lg">Recent Activity</CardTitle>
                        <Button variant="ghost" size="sm" className="text-primary hover:text-primary/90 p-0 h-auto">View All</Button>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto pt-4 pr-2">
                        <div className="space-y-4">
                            {predictionData?.recommendations?.length ? (
                                predictionData.recommendations.map((rec, i) => (
                                    <div key={i} className="flex gap-3 group">
                                        <div className="flex flex-col items-center">
                                            <div className="size-2 rounded-full bg-destructive mt-2 ring-4 ring-destructive/10"></div>
                                            <div className="w-0.5 h-full bg-border my-1 group-last:hidden"></div>
                                        </div>
                                        <div className="pb-4">
                                            <p className="text-sm font-semibold">Recommendation</p>
                                            <p className="text-xs text-muted-foreground mt-0.5">{rec.text}</p>
                                            <p className="text-[10px] text-muted-foreground mt-2">Just now</p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <>
                                    <div className="flex gap-3 group">
                                        <div className="flex flex-col items-center">
                                            <div className="size-2 rounded-full bg-destructive mt-2 ring-4 ring-destructive/10"></div>
                                            <div className="w-0.5 h-full bg-border my-1 group-last:hidden"></div>
                                        </div>
                                        <div className="pb-4">
                                            <p className="text-sm font-semibold">Severe Storm Alert</p>
                                            <p className="text-xs text-muted-foreground mt-0.5">High probability of hail in Sector 4. Cover sensitive equipment.</p>
                                            <p className="text-[10px] text-muted-foreground mt-2">2h ago</p>
                                        </div>
                                    </div>
                                    <div className="flex gap-3 group">
                                        <div className="flex flex-col items-center">
                                            <div className="size-2 rounded-full bg-yellow-500 mt-2 ring-4 ring-yellow-100 dark:ring-yellow-900/30"></div>
                                            <div className="w-0.5 h-full bg-border my-1 group-last:hidden"></div>
                                        </div>
                                        <div className="pb-4">
                                            <p className="text-sm font-semibold">Irrigation System Warning</p>
                                            <p className="text-xs text-muted-foreground mt-0.5">Pressure drop detected in Zone B pump.</p>
                                            <p className="text-[10px] text-muted-foreground mt-2">4h ago</p>
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Bottom Section: Market Prices Table */}
            <Card className="overflow-hidden">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
                    <CardTitle className="text-lg">Live Market Prices</CardTitle>
                    <Button
                        variant="ghost"
                        onClick={() => onNavigate('market')}
                        className="text-sm text-primary font-medium hover:underline flex items-center gap-1 p-0 h-auto hover:bg-transparent"
                    >
                        Full Report <ArrowRight className="size-4" />
                    </Button>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="px-6 py-4">Commodity</TableHead>
                                    <TableHead className="px-6 py-4">Price (per Quintal)</TableHead>
                                    <TableHead className="px-6 py-4">Change (24h)</TableHead>
                                    <TableHead className="px-6 py-4">Trend</TableHead>
                                    <TableHead className="px-6 py-4 text-right">Action</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {marketPrices.length > 0 ? (
                                    marketPrices.map((item, i) => (
                                        <TableRow key={i} className="hover:bg-muted/50 transition-colors">
                                            <TableCell className="px-6 py-4 font-medium flex items-center gap-3">
                                                <div className="size-8 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center text-yellow-600 dark:text-yellow-400">
                                                    <span className="material-symbols-outlined text-lg">nutrition</span>
                                                </div>
                                                {item.commodity}
                                            </TableCell>
                                            <TableCell className="px-6 py-4 text-muted-foreground font-mono">₹{item.price}</TableCell>
                                            <TableCell className={`px-6 py-4 font-medium`}>
                                                <div className={`flex items-center gap-1 ${item.change.includes('+') ? 'text-green-600' : 'text-red-600'}`}>
                                                    <span className="material-symbols-outlined text-sm">
                                                        {item.change.includes('+') ? 'trending_up' : 'trending_down'}
                                                    </span>
                                                    {item.change}
                                                </div>
                                            </TableCell>
                                            <TableCell className="px-6 py-4">
                                                <div className="w-24 h-8">
                                                    <svg className={`w-full h-full fill-none stroke-2 ${item.change.includes('+') ? 'stroke-green-600' : 'stroke-red-600'}`} viewBox="0 0 100 30">
                                                        <path d="M0,25 Q10,28 20,20 T40,15 T60,20 T80,10 T100,5"></path>
                                                    </svg>
                                                </div>
                                            </TableCell>
                                            <TableCell className="px-6 py-4 text-right">
                                                <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary transition-colors h-8 w-8">
                                                    <span className="material-symbols-outlined">more_vert</span>
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={5} className="text-center py-6 text-muted-foreground">Loading market prices...</TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>

            {/* Bottom Spacer */}
            <div className="h-8"></div>
        </div>
    );
}
