// src/components/finance/PnLDashboard.tsx

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

type PnLData = {
    summary: {
        total_costs: number;
        total_revenue: number;
        profit_loss: number;
        profit_margin: number | null;
        is_profitable: boolean;
    };
    cost_breakdown: Array<{
        category: string;
        category_display: string;
        total: number;
        percentage: number;
    }>;
    revenue_by_crop: Array<{
        crop: string;
        total: number;
        quantity: number;
    }>;
};

// Stat Card Component
const StatCard = ({
    title,
    value,
    trend,
    icon,
    iconBg,
    iconColor,
    valueColor
}: {
    title: string;
    value: string;
    trend?: string;
    icon: string;
    iconBg: string;
    iconColor: string;
    valueColor?: string;
}) => (
    <Card>
        <CardContent className="p-5">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-muted-foreground">{title}</p>
                    <p className={cn("text-2xl font-bold mt-1", valueColor)}>{value}</p>
                    {trend && (
                        <p className="text-xs text-muted-foreground mt-1">{trend}</p>
                    )}
                </div>
                <div className={cn("size-12 rounded-xl flex items-center justify-center", iconBg)}>
                    <span className={cn("material-symbols-outlined text-xl", iconColor)}>{icon}</span>
                </div>
            </div>
        </CardContent>
    </Card>
);

export function PnLDashboard() {
    const { token } = useAuth();
    const { selectedField } = useField();

    const [data, setData] = useState<PnLData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPnL = async () => {
            if (!token || !selectedField) return;
            setLoading(true);
            try {
                const pnlData = await apiFetch<PnLData>(
                    `/finance/pnl?field_id=${selectedField.id}`
                );
                setData(pnlData);
            } catch (err) {
                console.error("Failed to fetch P&L data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPnL();
    }, [token, selectedField]);

    if (!selectedField) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-5xl text-muted-foreground mb-4">payments</span>
                    <p className="text-muted-foreground">Please select a field to view P&L dashboard.</p>
                </CardContent>
            </Card>
        );
    }

    if (loading) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-4xl animate-spin text-primary">progress_activity</span>
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 space-y-4 flex flex-col items-center">
                    <div className="size-16 rounded-full bg-muted flex items-center justify-center mx-auto">
                        <span className="material-symbols-outlined text-3xl text-muted-foreground">currency_rupee</span>
                    </div>
                    <div>
                        <h3 className="text-lg font-bold">No Financial Data Yet</h3>
                        <p className="text-muted-foreground text-sm mt-1 max-w-sm mx-auto">
                            Start tracking your farm's finances by adding cost entries or recording revenue.
                        </p>
                    </div>
                    <div className="flex gap-4 justify-center">
                        <Button variant="outline" className="gap-2">
                            <span className="material-symbols-outlined text-lg">receipt_long</span>
                            Track Costs
                        </Button>
                        <Button className="gap-2">
                            <span className="material-symbols-outlined text-lg">add</span>
                            Add Revenue
                        </Button>
                    </div>
                </CardContent>
            </Card>
        );
    }

    const { summary, cost_breakdown, revenue_by_crop } = data;
    const costColors = ["bg-red-500", "bg-orange-500", "bg-amber-500", "bg-yellow-500", "bg-lime-500", "bg-teal-500", "bg-cyan-500", "bg-teal-500"];

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Profit & Loss</h1>
                    <p className="text-muted-foreground text-sm mt-1">Financial overview for {selectedField.name}</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" className="gap-2" disabled>
                        <span className="material-symbols-outlined text-lg">download</span>
                        Export
                    </Button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Total Revenue"
                    value={`₹${summary.total_revenue.toLocaleString("en-IN")}`}
                    icon="trending_up"
                    iconBg="bg-primary/10"
                    iconColor="text-primary"
                    valueColor="text-primary"
                />
                <StatCard
                    title="Total Costs"
                    value={`₹${summary.total_costs.toLocaleString("en-IN")}`}
                    icon="trending_down"
                    iconBg="bg-destructive/10"
                    iconColor="text-destructive"
                    valueColor="text-destructive"
                />
                <StatCard
                    title="Net Profit/Loss"
                    value={`${summary.is_profitable ? "+" : ""}₹${summary.profit_loss.toLocaleString("en-IN")}`}
                    icon={summary.is_profitable ? "savings" : "money_off"}
                    iconBg={summary.is_profitable ? "bg-primary/10" : "bg-destructive/10"}
                    iconColor={summary.is_profitable ? "text-primary" : "text-destructive"}
                    valueColor={summary.is_profitable ? "text-primary" : "text-destructive"}
                />
                <StatCard
                    title="Profit Margin"
                    value={summary.profit_margin !== null ? `${summary.profit_margin.toFixed(1)}%` : "N/A"}
                    icon="pie_chart"
                    iconBg="bg-blue-500/10"
                    iconColor="text-blue-500"
                    valueColor={(summary.profit_margin ?? 0) >= 0 ? "text-primary" : "text-destructive"}
                />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Cost Breakdown */}
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="material-symbols-outlined text-primary">donut_large</span>
                            <h3 className="font-bold">Cost Breakdown</h3>
                        </div>
                        {cost_breakdown.length > 0 ? (
                            <div className="space-y-4">
                                {/* Simple donut visualization */}
                                <div className="flex justify-center mb-6">
                                    <div className="relative size-40">
                                        <svg className="size-full -rotate-90" viewBox="0 0 100 100">
                                            {cost_breakdown.reduce((acc, item, i) => {
                                                const prevOffset = acc.offset;
                                                const strokeDash = item.percentage;
                                                acc.elements.push(
                                                    <circle
                                                        key={item.category}
                                                        cx="50"
                                                        cy="50"
                                                        r="40"
                                                        fill="none"
                                                        strokeWidth="18"
                                                        stroke={`hsl(${(i * 40) + 0}, 70%, 50%)`}
                                                        strokeDasharray={`${strokeDash} ${100 - strokeDash}`}
                                                        strokeDashoffset={-prevOffset}
                                                    />
                                                );
                                                acc.offset += strokeDash;
                                                return acc;
                                            }, { elements: [] as JSX.Element[], offset: 0 }).elements}
                                        </svg>
                                        <div className="absolute inset-0 flex items-center justify-center flex-col">
                                            <span className="text-lg font-bold">₹{(summary.total_costs / 1000).toFixed(0)}K</span>
                                            <span className="text-xs text-muted-foreground">Total</span>
                                        </div>
                                    </div>
                                </div>
                                {/* Legend */}
                                {cost_breakdown.map((item, index) => (
                                    <div key={item.category} className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className={cn("size-3 rounded-full", costColors[index % costColors.length])} />
                                            <span className="text-sm">{item.category_display}</span>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-sm font-medium">₹{item.total.toLocaleString("en-IN")}</span>
                                            <span className="text-xs text-muted-foreground ml-2">({item.percentage.toFixed(1)}%)</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-muted-foreground text-center py-8">No cost data available.</p>
                        )}
                    </CardContent>
                </Card>

                {/* Revenue by Crop */}
                <Card>
                    <CardContent className="p-6">
                        <div className="flex items-center gap-2 mb-6">
                            <span className="material-symbols-outlined text-primary">bar_chart</span>
                            <h3 className="font-bold">Revenue by Crop</h3>
                        </div>
                        {revenue_by_crop.length > 0 ? (
                            <div className="space-y-4">
                                {revenue_by_crop.map((item) => {
                                    const maxRevenue = Math.max(...revenue_by_crop.map(r => r.total));
                                    const barWidth = (item.total / maxRevenue) * 100;
                                    return (
                                        <div key={item.crop} className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="font-medium">{item.crop}</span>
                                                <span className="text-primary font-bold">₹{item.total.toLocaleString("en-IN")}</span>
                                            </div>
                                            <div className="h-8 bg-muted rounded-lg overflow-hidden relative">
                                                <div
                                                    className="h-full bg-gradient-to-r from-primary to-primary/70 rounded-lg transition-all duration-500"
                                                    style={{ width: `${barWidth}%` }}
                                                />
                                                <span className="absolute inset-y-0 left-3 flex items-center text-xs text-white font-medium">
                                                    {item.quantity.toLocaleString("en-IN")} kg
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center py-8">
                                <span className="material-symbols-outlined text-4xl text-muted-foreground mb-2">receipt</span>
                                <p className="text-muted-foreground text-sm">No revenue recorded yet.</p>
                                <Button variant="outline" className="mt-4 gap-2">
                                    <span className="material-symbols-outlined text-lg">add</span>
                                    Add Revenue
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Monthly Trend */}
            <Card>
                <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <span className="material-symbols-outlined text-primary">trending_up</span>
                            <h3 className="font-bold">Monthly Trend</h3>
                        </div>
                        <div className="flex gap-4 text-sm">
                            <span className="flex items-center gap-2">
                                <div className="size-3 rounded-full bg-primary" />
                                Revenue
                            </span>
                            <span className="flex items-center gap-2">
                                <div className="size-3 rounded-full bg-destructive" />
                                Costs
                            </span>
                        </div>
                    </div>
                    <div className="flex flex-col items-center justify-center h-48 text-center">
                        <span className="material-symbols-outlined text-4xl text-muted-foreground mb-2">bar_chart</span>
                        <p className="text-muted-foreground text-sm">Monthly trend visualization requires more transaction history.</p>
                        <p className="text-muted-foreground text-xs mt-1">Continue logging income and expenses to see trends over time.</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
