// src/components/finance/CostCalculator.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import {
    Plus,
    Trash2,
    Loader2,
    IndianRupee,
    Wheat,
    FlaskConical,
    Bug,
    Users,
    Droplets,
    Tractor,
    Truck,
    MoreHorizontal,
    TrendingUp,
    TrendingDown,
    ArrowUpRight,
    ArrowDownRight,
} from "lucide-react";

const COST_CATEGORIES = [
    { value: "seeds", label: "Seeds", icon: Wheat },
    { value: "fertilizer", label: "Fertilizer", icon: FlaskConical },
    { value: "pesticide", label: "Pesticide", icon: Bug },
    { value: "labor", label: "Labor", icon: Users },
    { value: "irrigation", label: "Irrigation", icon: Droplets },
    { value: "equipment", label: "Equipment Rental", icon: Tractor },
    { value: "transport", label: "Transport", icon: Truck },
    { value: "other", label: "Other", icon: MoreHorizontal },
];

type CostEntry = {
    id: number;
    category: string;
    category_display: string;
    description: string;
    amount: number;
    quantity: number | null;
    unit: string;
    date: string;
};

type RevenueEntry = {
    id: number;
    crop: string;
    quantity_sold: number;
    unit: string;
    price_per_unit: number;
    total_amount: number;
    buyer: string;
    date: string;
    notes: string;
};

type Season = {
    id: number;
    name: string;
    season_type: string;
    year: number;
    start_date: string;
    end_date: string;
    crop: string;
    is_active: boolean;
    total_costs: number;
    total_revenue: number;
    profit_loss: number;
};

type CostSummary = {
    breakdown: Array<{
        category: string;
        category_display: string;
        total: number;
        count: number;
    }>;
    total: number;
};

export function CostCalculator() {
    const { token } = useAuth();
    const { selectedField } = useField();

    const [activeTab, setActiveTab] = useState("costs");
    const [costs, setCosts] = useState<CostEntry[]>([]);
    const [revenues, setRevenues] = useState<RevenueEntry[]>([]);
    const [seasons, setSeasons] = useState<Season[]>([]);
    const [selectedSeason, setSelectedSeason] = useState<string>("all");
    const [summary, setSummary] = useState<CostSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    // Cost form state
    const [costForm, setCostForm] = useState({
        category: "",
        description: "",
        amount: "",
        quantity: "",
        unit: "",
        date: new Date().toISOString().split("T")[0],
    });

    // Revenue form state
    const [revenueForm, setRevenueForm] = useState({
        crop: "",
        quantity_sold: "",
        unit: "kg",
        price_per_unit: "",
        buyer: "",
        date: new Date().toISOString().split("T")[0],
        notes: "",
    });

    const fetchData = async () => {
        if (!token || !selectedField) return;
        setLoading(true);
        try {
            const seasonParam = selectedSeason !== "all" ? `&season_id=${selectedSeason}` : "";

            const [costsData, summaryData, revenuesData, seasonsData] = await Promise.all([
                apiFetch<CostEntry[]>(`/finance/costs?field_id=${selectedField.id}${seasonParam}`),
                apiFetch<CostSummary>(`/finance/costs/summary?field_id=${selectedField.id}${seasonParam}`),
                apiFetch<RevenueEntry[]>(`/finance/revenue?field_id=${selectedField.id}${seasonParam}`),
                apiFetch<Season[]>(`/finance/seasons?field_id=${selectedField.id}`),
            ]);
            setCosts(costsData);
            setSummary(summaryData);
            setRevenues(revenuesData);
            setSeasons(seasonsData);
        } catch (err) {
            console.error("Failed to fetch data:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [token, selectedField, selectedSeason]);

    const handleCostSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedField || !costForm.category || !costForm.amount) return;
        if (parseFloat(costForm.amount) <= 0) return;

        setSubmitting(true);
        try {
            await apiFetch("/finance/costs", {
                method: "POST",
                body: JSON.stringify({
                    field: selectedField.id,
                    season: selectedSeason !== "all" ? parseInt(selectedSeason) : null,
                    category: costForm.category,
                    description: costForm.description,
                    amount: parseFloat(costForm.amount),
                    quantity: costForm.quantity ? parseFloat(costForm.quantity) : null,
                    unit: costForm.unit,
                    date: costForm.date,
                }),
            });
            setCostForm({
                category: "",
                description: "",
                amount: "",
                quantity: "",
                unit: "",
                date: new Date().toISOString().split("T")[0],
            });
            fetchData();
        } catch (err) {
            console.error("Failed to add cost:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleRevenueSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedField || !revenueForm.crop || !revenueForm.quantity_sold || !revenueForm.price_per_unit) return;

        setSubmitting(true);
        try {
            await apiFetch("/finance/revenue", {
                method: "POST",
                body: JSON.stringify({
                    field: selectedField.id,
                    season: selectedSeason !== "all" ? parseInt(selectedSeason) : null,
                    crop: revenueForm.crop,
                    quantity_sold: parseFloat(revenueForm.quantity_sold),
                    unit: revenueForm.unit,
                    price_per_unit: parseFloat(revenueForm.price_per_unit),
                    total_amount: parseFloat(revenueForm.quantity_sold) * parseFloat(revenueForm.price_per_unit),
                    buyer: revenueForm.buyer,
                    date: revenueForm.date,
                    notes: revenueForm.notes,
                }),
            });
            setRevenueForm({
                crop: "",
                quantity_sold: "",
                unit: "kg",
                price_per_unit: "",
                buyer: "",
                date: new Date().toISOString().split("T")[0],
                notes: "",
            });
            fetchData();
        } catch (err) {
            console.error("Failed to add revenue:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleDeleteCost = async (id: number) => {
        try {
            await apiFetch(`/finance/costs/${id}`, { method: "DELETE" });
            fetchData();
        } catch (err) {
            console.error("Failed to delete cost:", err);
        }
    };

    const handleDeleteRevenue = async (id: number) => {
        try {
            await apiFetch(`/finance/revenue/${id}`, { method: "DELETE" });
            fetchData();
        } catch (err) {
            console.error("Failed to delete revenue:", err);
        }
    };

    const getCategoryIcon = (category: string) => {
        const cat = COST_CATEGORIES.find((c) => c.value === category);
        return cat ? cat.icon : MoreHorizontal;
    };

    const totalRevenue = revenues.reduce((sum, r) => sum + r.total_amount, 0);
    const totalCosts = summary?.total || 0;
    const profitLoss = totalRevenue - totalCosts;

    if (!selectedField) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-4xl text-muted-foreground mb-4">agriculture</span>
                    <p className="text-muted-foreground">Please select a field to track costs and revenue.</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Cost & Revenue Tracker</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Track expenses and income for {selectedField.name}
                    </p>
                </div>
                <Select value={selectedSeason} onValueChange={setSelectedSeason}>
                    <SelectTrigger className="w-48">
                        <SelectValue placeholder="All Seasons" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Seasons</SelectItem>
                        {seasons.map((s) => (
                            <SelectItem key={s.id} value={String(s.id)}>
                                {s.name} ({s.year})
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Revenue</p>
                                <p className="text-2xl font-bold text-green-600">
                                    ₹{totalRevenue.toLocaleString("en-IN")}
                                </p>
                            </div>
                            <div className="size-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                                <ArrowUpRight className="h-6 w-6 text-green-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Costs</p>
                                <p className="text-2xl font-bold text-red-600">
                                    ₹{totalCosts.toLocaleString("en-IN")}
                                </p>
                            </div>
                            <div className="size-12 rounded-xl bg-red-500/10 flex items-center justify-center">
                                <ArrowDownRight className="h-6 w-6 text-red-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Net Profit/Loss</p>
                                <p className={`text-2xl font-bold ${profitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    ₹{Math.abs(profitLoss).toLocaleString("en-IN")}
                                    <span className="text-sm ml-1">{profitLoss >= 0 ? 'Profit' : 'Loss'}</span>
                                </p>
                            </div>
                            <div className={`size-12 rounded-xl flex items-center justify-center ${profitLoss >= 0 ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                                {profitLoss >= 0 ?
                                    <TrendingUp className="h-6 w-6 text-green-600" /> :
                                    <TrendingDown className="h-6 w-6 text-red-600" />
                                }
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabs for Costs/Revenue */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2 max-w-md">
                    <TabsTrigger value="costs" className="gap-2">
                        <ArrowDownRight className="h-4 w-4" />
                        Expenses ({costs.length})
                    </TabsTrigger>
                    <TabsTrigger value="revenue" className="gap-2">
                        <ArrowUpRight className="h-4 w-4" />
                        Income ({revenues.length})
                    </TabsTrigger>
                </TabsList>

                {/* Costs Tab */}
                <TabsContent value="costs" className="mt-6">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Add Cost Form */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Plus className="h-5 w-5" />
                                    Add Expense
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleCostSubmit} className="space-y-4">
                                    <div>
                                        <Label>Category</Label>
                                        <Select value={costForm.category} onValueChange={(v) => setCostForm({ ...costForm, category: v })}>
                                            <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
                                            <SelectContent>
                                                {COST_CATEGORIES.map((cat) => (
                                                    <SelectItem key={cat.value} value={cat.value}>
                                                        <div className="flex items-center gap-2">
                                                            <cat.icon className="h-4 w-4" />
                                                            {cat.label}
                                                        </div>
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div>
                                        <Label>Description</Label>
                                        <Input value={costForm.description} onChange={(e) => setCostForm({ ...costForm, description: e.target.value })} placeholder="e.g., Urea 50kg" />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Amount (₹)</Label>
                                            <Input type="number" value={costForm.amount} onChange={(e) => setCostForm({ ...costForm, amount: e.target.value })} placeholder="0" required min="0" />
                                        </div>
                                        <div>
                                            <Label>Date</Label>
                                            <Input type="date" value={costForm.date} onChange={(e) => setCostForm({ ...costForm, date: e.target.value })} />
                                        </div>
                                    </div>
                                    <Button type="submit" className="w-full" disabled={submitting}>
                                        {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
                                        Add Expense
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>

                        {/* Costs List */}
                        <Card className="lg:col-span-2">
                            <CardHeader>
                                <CardTitle>Recent Expenses</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {loading ? (
                                    <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
                                ) : costs.length > 0 ? (
                                    <div className="divide-y max-h-96 overflow-y-auto">
                                        {costs.map((cost) => {
                                            const Icon = getCategoryIcon(cost.category);
                                            return (
                                                <div key={cost.id} className="flex items-center justify-between py-3">
                                                    <div className="flex items-center gap-3">
                                                        <div className="p-2 bg-muted rounded-full"><Icon className="h-4 w-4" /></div>
                                                        <div>
                                                            <div className="font-medium">{cost.description || cost.category_display}</div>
                                                            <div className="text-sm text-muted-foreground">{new Date(cost.date).toLocaleDateString("en-IN")}</div>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-4">
                                                        <span className="font-semibold text-red-600">-₹{cost.amount.toLocaleString("en-IN")}</span>
                                                        <Button variant="ghost" size="sm" onClick={() => handleDeleteCost(cost.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <p className="text-muted-foreground text-center py-8">No expenses recorded yet.</p>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Revenue Tab */}
                <TabsContent value="revenue" className="mt-6">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Add Revenue Form */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Plus className="h-5 w-5" />
                                    Add Income
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleRevenueSubmit} className="space-y-4">
                                    <div>
                                        <Label>Crop/Product</Label>
                                        <Input value={revenueForm.crop} onChange={(e) => setRevenueForm({ ...revenueForm, crop: e.target.value })} placeholder="e.g., Rice, Wheat" required />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Quantity Sold</Label>
                                            <Input type="number" value={revenueForm.quantity_sold} onChange={(e) => setRevenueForm({ ...revenueForm, quantity_sold: e.target.value })} placeholder="0" required min="0" />
                                        </div>
                                        <div>
                                            <Label>Unit</Label>
                                            <Select value={revenueForm.unit} onValueChange={(v) => setRevenueForm({ ...revenueForm, unit: v })}>
                                                <SelectTrigger><SelectValue /></SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="kg">Kg</SelectItem>
                                                    <SelectItem value="quintal">Quintal</SelectItem>
                                                    <SelectItem value="ton">Ton</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Price per Unit (₹)</Label>
                                            <Input type="number" value={revenueForm.price_per_unit} onChange={(e) => setRevenueForm({ ...revenueForm, price_per_unit: e.target.value })} placeholder="0" required min="0" />
                                        </div>
                                        <div>
                                            <Label>Date</Label>
                                            <Input type="date" value={revenueForm.date} onChange={(e) => setRevenueForm({ ...revenueForm, date: e.target.value })} />
                                        </div>
                                    </div>
                                    <div>
                                        <Label>Buyer (optional)</Label>
                                        <Input value={revenueForm.buyer} onChange={(e) => setRevenueForm({ ...revenueForm, buyer: e.target.value })} placeholder="e.g., Mandi, Local trader" />
                                    </div>
                                    {revenueForm.quantity_sold && revenueForm.price_per_unit && (
                                        <div className="p-3 bg-green-500/10 rounded-lg text-center">
                                            <span className="text-sm text-muted-foreground">Total: </span>
                                            <span className="font-bold text-green-600">
                                                ₹{(parseFloat(revenueForm.quantity_sold) * parseFloat(revenueForm.price_per_unit)).toLocaleString("en-IN")}
                                            </span>
                                        </div>
                                    )}
                                    <Button type="submit" className="w-full" disabled={submitting}>
                                        {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
                                        Add Income
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>

                        {/* Revenue List */}
                        <Card className="lg:col-span-2">
                            <CardHeader>
                                <CardTitle>Recent Income</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {loading ? (
                                    <div className="flex justify-center py-8"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
                                ) : revenues.length > 0 ? (
                                    <div className="divide-y max-h-96 overflow-y-auto">
                                        {revenues.map((rev) => (
                                            <div key={rev.id} className="flex items-center justify-between py-3">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-2 bg-green-500/10 rounded-full"><Wheat className="h-4 w-4 text-green-600" /></div>
                                                    <div>
                                                        <div className="font-medium">{rev.crop}</div>
                                                        <div className="text-sm text-muted-foreground">
                                                            {rev.quantity_sold} {rev.unit} @ ₹{rev.price_per_unit}/{rev.unit}
                                                            {rev.buyer && ` • ${rev.buyer}`}
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <span className="font-semibold text-green-600">+₹{rev.total_amount.toLocaleString("en-IN")}</span>
                                                    <Button variant="ghost" size="sm" onClick={() => handleDeleteRevenue(rev.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-muted-foreground text-center py-8">No income recorded yet. Add your first sale above.</p>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
