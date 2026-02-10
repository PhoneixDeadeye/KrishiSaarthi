"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

interface MandiPrice {
    crop: string;
    min_price: number;
    max_price: number;
    modal_price: number;
    msp: number | null;
    vs_msp: number | null;
    trend: string;
    unit: string;
}

interface MandiData {
    mandi: string;
    prices: MandiPrice[];
    arrivals: number;
    last_updated: string;
}

interface PriceTrend {
    crop: string;
    data: { date: string; price: number; day: string }[];
    change_7d: number;
}

interface CropSummary {
    crop: string;
    modal_price: number;
    msp: number | null;
    trend: string;
    change: number;
}

interface MarketTip {
    type: string;
    icon: string;
    text: string;
}

interface MarketData {
    state: string;
    crop: string | null;
    date: string;
    mandi_prices: MandiData[];
    price_trends: PriceTrend;
    crops_summary: CropSummary[] | null;
    market_tips: MarketTip[];
}

const STATES = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Gujarat', 'Madhya Pradesh', 'Kerala'];
const CROPS = ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Soybean', 'Groundnut', 'Pulses', 'Potato', 'Onion', 'Tomato'];

export function MarketPrices() {
    const [data, setData] = useState<MarketData | null>(null);
    const [loading, setLoading] = useState(false);
    const [state, setState] = useState(() => localStorage.getItem('market_state') || 'Punjab');
    const [crop, setCrop] = useState<string>('');

    useEffect(() => {
        localStorage.setItem('market_state', state);
        fetchMarketData();
    }, [state, crop]);

    const fetchMarketData = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ state });
            if (crop && crop !== 'all') params.append('crop', crop);
            const result = await apiFetch(`/finance/market-prices?${params}`) as MarketData;
            setData(result);
        } catch (error) {
            console.error("Failed to fetch market data:", error);
        } finally {
            setLoading(false);
        }
    };

    const formatPrice = (price: number) => `₹${price.toLocaleString()}`;

    // Get top gainers and losers
    const topGainers = data?.crops_summary?.filter(c => c.change > 0).sort((a, b) => b.change - a.change).slice(0, 3) || [];
    const topLosers = data?.crops_summary?.filter(c => c.change < 0).sort((a, b) => a.change - b.change).slice(0, 3) || [];

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Market Prices</h1>
                    <p className="text-muted-foreground text-sm mt-1">Live commodity prices from agricultural mandis</p>
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                    <Select value={state} onValueChange={setState}>
                        <SelectTrigger className="w-[160px] bg-card">
                            <span className="material-symbols-outlined text-lg mr-2 text-muted-foreground">location_on</span>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {STATES.map(s => (
                                <SelectItem key={s} value={s}>{s}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Select value={crop} onValueChange={setCrop}>
                        <SelectTrigger className="w-[140px] bg-card">
                            <SelectValue placeholder="All Crops" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Crops</SelectItem>
                            {CROPS.map(c => (
                                <SelectItem key={c} value={c}>{c}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-muted-foreground text-xl">search</span>
                        <input
                            type="text"
                            placeholder="Search commodities..."
                            className="w-48 pl-10 pr-4 py-2 bg-card border rounded-lg text-sm focus:ring-2 focus:ring-primary/50"
                        />
                    </div>
                    <Button onClick={fetchMarketData} variant="outline" size="icon" disabled={loading} className="shrink-0">
                        <span className={cn("material-symbols-outlined", loading && "animate-spin")}>refresh</span>
                    </Button>
                </div>
            </div>

            {loading ? (
                <Card className="text-center">
                    <CardContent className="py-16 text-muted-foreground flex flex-col items-center">
                        <span className="material-symbols-outlined text-4xl animate-spin mb-2">progress_activity</span>
                        <p>Loading market data...</p>
                    </CardContent>
                </Card>
            ) : data ? (
                <>
                    {/* Top Gainers & Losers */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Top Gainers */}
                        <Card>
                            <CardContent className="p-5">
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="size-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                                        <span className="material-symbols-outlined text-lg">trending_up</span>
                                    </div>
                                    <h3 className="font-bold">Top Gainers</h3>
                                </div>
                                <div className="space-y-3">
                                    {topGainers.length > 0 ? topGainers.map((item, i) => (
                                        <div key={i} className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="size-10 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center text-yellow-600 dark:text-yellow-400">
                                                    <span className="material-symbols-outlined">nutrition</span>
                                                </div>
                                                <div>
                                                    <p className="font-medium text-sm">{item.crop}</p>
                                                    <p className="text-xs text-muted-foreground">{formatPrice(item.modal_price)}/qtl</p>
                                                </div>
                                            </div>
                                            <Badge className="bg-primary/20 text-primary font-bold">
                                                +{item.change}%
                                            </Badge>
                                        </div>
                                    )) : (
                                        <p className="text-sm text-muted-foreground">No gainers data</p>
                                    )}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Top Losers */}
                        <Card>
                            <CardContent className="p-5">
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="size-8 rounded-full bg-destructive/10 flex items-center justify-center text-destructive">
                                        <span className="material-symbols-outlined text-lg">trending_down</span>
                                    </div>
                                    <h3 className="font-bold">Top Losers</h3>
                                </div>
                                <div className="space-y-3">
                                    {topLosers.length > 0 ? topLosers.map((item, i) => (
                                        <div key={i} className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className="size-10 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400">
                                                    <span className="material-symbols-outlined">nutrition</span>
                                                </div>
                                                <div>
                                                    <p className="font-medium text-sm">{item.crop}</p>
                                                    <p className="text-xs text-muted-foreground">{formatPrice(item.modal_price)}/qtl</p>
                                                </div>
                                            </div>
                                            <Badge className="bg-destructive/20 text-destructive font-bold">
                                                {item.change}%
                                            </Badge>
                                        </div>
                                    )) : (
                                        <p className="text-sm text-muted-foreground">No losers data</p>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Main Price Table */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
                            <CardTitle className="text-lg">Commodity Prices</CardTitle>
                            <Badge variant="outline" className="text-xs">
                                Last updated: {data.date}
                            </Badge>
                        </CardHeader>

                        {/* Desktop Table */}
                        <div className="hidden md:block overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-muted text-xs uppercase text-muted-foreground font-semibold">
                                    <tr>
                                        <th className="px-5 py-4">Commodity</th>
                                        <th className="px-5 py-4">Market</th>
                                        <th className="px-5 py-4 text-right">Min Price</th>
                                        <th className="px-5 py-4 text-right">Max Price</th>
                                        <th className="px-5 py-4 text-right">Modal Price</th>
                                        <th className="px-5 py-4 text-center">24h Change</th>
                                        <th className="px-5 py-4">Trend</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border text-sm">
                                    {data.mandi_prices.flatMap(m =>
                                        m.prices.map((p, pIdx) => ({ ...p, mandi: m.mandi, arrivals: m.arrivals, id: `${m.mandi}-${p.crop}-${pIdx}` }))
                                    ).slice(0, 15).map((row) => (
                                        <tr key={row.id} className="hover:bg-muted/50 transition-colors">
                                            <td className="px-5 py-4 font-medium flex items-center gap-3">
                                                <div className="size-8 rounded-full bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center text-yellow-600 dark:text-yellow-400">
                                                    <span className="material-symbols-outlined text-lg">nutrition</span>
                                                </div>
                                                {row.crop}
                                            </td>
                                            <td className="px-5 py-4 text-muted-foreground">{row.mandi}</td>
                                            <td className="px-5 py-4 text-right font-mono text-muted-foreground">{formatPrice(row.min_price)}</td>
                                            <td className="px-5 py-4 text-right font-mono text-muted-foreground">{formatPrice(row.max_price)}</td>
                                            <td className="px-5 py-4 text-right font-mono font-bold">{formatPrice(row.modal_price)}</td>
                                            <td className="px-5 py-4 text-center">
                                                {row.vs_msp !== null ? (
                                                    <span className={cn(
                                                        "flex items-center justify-center gap-1 font-medium",
                                                        row.vs_msp >= 0 ? "text-primary" : "text-destructive"
                                                    )}>
                                                        <span className="material-symbols-outlined text-sm">
                                                            {row.vs_msp >= 0 ? "trending_up" : "trending_down"}
                                                        </span>
                                                        {row.vs_msp >= 0 ? '+' : ''}{row.vs_msp}%
                                                    </span>
                                                ) : (
                                                    <span className="text-muted-foreground">-</span>
                                                )}
                                            </td>
                                            <td className="px-5 py-4">
                                                <div className="w-20 h-6">
                                                    <svg
                                                        className={cn(
                                                            "w-full h-full fill-none stroke-2",
                                                            row.trend === 'up' ? "stroke-primary" : row.trend === 'down' ? "stroke-destructive" : "stroke-muted-foreground"
                                                        )}
                                                        viewBox="0 0 80 24"
                                                    >
                                                        <path d={row.trend === 'up'
                                                            ? "M0,20 Q10,22 20,16 T40,12 T60,8 T80,4"
                                                            : row.trend === 'down'
                                                                ? "M0,4 Q10,6 20,10 T40,14 T60,18 T80,20"
                                                                : "M0,12 Q20,12 40,12 T80,12"
                                                        }></path>
                                                    </svg>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Mobile Cards */}
                        <CardContent className="md:hidden p-4 space-y-3">
                            {data.mandi_prices.slice(0, 5).map((mandi, idx) => (
                                <div key={idx} className="p-4 rounded-lg bg-muted/50 space-y-3">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="material-symbols-outlined text-primary">location_on</span>
                                            <span className="font-semibold">{mandi.mandi}</span>
                                        </div>
                                        <span className="text-xs text-muted-foreground">{mandi.arrivals} qtl</span>
                                    </div>
                                    {mandi.prices.slice(0, 3).map((p, i) => (
                                        <div key={i} className="flex items-center justify-between py-2 border-t border-border">
                                            <span className="font-medium">{p.crop}</span>
                                            <div className="text-right">
                                                <span className="font-bold">{formatPrice(p.modal_price)}</span>
                                                {p.vs_msp !== null && (
                                                    <span className={cn(
                                                        "block text-xs font-medium",
                                                        p.vs_msp >= 0 ? "text-primary" : "text-destructive"
                                                    )}>
                                                        {p.vs_msp >= 0 ? '+' : ''}{p.vs_msp}%
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Market Tips */}
                    {data.market_tips.length > 0 && (
                        <Card>
                            <CardContent className="p-5">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="material-symbols-outlined text-primary">lightbulb</span>
                                    <h3 className="font-bold">Market Intelligence</h3>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    {data.market_tips.map((tip, idx) => (
                                        <div key={idx} className="p-4 rounded-lg bg-primary/5 border border-primary/20 flex items-start gap-3">
                                            <span className="text-2xl">{tip.icon}</span>
                                            <p className="text-sm">{tip.text}</p>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </>
            ) : (
                <Card className="text-center">
                    <CardContent className="py-16 text-muted-foreground flex flex-col items-center">
                        <span className="material-symbols-outlined text-4xl mb-2">error</span>
                        <p>Failed to load market data. Click refresh to try again.</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
