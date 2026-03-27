import { useState, useEffect, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";

interface MarketPriceCard {
    crop: string;
    msp: number | null;
    estimated_range: {
        low: number;
        high: number;
    };
    unit: string;
}

interface MarketTip {
    type: string;
    icon: string;
    text: string;
}

interface MarketData {
    state: string | null;
    date: string;
    data_source: string;
    is_live_data: boolean;
    disclaimer: string;
    prices: MarketPriceCard[];
    tips: MarketTip[];
}

const STATES = ["Punjab", "Haryana", "Uttar Pradesh", "Maharashtra", "Gujarat", "Madhya Pradesh", "Kerala"];
const CROPS = ["Rice", "Wheat", "Cotton", "Sugarcane", "Maize", "Soybean", "Groundnut", "Pulses", "Potato", "Onion", "Tomato"];

export function MarketPrices() {
    const [data, setData] = useState<MarketData | null>(null);
    const [loading, setLoading] = useState(false);
    const [state, setState] = useState(() => localStorage.getItem("market_state") || "Punjab");
    const [crop, setCrop] = useState<string>("");
    const [searchQuery, setSearchQuery] = useState("");

    const fetchMarketData = async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams({ state });
            if (crop && crop !== "all") params.append("crop", crop);
            const result = await apiFetch<MarketData>(`/finance/market-prices?${params.toString()}`);
            setData(result);
        } catch (error) {
            logger.error("Failed to fetch market data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        localStorage.setItem("market_state", state);
        fetchMarketData();
    }, [state, crop]);

    const q = searchQuery.toLowerCase().trim();
    const matchesSearch = (text: string) => !q || text.toLowerCase().includes(q);

    const rows = useMemo(() => {
        if (!data) return [];
        return data.prices
            .filter((p) => matchesSearch(p.crop))
            .map((p) => {
                const modal = Math.round((p.estimated_range.low + p.estimated_range.high) / 2);
                const vsMsp = p.msp ? Number((((modal - p.msp) / p.msp) * 100).toFixed(1)) : null;
                const trend = vsMsp === null ? "stable" : vsMsp >= 0 ? "up" : "down";
                return {
                    id: `${p.crop}-${p.unit}`,
                    crop: p.crop,
                    mandi: `${data.state || "India"} Reference`,
                    min_price: p.estimated_range.low,
                    max_price: p.estimated_range.high,
                    modal_price: modal,
                    vs_msp: vsMsp,
                    trend,
                };
            });
    }, [data, q]);

    const topGainers = rows.filter((r) => (r.vs_msp ?? 0) > 0).sort((a, b) => (b.vs_msp ?? 0) - (a.vs_msp ?? 0)).slice(0, 3);
    const topLosers = rows.filter((r) => (r.vs_msp ?? 0) < 0).sort((a, b) => (a.vs_msp ?? 0) - (b.vs_msp ?? 0)).slice(0, 3);

    const formatPrice = (price: number) => `₹${price.toLocaleString()}`;

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Market Prices</h1>
                    <p className="text-muted-foreground text-sm mt-1">MSP-based reference ranges for planning (not live mandi feed)</p>
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                    <Select value={state} onValueChange={setState}>
                        <SelectTrigger className="w-[160px] bg-card">
                            <span className="material-symbols-outlined text-lg mr-2 text-muted-foreground">location_on</span>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>{STATES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
                    </Select>

                    <Select value={crop} onValueChange={setCrop}>
                        <SelectTrigger className="w-[140px] bg-card"><SelectValue placeholder="All Crops" /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Crops</SelectItem>
                            {CROPS.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                        </SelectContent>
                    </Select>

                    <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-muted-foreground text-xl">search</span>
                        <input
                            type="text"
                            placeholder="Search commodities..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-48 pl-10 pr-4 py-2 bg-card border rounded-lg text-sm focus:ring-2 focus:ring-primary/50"
                        />
                    </div>

                    <Button onClick={fetchMarketData} variant="outline" size="icon" disabled={loading} className="shrink-0">
                        <span className={cn("material-symbols-outlined", loading && "animate-spin")}>refresh</span>
                    </Button>
                </div>
            </div>

            {loading ? (
                <Card className="text-center"><CardContent className="py-16 text-muted-foreground flex flex-col items-center"><span className="material-symbols-outlined text-4xl animate-spin mb-2">progress_activity</span><p>Loading market data...</p></CardContent></Card>
            ) : data ? (
                <>
                    <Card className="border-primary/20 bg-primary/5"><CardContent className="p-4 text-sm text-muted-foreground">{data.disclaimer}</CardContent></Card>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Card><CardContent className="p-5"><h3 className="font-bold mb-4">Top Above MSP</h3><div className="space-y-3">{topGainers.length ? topGainers.map((item) => (<div key={item.id} className="flex items-center justify-between"><p className="font-medium text-sm">{item.crop}</p><Badge className="bg-primary/20 text-primary font-bold">+{item.vs_msp}%</Badge></div>)) : <p className="text-sm text-muted-foreground">No crops currently above MSP</p>}</div></CardContent></Card>
                        <Card><CardContent className="p-5"><h3 className="font-bold mb-4">Top Below MSP</h3><div className="space-y-3">{topLosers.length ? topLosers.map((item) => (<div key={item.id} className="flex items-center justify-between"><p className="font-medium text-sm">{item.crop}</p><Badge className="bg-destructive/20 text-destructive font-bold">{item.vs_msp}%</Badge></div>)) : <p className="text-sm text-muted-foreground">No crops currently below MSP</p>}</div></CardContent></Card>
                    </div>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
                            <CardTitle className="text-lg">Commodity Price Ranges</CardTitle>
                            <Badge variant="outline" className="text-xs">Last updated: {data.date}</Badge>
                        </CardHeader>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-muted text-xs uppercase text-muted-foreground font-semibold">
                                    <tr>
                                        <th className="px-5 py-4">Commodity</th><th className="px-5 py-4">Reference Market</th><th className="px-5 py-4 text-right">Low</th><th className="px-5 py-4 text-right">High</th><th className="px-5 py-4 text-right">Estimated Modal</th><th className="px-5 py-4 text-center">vs MSP</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border text-sm">
                                    {rows.slice(0, 15).map((row) => (
                                        <tr key={row.id} className="hover:bg-muted/50 transition-colors">
                                            <td className="px-5 py-4 font-medium">{row.crop}</td>
                                            <td className="px-5 py-4 text-muted-foreground">{row.mandi}</td>
                                            <td className="px-5 py-4 text-right font-mono text-muted-foreground">{formatPrice(row.min_price)}</td>
                                            <td className="px-5 py-4 text-right font-mono text-muted-foreground">{formatPrice(row.max_price)}</td>
                                            <td className="px-5 py-4 text-right font-mono font-bold">{formatPrice(row.modal_price)}</td>
                                            <td className="px-5 py-4 text-center">{row.vs_msp !== null ? <span className={cn("font-medium", row.vs_msp >= 0 ? "text-primary" : "text-destructive")}>{row.vs_msp >= 0 ? "+" : ""}{row.vs_msp}%</span> : <span className="text-muted-foreground">N/A</span>}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>

                    {data.tips.length > 0 && (
                        <Card>
                            <CardContent className="p-5">
                                <div className="flex items-center gap-2 mb-4"><span className="material-symbols-outlined text-primary">lightbulb</span><h3 className="font-bold">Market Intelligence</h3></div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">{data.tips.map((tip, idx) => (<div key={idx} className="p-4 rounded-lg bg-primary/5 border border-primary/20 flex items-start gap-3"><span className="text-2xl">{tip.icon}</span><p className="text-sm">{tip.text}</p></div>))}</div>
                            </CardContent>
                        </Card>
                    )}
                </>
            ) : (
                <Card className="text-center"><CardContent className="py-16 text-muted-foreground flex flex-col items-center"><span className="material-symbols-outlined text-4xl mb-2">error</span><p>Failed to load market data. Click refresh to try again.</p></CardContent></Card>
            )}
        </div>
    );
}
