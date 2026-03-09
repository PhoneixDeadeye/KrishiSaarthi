// src/components/planning/InventoryTracker.tsx

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/AuthContext";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";

const INVENTORY_CATEGORIES = [
    { value: "seeds", label: "Seeds", icon: "grass" },
    { value: "fertilizer", label: "Fertilizer", icon: "science" },
    { value: "pesticide", label: "Pesticide", icon: "bug_report" },
    { value: "herbicide", label: "Herbicide", icon: "eco" },
    { value: "tools", label: "Tools", icon: "construction" },
    { value: "other", label: "Other", icon: "inventory_2" },
];

type InventoryItem = {
    id: number;
    name: string;
    category: string;
    category_display: string;
    description: string;
    quantity: number;
    unit: string;
    reorder_level: number;
    is_low_stock: boolean;
    purchase_price: number | null;
    supplier: string;
};

type InventoryResponse = {
    items: InventoryItem[];
    summary: {
        total_items: number;
        low_stock_count: number;
    };
};

export function InventoryTracker() {
    const { token } = useAuth();
    const [data, setData] = useState<InventoryResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [transactionItem, setTransactionItem] = useState<InventoryItem | null>(null);
    const [transactionType, setTransactionType] = useState<"purchase" | "use">("purchase");
    const [transactionQty, setTransactionQty] = useState("");
    const [activeCategory, setActiveCategory] = useState<string>("all");

    const [formData, setFormData] = useState({
        name: "",
        category: "",
        quantity: "",
        unit: "",
        reorder_level: "",
        purchase_price: "",
        supplier: "",
    });

    const fetchInventory = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const response = await apiFetch<InventoryResponse>("/planning/inventory");
            setData(response);
        } catch (err) {
            logger.error("Failed to fetch inventory:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchInventory();
    }, [token]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name || !formData.category || !formData.unit) return;

        const quantity = parseFloat(formData.quantity) || 0;
        const reorderLevel = parseFloat(formData.reorder_level) || 0;
        const purchasePrice = formData.purchase_price ? parseFloat(formData.purchase_price) : null;

        if (quantity < 0 || reorderLevel < 0 || (purchasePrice !== null && purchasePrice < 0)) {
            alert("Please enter valid non-negative numbers");
            return;
        }

        setSubmitting(true);
        try {
            await apiFetch("/planning/inventory", {
                method: "POST",
                body: JSON.stringify({
                    name: formData.name,
                    category: formData.category,
                    quantity,
                    unit: formData.unit,
                    reorder_level: reorderLevel,
                    purchase_price: purchasePrice,
                    supplier: formData.supplier,
                }),
            });
            setFormData({ name: "", category: "", quantity: "", unit: "", reorder_level: "", purchase_price: "", supplier: "" });
            setShowAddForm(false);
            fetchInventory();
        } catch (err) {
            logger.error("Failed to add item:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleTransaction = async () => {
        if (!transactionItem || !transactionQty) return;
        const qty = parseFloat(transactionQty);

        if (qty <= 0) {
            alert("Quantity must be greater than 0");
            return;
        }

        if (transactionType === "use" && qty > transactionItem.quantity) {
            alert("Insufficient stock!");
            return;
        }
        setSubmitting(true);
        try {
            await apiFetch(`/planning/inventory/${transactionItem.id}/transaction`, {
                method: "POST",
                body: JSON.stringify({
                    transaction_type: transactionType,
                    quantity: qty,
                    date: new Date().toISOString().split("T")[0],
                }),
            });
            setTransactionItem(null);
            setTransactionQty("");
            fetchInventory();
        } catch (err) {
            logger.error("Failed to record transaction:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id: number) => {
        try {
            await apiFetch(`/planning/inventory/${id}`, { method: "DELETE" });
            fetchInventory();
        } catch (err) {
            logger.error("Failed to delete item:", err);
        }
    };

    const getCategoryIcon = (category: string) => INVENTORY_CATEGORIES.find((c) => c.value === category)?.icon || "inventory_2";

    const filteredItems = data?.items.filter(item =>
        activeCategory === "all" || item.category === activeCategory
    ) || [];

    if (loading) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-4xl animate-spin text-primary">progress_activity</span>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Inventory</h1>
                    <p className="text-muted-foreground text-sm mt-1">Track seeds, fertilizers, and supplies</p>
                </div>
                <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
                    <span className="material-symbols-outlined text-lg">{showAddForm ? "close" : "add"}</span>
                    {showAddForm ? "Cancel" : "Add Item"}
                </Button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Items</p>
                                <p className="text-2xl font-bold mt-1">{data?.summary.total_items || 0}</p>
                            </div>
                            <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                <span className="material-symbols-outlined">inventory_2</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card className={cn(data?.summary.low_stock_count && "border-amber-500")}>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Low Stock</p>
                                <p className="text-2xl font-bold mt-1 text-amber-600">{data?.summary.low_stock_count || 0}</p>
                            </div>
                            <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500">
                                <span className="material-symbols-outlined">warning</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Categories</p>
                                <p className="text-2xl font-bold mt-1">{new Set(data?.items.map(i => i.category)).size || 0}</p>
                            </div>
                            <div className="size-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
                                <span className="material-symbols-outlined">category</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">In Stock</p>
                                <p className="text-2xl font-bold mt-1 text-primary">
                                    {(data?.summary.total_items || 0) - (data?.summary.low_stock_count || 0)}
                                </p>
                            </div>
                            <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                <span className="material-symbols-outlined">check_circle</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Add Item Form */}
            {showAddForm && (
                <Card>
                    <CardContent className="p-6">
                        <h3 className="font-bold mb-4">Add New Item</h3>
                        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Name</Label>
                                <Input
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="e.g., DAP Fertilizer"
                                    required
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Category</Label>
                                <Select
                                    value={formData.category}
                                    onValueChange={(v) => setFormData({ ...formData, category: v })}
                                >
                                    <SelectTrigger className="bg-background">
                                        <SelectValue placeholder="Select category" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {INVENTORY_CATEGORIES.map((cat) => (
                                            <SelectItem key={cat.value} value={cat.value}>
                                                <div className="flex items-center gap-2">
                                                    <span className="material-symbols-outlined text-sm">{cat.icon}</span>
                                                    {cat.label}
                                                </div>
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Quantity</Label>
                                    <Input
                                        type="number"
                                        value={formData.quantity}
                                        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                                        placeholder="0"
                                        className="bg-background"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Unit</Label>
                                    <Input
                                        value={formData.unit}
                                        onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                                        placeholder="kg, L"
                                        required
                                        className="bg-background"
                                    />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Reorder Level</Label>
                                <Input
                                    type="number"
                                    value={formData.reorder_level}
                                    onChange={(e) => setFormData({ ...formData, reorder_level: e.target.value })}
                                    placeholder="10"
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Supplier (optional)</Label>
                                <Input
                                    value={formData.supplier}
                                    onChange={(e) => setFormData({ ...formData, supplier: e.target.value })}
                                    placeholder="Supplier name"
                                    className="bg-background"
                                />
                            </div>
                            <div className="flex items-end">
                                <Button type="submit" disabled={submitting} className="w-full gap-2">
                                    {submitting ? (
                                        <span className="material-symbols-outlined text-lg animate-spin">progress_activity</span>
                                    ) : (
                                        <span className="material-symbols-outlined text-lg">add</span>
                                    )}
                                    Add Item
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* Category Filters */}
            <div className="flex gap-2 overflow-x-auto pb-2">
                <Button
                    variant={activeCategory === "all" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setActiveCategory("all")}
                >
                    All
                </Button>
                {INVENTORY_CATEGORIES.map((cat) => (
                    <Button
                        key={cat.value}
                        variant={activeCategory === cat.value ? "default" : "outline"}
                        size="sm"
                        onClick={() => setActiveCategory(cat.value)}
                        className="gap-1"
                    >
                        <span className="material-symbols-outlined text-sm">{cat.icon}</span>
                        {cat.label}
                    </Button>
                ))}
            </div>

            {/* Inventory Grid */}
            {filteredItems.length === 0 ? (
                <Card className="text-center">
                    <CardContent className="p-12 space-y-4 flex flex-col items-center">
                        <div className="size-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                            <span className="material-symbols-outlined text-3xl text-primary">inventory_2</span>
                        </div>
                        <h3 className="text-lg font-bold">No Inventory Items Yet</h3>
                        <p className="text-muted-foreground text-sm max-w-sm mx-auto">
                            Track seeds, fertilizers, and equipment. Add your first item to get started.
                        </p>
                        <Button onClick={() => setShowAddForm(true)} className="gap-2">
                            <span className="material-symbols-outlined text-lg">add</span>
                            Add First Item
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredItems.map((item) => (
                        <Card
                            key={item.id}
                            className={cn("transition-all hover:shadow-md", item.is_low_stock && "border-amber-500")}
                        >
                            <CardContent className="p-4">
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-3">
                                        <div className={cn(
                                            "size-10 rounded-lg flex items-center justify-center",
                                            item.is_low_stock ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600" : "bg-primary/10 text-primary"
                                        )}>
                                            <span className="material-symbols-outlined">{getCategoryIcon(item.category)}</span>
                                        </div>
                                        <div>
                                            <h3 className="font-medium">{item.name}</h3>
                                            <p className="text-xs text-muted-foreground">{item.category_display}</p>
                                        </div>
                                    </div>
                                    {item.is_low_stock && (
                                        <Badge className="bg-amber-500/10 text-amber-600 border-amber-200 dark:border-amber-800 animate-pulse">
                                            Low Stock
                                        </Badge>
                                    )}
                                </div>

                                {/* Stock Level */}
                                <div className="text-center py-4 bg-muted/50 rounded-lg mb-3">
                                    <p className="text-3xl font-bold">{item.quantity}</p>
                                    <p className="text-sm text-muted-foreground">{item.unit}</p>
                                    {item.reorder_level > 0 && (
                                        <div className="mt-2 mx-auto w-32">
                                            <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                                                <div
                                                    className={cn(
                                                        "h-full rounded-full transition-all",
                                                        item.is_low_stock ? "bg-amber-500" : "bg-primary"
                                                    )}
                                                    style={{ width: `${Math.min((item.quantity / (item.reorder_level * 3)) * 100, 100)}%` }}
                                                />
                                            </div>
                                            <p className="text-[10px] text-muted-foreground mt-1">
                                                Reorder at {item.reorder_level} {item.unit}
                                            </p>
                                        </div>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="flex-1 gap-1"
                                        onClick={() => { setTransactionItem(item); setTransactionType("purchase"); }}
                                    >
                                        <span className="material-symbols-outlined text-sm">add</span>
                                        Add
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="flex-1 gap-1"
                                        onClick={() => { setTransactionItem(item); setTransactionType("use"); }}
                                    >
                                        <span className="material-symbols-outlined text-sm">remove</span>
                                        Use
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-8 w-8 text-destructive hover:text-destructive"
                                        onClick={() => handleDelete(item.id)}
                                    >
                                        <span className="material-symbols-outlined text-sm">delete</span>
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Transaction Modal */}
            {transactionItem && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <Card className="w-full max-w-md">
                        <CardContent className="p-6 space-y-4">
                            <div className="flex items-center gap-3">
                                <div className={cn(
                                    "size-10 rounded-lg flex items-center justify-center",
                                    transactionType === "purchase" ? "bg-primary/10 text-primary" : "bg-amber-500/10 text-amber-600"
                                )}>
                                    <span className="material-symbols-outlined">
                                        {transactionType === "purchase" ? "add_shopping_cart" : "shopping_cart_checkout"}
                                    </span>
                                </div>
                                <div>
                                    <h3 className="font-bold">
                                        {transactionType === "purchase" ? "Add Stock" : "Use Stock"}
                                    </h3>
                                    <p className="text-sm text-muted-foreground">{transactionItem.name}</p>
                                </div>
                            </div>

                            <div className="p-4 bg-muted/50 rounded-lg text-center">
                                <p className="text-sm text-muted-foreground">Current Stock</p>
                                <p className="text-2xl font-bold">{transactionItem.quantity} {transactionItem.unit}</p>
                            </div>

                            <div className="space-y-2">
                                <Label>Quantity ({transactionItem.unit})</Label>
                                <Input
                                    type="number"
                                    value={transactionQty}
                                    onChange={(e) => setTransactionQty(e.target.value)}
                                    placeholder="Enter quantity"
                                    autoFocus
                                    className="bg-background"
                                />
                            </div>

                            <div className="flex gap-2">
                                <Button onClick={handleTransaction} disabled={submitting} className="flex-1 gap-2">
                                    {submitting ? (
                                        <span className="material-symbols-outlined text-lg animate-spin">progress_activity</span>
                                    ) : (
                                        <span className="material-symbols-outlined text-lg">check</span>
                                    )}
                                    Confirm
                                </Button>
                                <Button variant="outline" onClick={() => setTransactionItem(null)}>
                                    Cancel
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
