// src/components/planning/LaborManager.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

type LaborEntry = {
    id: number;
    field: number;
    field_name: string;
    worker_name: string;
    work_type: string;
    hours_worked: number;
    hourly_rate: number;
    total_wage: number;
    date: string;
    notes: string;
    is_paid: boolean;
};

type LaborResponse = {
    entries: LaborEntry[];
    summary: {
        total_entries: number;
        total_wages: number;
        unpaid_wages: number;
    };
};

export function LaborManager() {
    const { token } = useAuth();
    const { selectedField } = useField();
    const [data, setData] = useState<LaborResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);

    const [formData, setFormData] = useState({
        worker_name: "",
        work_type: "",
        hours_worked: "",
        hourly_rate: "",
        date: new Date().toISOString().split("T")[0],
        notes: "",
    });

    const fetchLabor = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const url = selectedField
                ? `/planning/labor?field_id=${selectedField.id}`
                : "/planning/labor";
            const response = await apiFetch<LaborResponse>(url);
            setData(response);
        } catch (err) {
            console.error("Failed to fetch labor entries:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLabor();
    }, [token, selectedField]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedField || !formData.worker_name || !formData.hours_worked) return;

        const hours = parseFloat(formData.hours_worked);
        const rate = parseFloat(formData.hourly_rate) || 0;

        if (hours <= 0 || rate < 0) {
            alert("Please enter valid positive numbers for hours and rate");
            return;
        }

        setSubmitting(true);
        try {
            await apiFetch("/planning/labor", {
                method: "POST",
                body: JSON.stringify({
                    field: selectedField.id,
                    worker_name: formData.worker_name,
                    work_type: formData.work_type,
                    hours_worked: hours,
                    hourly_rate: rate,
                    date: formData.date,
                    notes: formData.notes,
                }),
            });
            setFormData({
                worker_name: "",
                work_type: "",
                hours_worked: "",
                hourly_rate: "",
                date: new Date().toISOString().split("T")[0],
                notes: "",
            });
            setShowAddForm(false);
            fetchLabor();
        } catch (err) {
            console.error("Failed to add labor entry:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleMarkPaid = async (entry: LaborEntry) => {
        try {
            await apiFetch(`/planning/labor/${entry.id}`, {
                method: "PUT",
                body: JSON.stringify({ is_paid: !entry.is_paid }),
            });
            fetchLabor();
        } catch (err) {
            console.error("Failed to update payment status:", err);
        }
    };

    const handleDelete = async (id: number) => {
        try {
            await apiFetch(`/planning/labor/${id}`, { method: "DELETE" });
            fetchLabor();
        } catch (err) {
            console.error("Failed to delete entry:", err);
        }
    };

    if (!selectedField) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-5xl text-muted-foreground mb-4">group</span>
                    <p className="text-muted-foreground">Please select a field to manage labor entries.</p>
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

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Labor Management</h1>
                    <p className="text-muted-foreground text-sm mt-1">Track worker hours and wages</p>
                </div>
                <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
                    <span className="material-symbols-outlined text-lg">{showAddForm ? "close" : "add"}</span>
                    {showAddForm ? "Cancel" : "Add Entry"}
                </Button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Entries</p>
                                <p className="text-2xl font-bold mt-1">{data?.summary.total_entries || 0}</p>
                            </div>
                            <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                <span className="material-symbols-outlined">group</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Wages</p>
                                <p className="text-2xl font-bold mt-1 text-primary">
                                    ₹{(data?.summary.total_wages || 0).toLocaleString("en-IN")}
                                </p>
                            </div>
                            <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                <span className="material-symbols-outlined">currency_rupee</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card className={cn(data?.summary.unpaid_wages && "border-amber-500")}>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Unpaid Wages</p>
                                <p className="text-2xl font-bold mt-1 text-amber-600">
                                    ₹{(data?.summary.unpaid_wages || 0).toLocaleString("en-IN")}
                                </p>
                            </div>
                            <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500">
                                <span className="material-symbols-outlined">schedule</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5">
                        <div className="flex items-start justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Paid</p>
                                <p className="text-2xl font-bold mt-1 text-primary">
                                    ₹{((data?.summary.total_wages || 0) - (data?.summary.unpaid_wages || 0)).toLocaleString("en-IN")}
                                </p>
                            </div>
                            <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                <span className="material-symbols-outlined">check_circle</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Add Entry Form */}
            {showAddForm && (
                <Card>
                    <CardContent className="p-6">
                        <h3 className="font-bold mb-4">Add Labor Entry</h3>
                        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Worker Name</Label>
                                <Input
                                    value={formData.worker_name}
                                    onChange={(e) => setFormData({ ...formData, worker_name: e.target.value })}
                                    placeholder="Enter worker name"
                                    required
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Work Type</Label>
                                <Input
                                    value={formData.work_type}
                                    onChange={(e) => setFormData({ ...formData, work_type: e.target.value })}
                                    placeholder="e.g., Weeding, Harvesting"
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Date</Label>
                                <Input
                                    type="date"
                                    value={formData.date}
                                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Hours Worked</Label>
                                <Input
                                    type="number"
                                    step="0.5"
                                    value={formData.hours_worked}
                                    onChange={(e) => setFormData({ ...formData, hours_worked: e.target.value })}
                                    placeholder="8"
                                    required
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Hourly Rate (₹)</Label>
                                <Input
                                    type="number"
                                    value={formData.hourly_rate}
                                    onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                                    placeholder="50"
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
                                    Add Entry
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* Labor Entries List */}
            <Card>
                <CardHeader className="pb-4 border-b">
                    <CardTitle className="text-lg">Recent Entries</CardTitle>
                </CardHeader>
                <div className="divide-y">
                    {data?.entries.length ? (
                        data.entries.map((entry) => (
                            <div
                                key={entry.id}
                                className="p-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <div className={cn(
                                        "size-10 rounded-lg flex items-center justify-center",
                                        entry.is_paid ? "bg-primary/10 text-primary" : "bg-amber-500/10 text-amber-600"
                                    )}>
                                        <span className="material-symbols-outlined">person</span>
                                    </div>
                                    <div>
                                        <div className="font-medium">{entry.worker_name}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {entry.work_type || "General work"} • {entry.hours_worked}h @ ₹{entry.hourly_rate}/hr
                                        </div>
                                        <div className="text-xs text-muted-foreground">
                                            {new Date(entry.date).toLocaleDateString("en-IN", {
                                                day: "numeric",
                                                month: "short",
                                                year: "numeric"
                                            })}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <div className="font-bold text-lg">
                                            ₹{entry.total_wage.toLocaleString("en-IN")}
                                        </div>
                                        <Badge className={cn(
                                            "text-xs",
                                            entry.is_paid
                                                ? "bg-primary/10 text-primary border-primary/20"
                                                : "bg-amber-500/10 text-amber-600 border-amber-200"
                                        )}>
                                            {entry.is_paid ? "Paid" : "Pending"}
                                        </Badge>
                                    </div>
                                    <div className="flex gap-1">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8"
                                            onClick={() => handleMarkPaid(entry)}
                                            title={entry.is_paid ? "Mark as unpaid" : "Mark as paid"}
                                        >
                                            <span className={cn(
                                                "material-symbols-outlined text-lg",
                                                entry.is_paid && "text-primary"
                                            )}>
                                                {entry.is_paid ? "check_circle" : "radio_button_unchecked"}
                                            </span>
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-destructive hover:text-destructive"
                                            onClick={() => handleDelete(entry.id)}
                                        >
                                            <span className="material-symbols-outlined text-lg">delete</span>
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="p-12 text-center">
                            <span className="material-symbols-outlined text-4xl text-muted-foreground mb-2">group_off</span>
                            <p className="text-muted-foreground text-sm">No labor entries yet. Add your first entry above.</p>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
}
