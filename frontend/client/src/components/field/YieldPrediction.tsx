
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { PredictionData } from "@/types/field";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell
} from "recharts";

export function YieldPrediction() {
    const { selectedField } = useField();
    const [prediction, setPrediction] = useState<PredictionData | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (selectedField) {
            fetchPrediction();
        }
    }, [selectedField]);

    const fetchPrediction = async () => {
        if (!selectedField) return;
        setLoading(true);
        try {
            const data = await apiFetch<PredictionData>(`/field/yield-prediction?field_id=${selectedField.id}`);
            setPrediction(data);
        } catch (error) {
            logger.error("Failed to fetch yield prediction:", error);
        } finally {
            setLoading(false);
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'increasing': return { icon: "trending_up", color: "text-primary" };
            case 'decreasing': return { icon: "trending_down", color: "text-red-500" };
            default: return { icon: "trending_flat", color: "text-muted-foreground" };
        }
    };

    const formatYield = (value: number) => {
        if (value >= 1000) return `${(value / 1000).toFixed(1)}t`;
        return `${value}kg`;
    };

    if (!selectedField) {
        return (
            <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center">
                    <span className="material-symbols-outlined text-3xl text-muted-foreground">target</span>
                </div>
                <div className="space-y-2">
                    <h3 className="text-lg font-semibold">No Field Selected</h3>
                    <p className="text-muted-foreground max-w-sm">Select a field from the sidebar to view its yield prediction and analysis.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        Yield Estimate
                    </h1>
                    <p className="text-muted-foreground">
                        AI-powered analysis for {selectedField.name}
                    </p>
                </div>
                <Button onClick={fetchPrediction} variant="outline" disabled={loading} className="gap-2">
                    <span className={cn("material-symbols-outlined text-lg", loading && "animate-spin")}>
                        {loading ? "progress_activity" : "refresh"}
                    </span>
                    {loading ? "Calculating..." : "Refresh Analysis"}
                </Button>
            </div>

            {loading ? (
                <div className="grid gap-6">
                    <div className="h-48 bg-muted animate-pulse rounded-lg" />
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map(i => (
                            <div key={i} className="h-32 bg-muted animate-pulse rounded-lg" />
                        ))}
                    </div>
                </div>
            ) : prediction ? (
                <>
                    {/* Main Prediction Card */}
                    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent overflow-hidden">
                        <CardContent className="p-6 sm:p-8">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
                                {/* Yield Prediction */}
                                <div className="text-center space-y-2">
                                    <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">Predicted Yield</p>
                                    <div className="flex flex-col items-center justify-center">
                                        <span className="text-5xl font-bold text-primary tracking-tight">
                                            {formatYield(prediction.prediction.yield_per_hectare)}
                                        </span>
                                        <span className="text-sm text-muted-foreground mt-1">per hectare</span>
                                    </div>
                                    <div className="pt-4 mt-4 border-t border-primary/10 w-3/4 mx-auto">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-muted-foreground">Total Output:</span>
                                            <span className="font-semibold">{formatYield(prediction.prediction.total_yield)}</span>
                                        </div>
                                        <div className="flex justify-between text-sm mt-1">
                                            <span className="text-muted-foreground">Field Area:</span>
                                            <span>{prediction.field_area_hectares} ha</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Confidence Gauge */}
                                <div className="text-center relative py-4 md:border-x border-border/50">
                                    <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-4">Confidence Score</p>
                                    <div className="relative size-32 mx-auto">
                                        <svg className="size-full transform -rotate-90">
                                            <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="10" fill="none" className="text-muted/20" />
                                            <circle
                                                cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="10" fill="none"
                                                className="text-primary transition-all duration-1000 ease-out"
                                                strokeDasharray={`${prediction.prediction.confidence * 3.51} 351`}
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                                            <span className="text-3xl font-bold">{prediction.prediction.confidence}%</span>
                                            <span className="text-xs text-muted-foreground">High</span>
                                        </div>
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-4">
                                        Range: {formatYield(prediction.prediction.range.low)} - {formatYield(prediction.prediction.range.high)}
                                    </p>
                                </div>

                                {/* vs Regional */}
                                <div className="text-center space-y-4">
                                    <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">Regional Comparison</p>
                                    <div>
                                        <div className="flex items-baseline justify-center gap-1">
                                            <span className={cn(
                                                "text-4xl font-bold",
                                                prediction.comparison.vs_regional >= 0 ? 'text-green-600 dark:text-green-500' : 'text-red-500'
                                            )}>
                                                {prediction.comparison.vs_regional >= 0 ? '+' : ''}{prediction.comparison.vs_regional}%
                                            </span>
                                            <span className="text-sm text-muted-foreground">vs avg</span>
                                        </div>
                                    </div>

                                    <div className="flex flex-col items-center gap-2">
                                        <div className="flex gap-1">
                                            {[...Array(5)].map((_, i) => (
                                                <span
                                                    key={i}
                                                    className={cn(
                                                        "material-symbols-outlined text-xl transition-all",
                                                        i < prediction.comparison.rating.stars ? 'text-yellow-400 fill-1' : 'text-muted/30'
                                                    )}
                                                    style={{ fontVariationSettings: i < prediction.comparison.rating.stars ? "'FILL' 1" : "'FILL' 0" }}
                                                >
                                                    star
                                                </span>
                                            ))}
                                        </div>
                                        <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                                            {prediction.comparison.rating.rating}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            {
                                label: "Current NDVI",
                                value: prediction.ndvi.current,
                                icon: "grass",
                                sub: prediction.ndvi.trend,
                                trend: getTrendIcon(prediction.ndvi.trend),
                                color: "text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30",
                            },
                            {
                                label: "Crop Health",
                                value: prediction.ndvi.status.status,
                                icon: prediction.ndvi.status.icon, // Emoji
                                isEmoji: true,
                                color: "text-blue-600 bg-blue-100 dark:bg-blue-900/30",
                            },
                            {
                                label: "Regional Avg",
                                value: formatYield(prediction.comparison.regional_average),
                                icon: "bar_chart",
                                sub: "per hectare",
                                color: "text-teal-600 bg-teal-100 dark:bg-teal-900/30",
                            },
                            {
                                label: "Crop Type",
                                value: prediction.crop_type,
                                icon: "eco",
                                color: "text-amber-600 bg-amber-100 dark:bg-amber-900/30",
                            },
                        ].map((stat, i) => (
                            <Card key={i}>
                                <CardContent className="p-4 flex flex-col justify-between h-full">
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-sm text-muted-foreground font-medium">{stat.label}</span>
                                        <div className={cn("size-8 rounded-md flex items-center justify-center", stat.color)}>
                                            {stat.isEmoji ? (
                                                <span className="text-lg">{stat.icon}</span>
                                            ) : (
                                                <span className="material-symbols-outlined text-lg">{stat.icon}</span>
                                            )}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-xl font-bold truncate">{stat.value}</div>
                                        {stat.sub && (
                                            <div className="flex items-center gap-1 mt-1">
                                                {stat.trend && (
                                                    <span className={cn("material-symbols-outlined text-base", stat.trend.color)}>
                                                        {stat.trend.icon}
                                                    </span>
                                                )}
                                                <span className="text-xs text-muted-foreground capitalize">{stat.sub}</span>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>

                    {/* Charts & Recommendations Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* NDVI Trend Chart */}
                        <Card className="lg:col-span-2">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="material-symbols-outlined text-primary">show_chart</span>
                                    NDVI Growth Trend
                                </CardTitle>
                                <CardDescription>Vegetation index over the last 12 weeks</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[300px] w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={prediction.ndvi.time_series} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.3} />
                                            <XAxis
                                                dataKey="date"
                                                tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                                                tickLine={false}
                                                axisLine={false}
                                                tickFormatter={(value, index) => index % 2 === 0 ? `W${index + 1}` : ''}
                                            />
                                            <YAxis
                                                domain={[0, 1]}
                                                tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                                                tickLine={false}
                                                axisLine={false}
                                            />
                                            <Tooltip
                                                cursor={{ fill: 'hsl(var(--muted)/0.2)' }}
                                                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                                                labelStyle={{ color: 'hsl(var(--foreground))' }}
                                            />
                                            <Bar dataKey="ndvi" radius={[4, 4, 0, 0]}>
                                                {prediction.ndvi.time_series.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={`hsl(var(--primary) / ${0.3 + (entry.ndvi * 0.7)})`} />
                                                ))}
                                            </Bar>
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Recommendations */}
                        <Card className="lg:col-span-1 flex flex-col">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <span className="material-symbols-outlined text-amber-500">lightbulb</span>
                                    AI Insights
                                </CardTitle>
                                <CardDescription>Actionable recommendations</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                                <div className="space-y-3">
                                    {prediction.recommendations.map((rec, idx) => (
                                        <div
                                            key={idx}
                                            className={cn(
                                                "p-3 rounded-lg border flex gap-3 transition-colors hover:shadow-sm",
                                                rec.type === 'warning' ? 'bg-amber-500/5 border-amber-500/20' :
                                                    rec.type === 'positive' ? 'bg-emerald-500/5 border-emerald-500/20' :
                                                        'bg-blue-500/5 border-blue-500/20'
                                            )}
                                        >
                                            <div className={cn(
                                                "size-8 rounded-full shrink-0 flex items-center justify-center",
                                                rec.type === 'warning' ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-400' :
                                                    rec.type === 'positive' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-400' :
                                                        'bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-400'
                                            )}>
                                                <span className="material-symbols-outlined text-lg text-center">
                                                    {rec.type === 'warning' ? 'warning' : rec.type === 'positive' ? 'check_circle' : 'info'}
                                                </span>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium leading-tight">{rec.text}</p>
                                                <p className="text-xs text-muted-foreground mt-1 capitalize">{rec.type} Priority</p>
                                            </div>
                                        </div>
                                    ))}
                                    {prediction.recommendations.length === 0 && (
                                        <div className="text-center py-8 text-muted-foreground">
                                            <span className="material-symbols-outlined text-3xl mb-2 opacity-50">check_circle</span>
                                            <p>No issues detected.</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </>
            ) : (
                <Card className="p-12 text-center text-muted-foreground border-dashed">
                    <div className="flex flex-col items-center">
                        <span className="material-symbols-outlined text-4xl mb-4 bg-muted/50 p-4 rounded-full">error_outline</span>
                        <h3 className="text-lg font-medium text-foreground">Analysis Unavailable</h3>
                        <p className="max-w-xs mx-auto mt-2 mb-4">We couldn't generate the yield prediction. Please check your internet connection or try again later.</p>
                        <Button onClick={fetchPrediction} variant="outline">Retry</Button>
                    </div>
                </Card>
            )}
        </div>
    );
}
