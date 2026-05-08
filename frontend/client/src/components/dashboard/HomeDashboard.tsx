import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useTranslation } from "@/hooks/useTranslation";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { Sprout, Plus, ArrowRight, AlertCircle, Loader2, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, type TooltipProps } from "recharts";
import { PredictionData } from "@/types/field";
import { logger } from "@/lib/logger";
import { WeatherWidget } from "./WeatherWidget";
import { HealthGauge } from "./HealthGauge";
import { useWeather } from "@/hooks/useWeather";
import { useHealthScore } from "@/hooks/useHealthScore";

/* ── Custom Tooltip ─────────────────────────────────────── */
function ChartTooltip({ active, payload, label }: TooltipProps<number, string>) {
    if (!active || !payload?.length) return null;
    const ndvi = payload[0]?.value ?? 0;
    const dateStr = label ? new Date(label).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }) : '';
    const quality = ndvi >= 0.6 ? 'Healthy' : ndvi >= 0.4 ? 'Moderate' : 'Stressed';
    const qualityColor = ndvi >= 0.6 ? '#34d399' : ndvi >= 0.4 ? '#fbbf24' : '#f87171';
    return (
        <div className="rounded-xl border border-border/60 bg-card/95 backdrop-blur-md shadow-xl px-4 py-3 min-w-[160px]">
            <p className="text-xs text-muted-foreground mb-1.5">{dateStr}</p>
            <div className="flex items-baseline gap-2">
                <span className="text-lg font-bold tabular-nums">{Number(ndvi).toFixed(3)}</span>
                <span className="text-xs text-muted-foreground">NDVI</span>
            </div>
            <div className="flex items-center gap-1.5 mt-1.5">
                <span className="size-2 rounded-full" style={{ backgroundColor: qualityColor }} />
                <span className="text-xs font-medium" style={{ color: qualityColor }}>{quality}</span>
            </div>
        </div>
    );
}

/* ── Active Dot (animated) ──────────────────────────────── */
function ActiveDot(props: any) {
    const { cx, cy } = props;
    return (
        <g>
            <circle cx={cx} cy={cy} r={8} fill="hsl(var(--primary))" opacity={0.15}>
                <animate attributeName="r" from="6" to="14" dur="1.2s" repeatCount="indefinite" />
                <animate attributeName="opacity" from="0.25" to="0" dur="1.2s" repeatCount="indefinite" />
            </circle>
            <circle cx={cx} cy={cy} r={5} fill="hsl(var(--primary))" stroke="hsl(var(--background))" strokeWidth={2.5} />
        </g>
    );
}

interface MarketData {
    prices: {
        crop: string;
        msp: number | null;
        estimated_range: { low: number; high: number };
        unit: string;
    }[] | null;
}

export function HomeDashboard({ onNavigate }: { onNavigate: (tab: string) => void }) {
    const { t } = useTranslation();
    const { user, token } = useAuth();
    const { selectedField, fields, loading: fieldsLoading } = useField();

    const { weather, isLoading: weatherLoading, error: weatherError } = useWeather();
    const { healthData, isLoading: healthLoading, error: healthError } = useHealthScore();

    const [marketPrices, setMarketPrices] = useState<any[]>([]);
    const [marketLoading, setMarketLoading] = useState(true);
    const [marketError, setMarketError] = useState<string | null>(null);
    const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
    const [predictionLoading, setPredictionLoading] = useState(true);

    // Fetch Yield Prediction (NDVI)
    useEffect(() => {
        const fetchPrediction = async () => {
            if (!token || !selectedField) {
                setPredictionLoading(false);
                return;
            }
            setPredictionLoading(true);
            try {
                const data = await apiFetch<PredictionData>(
                    `/field/yield-prediction?field_id=${selectedField.id}`,
                    {},
                    { timeout: 15000, retries: 1 }
                );
                setPredictionData(data);
            } catch (err) {
                logger.error("Prediction fetch error:", err);
                setPredictionData(null);
            } finally {
                setPredictionLoading(false);
            }
        };
        fetchPrediction();
    }, [selectedField, token]);


    // Fetch Market Prices
    useEffect(() => {
        const fetchMarket = async () => {
            setMarketLoading(true);
            setMarketError(null);
            try {
                const data = await apiFetch<MarketData>(
                    '/finance/market-prices?state=Punjab',
                    {},
                    { timeout: 10000, retries: 1 }
                );
                if (data && data.prices && data.prices.length > 0) {
                    const formatPrices = data.prices.slice(0, 3).map(c => {
                        const displayPrice = c.msp ? c.msp : Math.round((c.estimated_range.low + c.estimated_range.high) / 2);
                        return {
                            commodity: c.crop,
                            price: displayPrice,
                            // The backend doesn't provide change/trend, so we display standard indicators based on the range
                            change: "Stable"
                        };
                    });
                    setMarketPrices(formatPrices);
                } else {
                    setMarketPrices([]);
                }
            } catch (error) {
                logger.error("Market fetch error:", error);
                setMarketPrices([]);
            } finally {
                setMarketLoading(false);
            }
        };
        fetchMarket();
    }, []);

    // Still loading fields from backend
    if (fieldsLoading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh] animate-in fade-in duration-500">
                <div className="flex flex-col items-center gap-3">
                    <Loader2 className="h-10 w-10 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">Loading your farm data...</p>
                </div>
            </div>
        );
    }

    // Fields loaded but none exist — show onboarding prompt
    if (!selectedField && fields.length === 0) {
        return (
            <div className="flex items-center justify-center min-h-[60vh] animate-in fade-in duration-500">
                <div className="flex flex-col items-center gap-4 max-w-md text-center">
                    <div className="size-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                        <Sprout className="size-8 text-primary" />
                    </div>
                    <h2 className="text-xl font-semibold">Welcome to AgriSmart!</h2>
                    <p className="text-sm text-muted-foreground">
                        Get started by adding your first field. Draw your field boundary on the map and select your crop type for AI-powered analysis.
                    </p>
                    <Button
                        onClick={() => onNavigate('field')}
                        className="gap-2"
                    >
                        <Plus className="size-4" />
                        Add Your First Field
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Top Grid: Weather & Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Weather Widget (Span 4) */}
                <div className="lg:col-span-4">
                    <WeatherWidget weather={weather} isLoading={weatherLoading} error={weatherError} />
                </div>

                {/* Crop Health Card (Span 8) */}
                <div className="lg:col-span-8">
                    {healthLoading ? (
                        <Card className="h-full flex items-center justify-center">
                            <CardContent className="flex flex-col items-center gap-2 py-8">
                                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                                <p className="text-sm text-muted-foreground">Loading health data...</p>
                            </CardContent>
                        </Card>
                    ) : healthError ? (
                        <Card className="h-full flex items-center justify-center">
                            <CardContent className="flex flex-col items-center gap-2 py-8 text-muted-foreground">
                                <AlertCircle className="h-8 w-8" />
                                <p className="text-sm">{healthError}</p>
                            </CardContent>
                        </Card>
                    ) : healthData ? (
                        <HealthGauge
                            score={healthData.score_percent || 0}
                            rating={healthData.rating || "Unknown"}
                            title={selectedField?.name || "Select Field"}
                        />
                    ) : (
                        <Card className="h-full flex items-center justify-center">
                            <CardContent className="flex flex-col items-center gap-2 py-8">
                                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                                <p className="text-sm text-muted-foreground">Loading crop health...</p>
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>

            {/* Middle Section: Chart & Activity Feed */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Yield Prediction Chart (Span 8) */}
                <Card className="lg:col-span-8 overflow-hidden">
                    <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between space-y-3 sm:space-y-0 pb-2 border-b">
                        <div className="space-y-1">
                            <CardTitle className="flex items-center gap-2">
                                <span className="inline-flex items-center justify-center size-7 rounded-lg bg-emerald-500/10">
                                    <TrendingUp className="size-4 text-emerald-500" />
                                </span>
                                Yield Prediction
                            </CardTitle>
                            <CardDescription>NDVI vegetation index over time — higher values indicate healthier crops.</CardDescription>
                        </div>
                        {predictionData?.ndvi && (
                            <div className="flex items-center gap-2 flex-wrap">
                                {/* Current NDVI badge */}
                                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                    <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                    <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 tabular-nums">
                                        NDVI {predictionData.ndvi.current.toFixed(2)}
                                    </span>
                                </div>
                                {/* Trend badge */}
                                <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${
                                    predictionData.ndvi.trend === 'increasing'
                                        ? 'bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400'
                                        : predictionData.ndvi.trend === 'decreasing'
                                          ? 'bg-red-500/10 border-red-500/20 text-red-500 dark:text-red-400'
                                          : 'bg-muted border-border text-muted-foreground'
                                }`}>
                                    {predictionData.ndvi.trend === 'increasing' ? (
                                        <TrendingUp className="size-3" />
                                    ) : predictionData.ndvi.trend === 'decreasing' ? (
                                        <TrendingDown className="size-3" />
                                    ) : (
                                        <Minus className="size-3" />
                                    )}
                                    <span className="capitalize">{predictionData.ndvi.trend}</span>
                                </div>
                                {/* Crop type badge */}
                                {predictionData.crop_type && (
                                    <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs font-medium text-amber-600 dark:text-amber-400">
                                        <Sprout className="size-3" />
                                        {predictionData.crop_type}
                                    </div>
                                )}
                            </div>
                        )}
                    </CardHeader>
                    <CardContent className="p-4 sm:p-6">
                        <div className="h-72 w-full">
                            {predictionData?.ndvi?.time_series ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={predictionData.ndvi.time_series} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="#34d399" stopOpacity={0.45} />
                                                <stop offset="50%" stopColor="#2dd4bf" stopOpacity={0.15} />
                                                <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0.02} />
                                            </linearGradient>
                                            <linearGradient id="ndviStroke" x1="0" y1="0" x2="1" y2="0">
                                                <stop offset="0%" stopColor="#34d399" />
                                                <stop offset="100%" stopColor="#2dd4bf" />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.08} />
                                        <XAxis
                                            dataKey="date"
                                            tickFormatter={(date) => {
                                                const d = new Date(date);
                                                return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
                                            }}
                                            interval={Math.max(0, Math.floor((predictionData.ndvi.time_series.length - 1) / 8))}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
                                            dy={8}
                                        />
                                        <YAxis
                                            domain={[0, 1]}
                                            ticks={[0, 0.25, 0.5, 0.75, 1]}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
                                            tickFormatter={(v) => v.toFixed(2)}
                                            dx={-4}
                                        />
                                        <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'var(--muted-foreground)', strokeWidth: 1, strokeDasharray: '4 4' }} />
                                        <Area
                                            type="monotone"
                                            dataKey="ndvi"
                                            stroke="url(#ndviStroke)"
                                            strokeWidth={2.5}
                                            fill="url(#ndviGradient)"
                                            fillOpacity={1}
                                            activeDot={<ActiveDot />}
                                            dot={false}
                                            animationDuration={1500}
                                            animationEasing="ease-in-out"
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : predictionLoading ? (
                                <div className="flex h-full items-center justify-center text-muted-foreground bg-muted/30 rounded-xl border border-dashed border-border/60">
                                    <div className="text-center space-y-2">
                                        <Loader2 className="size-8 mx-auto animate-spin opacity-40" />
                                        <p className="text-sm">Loading vegetation data...</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex h-full items-center justify-center text-muted-foreground bg-muted/30 rounded-xl border border-dashed border-border/60">
                                    <div className="text-center space-y-3">
                                        <Sprout className="size-8 mx-auto opacity-40" />
                                        <p className="text-sm">No vegetation data available yet.</p>
                                        <p className="text-xs opacity-60">Satellite data may take a few minutes to process after adding a field.</p>
                                    </div>
                                </div>
                            )}
                        </div>
                        {/* Legend */}
                        {predictionData?.ndvi?.time_series && (
                            <div className="flex items-center justify-center gap-6 mt-4 pt-3 border-t border-border/40">
                                <div className="flex items-center gap-2">
                                    <span className="inline-block w-5 h-[3px] rounded-full bg-gradient-to-r from-emerald-400 to-teal-400" />
                                    <span className="text-xs text-muted-foreground">NDVI Index</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="size-2 rounded-full bg-emerald-400" />
                                    <span className="text-xs text-muted-foreground">Healthy (≥0.6)</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="size-2 rounded-full bg-amber-400" />
                                    <span className="text-xs text-muted-foreground">Moderate</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className="size-2 rounded-full bg-red-400" />
                                    <span className="text-xs text-muted-foreground">Stressed</span>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Alerts Feed (Span 4) */}
                <Card className="lg:col-span-4 flex flex-col h-[450px]">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b">
                        <CardTitle className="text-lg">Recommendations</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto pt-4 pr-2">
                        <div className="space-y-4">
                            {predictionData?.recommendations?.length ? (
                                predictionData.recommendations.map((rec, i) => (
                                    <div key={i} className="flex gap-3 group">
                                        <div className="flex flex-col items-center">
                                            <div className="size-2 rounded-full bg-primary mt-2 ring-4 ring-primary/10"></div>
                                            <div className="w-0.5 h-full bg-border my-1 group-last:hidden"></div>
                                        </div>
                                        <div className="pb-4">
                                            <p className="text-sm font-semibold">Recommendation</p>
                                            <p className="text-xs text-muted-foreground mt-0.5">{rec.text}</p>
                                        </div>
                                    </div>
                                ))
                            ) : predictionLoading ? (
                                <div className="flex flex-col items-center justify-center h-full text-muted-foreground py-8">
                                    <Loader2 className="h-8 w-8 mb-2 animate-spin" />
                                    <p className="text-sm text-center">Analyzing your field data...</p>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-full text-muted-foreground py-8">
                                    <Sprout className="h-8 w-8 mb-2 opacity-40" />
                                    <p className="text-sm text-center">Recommendations will appear once satellite data is processed.</p>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Bottom Section: Market Prices Table */}
            <Card className="overflow-hidden">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
                    <div>
                        <CardTitle className="text-lg">Reference Market Prices</CardTitle>
                        <CardDescription className="text-xs mt-1">MSP & indicative prices. Not real-time data.</CardDescription>
                    </div>
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
                                    <TableHead className="px-6 py-4">Change</TableHead>
                                    <TableHead className="px-6 py-4">Trend</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {marketLoading ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center py-6">
                                            <div className="flex items-center justify-center gap-2 text-muted-foreground">
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Loading market prices...
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : marketError ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                                            {marketError}
                                        </TableCell>
                                    </TableRow>
                                ) : marketPrices.length > 0 ? (
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
                                                <div className={`flex items-center gap-1 text-muted-foreground`}>
                                                    <span className="material-symbols-outlined text-sm">
                                                        horizontal_rule
                                                    </span>
                                                    {item.change}
                                                </div>
                                            </TableCell>
                                            <TableCell className="px-6 py-4">
                                                <div className={`flex items-center gap-1 text-sm font-medium text-muted-foreground`}>
                                                    <span className="material-symbols-outlined text-lg">
                                                        horizontal_rule
                                                    </span>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center py-6 text-muted-foreground">
                                            No market price data available.
                                        </TableCell>
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
