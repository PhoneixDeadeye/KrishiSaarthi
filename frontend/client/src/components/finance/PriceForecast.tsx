import { useState, useEffect, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus, LineChart, RefreshCw, AlertTriangle, Lightbulb, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface ForecastDay {
    date: string;
    day: number;
    predicted_price: number;
    lower_bound: number;
    upper_bound: number;
    confidence: number;
}

interface Recommendation {
    type: string;
    icon: string;
    text: string;
    action?: string;
}

interface ForecastData {
    crop: string;
    base_price: number;
    forecast_days: number;
    forecast: ForecastDay[];
    summary: {
        current_price: number;
        end_price: number;
        min_price: number;
        max_price: number;
        avg_price: number;
        trend: string;
        volatility: string;
        confidence: string;
    };
    recommendation: Recommendation[];
}

const CROPS = ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Soybean', 'Groundnut', 'Pulses', 'Potato', 'Onion', 'Tomato'];

export function PriceForecast() {
    const [crop, setCrop] = useState('Rice');
    const [days, setDays] = useState('30');
    const [data, setData] = useState<ForecastData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchForecast = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiFetch(`/finance/price-forecast?crop=${crop}&days=${days}`);
            setData(response as ForecastData);
        } catch (err) {
            setError('Failed to load price forecast');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchForecast();
    }, [crop, days]);

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'bullish': return <TrendingUp className="h-5 w-5 text-green-500" />;
            case 'bearish': return <TrendingDown className="h-5 w-5 text-red-500" />;
            default: return <Minus className="h-5 w-5 text-gray-500" />;
        }
    };

    const getTrendColor = (trend: string) => {
        switch (trend) {
            case 'bullish': return 'text-green-600 bg-green-50';
            case 'bearish': return 'text-red-600 bg-red-50';
            default: return 'text-gray-600 bg-gray-50';
        }
    };

    const getVolatilityColor = (volatility: string) => {
        switch (volatility) {
            case 'low': return 'bg-green-100 text-green-700';
            case 'medium': return 'bg-yellow-100 text-yellow-700';
            case 'high': return 'bg-red-100 text-red-700';
            default: return 'bg-gray-100 text-gray-700';
        }
    };

    // Calculate chart dimensions
    const chartData = useMemo(() => {
        if (!data?.forecast?.length) return null;

        const prices = data.forecast.map(d => d.predicted_price);
        const minPrice = Math.min(...prices) * 0.95;
        const maxPrice = Math.max(...prices) * 1.05;
        const range = maxPrice - minPrice;

        return {
            minPrice,
            maxPrice,
            range,
            points: data.forecast.map((day, i) => ({
                x: (i / (data.forecast.length - 1)) * 100,
                y: 100 - ((day.predicted_price - minPrice) / range) * 100,
                ...day
            }))
        };
    }, [data]);

    const formatPrice = (price: number) => `₹${price.toLocaleString('en-IN')}`;

    const priceChange = data ? data.summary.end_price - data.summary.current_price : 0;
    const priceChangePercent = data ? ((priceChange / data.summary.current_price) * 100).toFixed(1) : '0';

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <LineChart className="h-6 w-6 text-primary" />
                        Price Forecast
                    </h1>
                    <p className="text-muted-foreground">AI-powered crop price predictions for the next {days} days</p>
                </div>

                <div className="flex items-center gap-3">
                    <Select value={crop} onValueChange={setCrop}>
                        <SelectTrigger className="w-40">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {CROPS.map(c => (
                                <SelectItem key={c} value={c}>{c}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Select value={days} onValueChange={setDays}>
                        <SelectTrigger className="w-32">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="7">7 Days</SelectItem>
                            <SelectItem value="15">15 Days</SelectItem>
                            <SelectItem value="30">30 Days</SelectItem>
                            <SelectItem value="60">60 Days</SelectItem>
                        </SelectContent>
                    </Select>

                    <Button variant="outline" size="icon" onClick={fetchForecast} disabled={loading}>
                        <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    </Button>
                </div>
            </div>

            {error && (
                <Card className="border-red-200 bg-red-50">
                    <CardContent className="p-4 flex items-center gap-2 text-red-700">
                        <AlertTriangle className="h-5 w-5" />
                        {error}
                    </CardContent>
                </Card>
            )}

            {data && (
                <>
                    {/* Summary Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Card>
                            <CardContent className="p-4">
                                <div className="text-sm text-muted-foreground">Current Price</div>
                                <div className="text-2xl font-bold">{formatPrice(data.summary.current_price)}</div>
                                <div className="text-xs text-muted-foreground">per quintal</div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="p-4">
                                <div className="text-sm text-muted-foreground">Expected in {days}d</div>
                                <div className="text-2xl font-bold flex items-center gap-2">
                                    {formatPrice(data.summary.end_price)}
                                    {priceChange >= 0 ? (
                                        <ArrowUpRight className="h-4 w-4 text-green-500" />
                                    ) : (
                                        <ArrowDownRight className="h-4 w-4 text-red-500" />
                                    )}
                                </div>
                                <div className={`text-xs ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {priceChange >= 0 ? '+' : ''}{priceChangePercent}%
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="p-4">
                                <div className="text-sm text-muted-foreground">Price Range</div>
                                <div className="text-lg font-semibold">
                                    {formatPrice(data.summary.min_price)} - {formatPrice(data.summary.max_price)}
                                </div>
                                <div className="text-xs text-muted-foreground">predicted range</div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardContent className="p-4">
                                <div className="text-sm text-muted-foreground">Market Trend</div>
                                <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getTrendColor(data.summary.trend)}`}>
                                    {getTrendIcon(data.summary.trend)}
                                    {data.summary.trend.charAt(0).toUpperCase() + data.summary.trend.slice(1)}
                                </div>
                                <div className="mt-1">
                                    <Badge className={getVolatilityColor(data.summary.volatility)}>
                                        {data.summary.volatility} volatility
                                    </Badge>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Chart */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg">Price Trend Chart</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {chartData && (
                                <div className="relative h-64">
                                    {/* Y-axis labels */}
                                    <div className="absolute left-0 top-0 bottom-0 w-16 flex flex-col justify-between text-xs text-muted-foreground">
                                        <span>{formatPrice(Math.round(chartData.maxPrice))}</span>
                                        <span>{formatPrice(Math.round((chartData.maxPrice + chartData.minPrice) / 2))}</span>
                                        <span>{formatPrice(Math.round(chartData.minPrice))}</span>
                                    </div>

                                    {/* Chart area */}
                                    <div className="ml-16 h-full relative border-l border-b border-border">
                                        {/* Grid lines */}
                                        <div className="absolute inset-0">
                                            <div className="border-t border-dashed border-border" style={{ top: '50%', position: 'absolute', width: '100%' }} />
                                        </div>

                                        {/* Line chart using SVG */}
                                        <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                                            {/* Confidence band */}
                                            <path
                                                d={`
                          M ${chartData.points.map((p, i) => `${p.x},${100 - ((data.forecast[i].upper_bound - chartData.minPrice) / chartData.range) * 100}`).join(' L ')}
                          L ${[...chartData.points].reverse().map((p, i) => `${p.x},${100 - ((data.forecast[data.forecast.length - 1 - i].lower_bound - chartData.minPrice) / chartData.range) * 100}`).join(' L ')}
                          Z
                        `}
                                                fill="rgba(59, 130, 246, 0.1)"
                                            />

                                            {/* Price line */}
                                            <polyline
                                                points={chartData.points.map(p => `${p.x},${p.y}`).join(' ')}
                                                fill="none"
                                                stroke="rgb(59, 130, 246)"
                                                strokeWidth="2"
                                                vectorEffect="non-scaling-stroke"
                                            />
                                        </svg>

                                        {/* X-axis labels */}
                                        <div className="absolute -bottom-6 left-0 right-0 flex justify-between text-xs text-muted-foreground">
                                            <span>Today</span>
                                            <span>Day {Math.round(parseInt(days) / 2)}</span>
                                            <span>Day {days}</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Recommendations */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-lg flex items-center gap-2">
                                <Lightbulb className="h-5 w-5 text-yellow-500" />
                                AI Recommendations
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {data.recommendation.map((rec, index) => (
                                <div
                                    key={index}
                                    className={`flex items-start gap-3 p-3 rounded-lg ${rec.type === 'warning' ? 'bg-yellow-50' : 'bg-gray-50'
                                        }`}
                                >
                                    <span className="text-xl">{rec.icon}</span>
                                    <div>
                                        <p className="text-sm">{rec.text}</p>
                                        {rec.action && (
                                            <Badge variant="outline" className="mt-1">
                                                Recommended: {rec.action.toUpperCase()}
                                            </Badge>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    );
}
