// src/components/planning/EquipmentScheduler.tsx

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<string, { bg: string; text: string; icon: string }> = {
    available: { bg: "bg-primary/10", text: "text-primary", icon: "check_circle" },
    in_use: { bg: "bg-blue-500/10", text: "text-blue-600", icon: "schedule" },
    maintenance: { bg: "bg-amber-500/10", text: "text-amber-600", icon: "build" },
    retired: { bg: "bg-gray-500/10", text: "text-gray-600", icon: "block" },
};

type Equipment = {
    id: number;
    name: string;
    equipment_type: string;
    description: string;
    status: string;
    status_display: string;
    last_maintenance: string | null;
    upcoming_bookings: Booking[];
};

type Booking = {
    id: number;
    equipment: number;
    equipment_name: string;
    field: number;
    field_name: string;
    start_datetime: string;
    end_datetime: string;
    purpose: string;
    is_completed: boolean;
};

type EquipmentResponse = {
    equipment: Equipment[];
    summary: {
        total: number;
        available: number;
        in_use: number;
        maintenance: number;
    };
};

export function EquipmentScheduler() {
    const { token } = useAuth();
    const { selectedField } = useField();
    const [data, setData] = useState<EquipmentResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [showAddEquipment, setShowAddEquipment] = useState(false);
    const [bookingEquipment, setBookingEquipment] = useState<Equipment | null>(null);

    const [equipmentForm, setEquipmentForm] = useState({
        name: "",
        equipment_type: "",
        description: "",
    });

    const [bookingForm, setBookingForm] = useState({
        start_datetime: "",
        end_datetime: "",
        purpose: "",
    });

    const fetchEquipment = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const response = await apiFetch<EquipmentResponse>("/planning/equipment");
            setData(response);
        } catch (err) {
            console.error("Failed to fetch equipment:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEquipment();
    }, [token]);

    const handleAddEquipment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!equipmentForm.name || !equipmentForm.equipment_type) return;

        setSubmitting(true);
        try {
            await apiFetch("/planning/equipment", {
                method: "POST",
                body: JSON.stringify(equipmentForm),
            });
            setEquipmentForm({ name: "", equipment_type: "", description: "" });
            setShowAddEquipment(false);
            fetchEquipment();
        } catch (err) {
            console.error("Failed to add equipment:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleBooking = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!bookingEquipment || !selectedField || !bookingForm.start_datetime) return;

        const start = new Date(bookingForm.start_datetime);
        const end = bookingForm.end_datetime ? new Date(bookingForm.end_datetime) : start;

        if (end < start) {
            alert("End time cannot be before start time");
            return;
        }

        if (bookingEquipment.status !== 'available') {
            alert("This equipment is not available for booking");
            return;
        }

        setSubmitting(true);
        try {
            await apiFetch(`/planning/equipment/${bookingEquipment.id}/book`, {
                method: "POST",
                body: JSON.stringify({
                    field: selectedField.id,
                    start_datetime: bookingForm.start_datetime,
                    end_datetime: bookingForm.end_datetime || bookingForm.start_datetime,
                    purpose: bookingForm.purpose,
                }),
            });
            setBookingForm({ start_datetime: "", end_datetime: "", purpose: "" });
            setBookingEquipment(null);
            fetchEquipment();
        } catch (err) {
            console.error("Failed to book equipment:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleStatusChange = async (equipment: Equipment, newStatus: string) => {
        try {
            await apiFetch(`/planning/equipment/${equipment.id}`, {
                method: "PUT",
                body: JSON.stringify({ status: newStatus }),
            });
            fetchEquipment();
        } catch (err) {
            console.error("Failed to update status:", err);
        }
    };

    const handleDeleteEquipment = async (id: number) => {
        try {
            await apiFetch(`/planning/equipment/${id}`, { method: "DELETE" });
            fetchEquipment();
        } catch (err) {
            console.error("Failed to delete equipment:", err);
        }
    };

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
                    <h1 className="text-2xl font-bold tracking-tight">Equipment</h1>
                    <p className="text-muted-foreground text-sm mt-1">Manage farm equipment and bookings</p>
                </div>
                <Button onClick={() => setShowAddEquipment(!showAddEquipment)} className="gap-2">
                    <span className="material-symbols-outlined text-lg">{showAddEquipment ? "close" : "add"}</span>
                    {showAddEquipment ? "Cancel" : "Add Equipment"}
                </Button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold">{data?.summary.total || 0}</p>
                        <p className="text-sm text-muted-foreground">Total</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold text-primary">{data?.summary.available || 0}</p>
                        <p className="text-sm text-muted-foreground">Available</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold text-blue-600">{data?.summary.in_use || 0}</p>
                        <p className="text-sm text-muted-foreground">In Use</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold text-amber-600">{data?.summary.maintenance || 0}</p>
                        <p className="text-sm text-muted-foreground">Maintenance</p>
                    </CardContent>
                </Card>
            </div>

            {/* Add Equipment Form */}
            {showAddEquipment && (
                <Card>
                    <CardContent className="p-6">
                        <h3 className="font-bold mb-4">Register New Equipment</h3>
                        <form onSubmit={handleAddEquipment} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Name</Label>
                                <Input
                                    value={equipmentForm.name}
                                    onChange={(e) => setEquipmentForm({ ...equipmentForm, name: e.target.value })}
                                    placeholder="e.g., John Deere Tractor"
                                    required
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Type</Label>
                                <Input
                                    value={equipmentForm.equipment_type}
                                    onChange={(e) => setEquipmentForm({ ...equipmentForm, equipment_type: e.target.value })}
                                    placeholder="e.g., Tractor, Pump, Sprayer"
                                    required
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
                                    Add Equipment
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* Equipment Grid */}
            {data?.equipment.length === 0 ? (
                <Card className="text-center">
                    <CardContent className="p-12 space-y-4 flex flex-col items-center">
                        <div className="size-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                            <span className="material-symbols-outlined text-3xl text-primary">agriculture</span>
                        </div>
                        <h3 className="text-lg font-bold">No Equipment Registered</h3>
                        <p className="text-muted-foreground text-sm max-w-sm mx-auto">
                            Track tractors, pumps, and other farm equipment. Add your first item to get started.
                        </p>
                        <Button onClick={() => setShowAddEquipment(true)} className="gap-2">
                            <span className="material-symbols-outlined text-lg">add</span>
                            Add First Equipment
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data?.equipment.map((eq) => {
                        const statusStyle = STATUS_COLORS[eq.status] || STATUS_COLORS.retired;
                        return (
                            <Card key={eq.id} className="hover:shadow-md transition-all">
                                <CardContent className="p-4">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <div className="size-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                                <span className="material-symbols-outlined">agriculture</span>
                                            </div>
                                            <div>
                                                <h3 className="font-medium">{eq.name}</h3>
                                                <p className="text-xs text-muted-foreground">{eq.equipment_type}</p>
                                            </div>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-destructive hover:text-destructive"
                                            onClick={() => handleDeleteEquipment(eq.id)}
                                        >
                                            <span className="material-symbols-outlined text-lg">delete</span>
                                        </Button>
                                    </div>

                                    {/* Status */}
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className={cn("size-8 rounded-lg flex items-center justify-center", statusStyle.bg, statusStyle.text)}>
                                            <span className="material-symbols-outlined text-sm">{statusStyle.icon}</span>
                                        </div>
                                        <Select
                                            value={eq.status}
                                            onValueChange={(v) => handleStatusChange(eq, v)}
                                        >
                                            <SelectTrigger className="flex-1 h-8">
                                                <Badge className={cn("text-xs", statusStyle.bg, statusStyle.text, "border-0")}>
                                                    {eq.status_display}
                                                </Badge>
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="available">Available</SelectItem>
                                                <SelectItem value="in_use">In Use</SelectItem>
                                                <SelectItem value="maintenance">Under Maintenance</SelectItem>
                                                <SelectItem value="retired">Retired</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    {eq.last_maintenance && (
                                        <p className="text-xs text-muted-foreground mb-3 flex items-center gap-1">
                                            <span className="material-symbols-outlined text-sm">build</span>
                                            Last maintenance: {new Date(eq.last_maintenance).toLocaleDateString("en-IN")}
                                        </p>
                                    )}

                                    {eq.upcoming_bookings.length > 0 && (
                                        <div className="mb-3 p-2 bg-muted/50 rounded-lg">
                                            <p className="text-xs font-medium mb-1 flex items-center gap-1">
                                                <span className="material-symbols-outlined text-sm text-primary">event</span>
                                                Upcoming
                                            </p>
                                            {eq.upcoming_bookings.slice(0, 2).map((b) => (
                                                <div key={b.id} className="text-xs text-muted-foreground">
                                                    {new Date(b.start_datetime).toLocaleDateString("en-IN", { day: "numeric", month: "short" })} - {b.purpose || "Booked"}
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="w-full gap-2"
                                        disabled={eq.status !== "available" || !selectedField}
                                        onClick={() => setBookingEquipment(eq)}
                                    >
                                        <span className="material-symbols-outlined text-sm">event_available</span>
                                        Book Now
                                    </Button>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}

            {/* Booking Modal */}
            {bookingEquipment && selectedField && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <Card className="w-full max-w-md">
                        <CardContent className="p-6 space-y-4">
                            <div className="flex items-center gap-3">
                                <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                    <span className="material-symbols-outlined">event_available</span>
                                </div>
                                <div>
                                    <h3 className="font-bold">Book Equipment</h3>
                                    <p className="text-sm text-muted-foreground">{bookingEquipment.name}</p>
                                </div>
                            </div>

                            <form onSubmit={handleBooking} className="space-y-4">
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Field</Label>
                                    <Input value={selectedField.name} disabled className="bg-muted" />
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Start Date & Time</Label>
                                    <Input
                                        type="datetime-local"
                                        value={bookingForm.start_datetime}
                                        onChange={(e) => setBookingForm({ ...bookingForm, start_datetime: e.target.value })}
                                        required
                                        className="bg-background"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">End Date & Time</Label>
                                    <Input
                                        type="datetime-local"
                                        value={bookingForm.end_datetime}
                                        onChange={(e) => setBookingForm({ ...bookingForm, end_datetime: e.target.value })}
                                        className="bg-background"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label className="text-sm font-medium">Purpose</Label>
                                    <Input
                                        value={bookingForm.purpose}
                                        onChange={(e) => setBookingForm({ ...bookingForm, purpose: e.target.value })}
                                        placeholder="e.g., Plowing, Harvesting"
                                        className="bg-background"
                                    />
                                </div>
                                <div className="flex gap-2">
                                    <Button type="submit" disabled={submitting} className="flex-1 gap-2">
                                        {submitting ? (
                                            <span className="material-symbols-outlined text-lg animate-spin">progress_activity</span>
                                        ) : (
                                            <span className="material-symbols-outlined text-lg">check</span>
                                        )}
                                        Confirm Booking
                                    </Button>
                                    <Button type="button" variant="outline" onClick={() => setBookingEquipment(null)}>
                                        Cancel
                                    </Button>
                                </div>
                            </form>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
