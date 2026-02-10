// src/components/planning/SeasonCalendar.tsx
"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

const ACTIVITY_TYPES = [
    { value: "sowing", label: "Sowing", icon: "grass", color: "bg-green-500" },
    { value: "irrigation", label: "Irrigation", icon: "water_drop", color: "bg-blue-500" },
    { value: "fertilizing", label: "Fertilizing", icon: "science", color: "bg-yellow-500" },
    { value: "spraying", label: "Spraying", icon: "bug_report", color: "bg-red-500" },
    { value: "weeding", label: "Weeding", icon: "content_cut", color: "bg-violet-500" },
    { value: "harvesting", label: "Harvesting", icon: "agriculture", color: "bg-orange-500" },
    { value: "other", label: "Other", icon: "more_horiz", color: "bg-gray-500" },
];

const STATUS_OPTIONS = [
    { value: "planned", label: "Planned", color: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400" },
    { value: "in_progress", label: "In Progress", color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400" },
    { value: "completed", label: "Completed", color: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" },
    { value: "cancelled", label: "Cancelled", color: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400" },
];

type CalendarEvent = {
    id: number;
    field: number;
    field_name: string;
    title: string;
    activity_type: string;
    activity_type_display: string;
    description: string;
    start_date: string;
    end_date: string;
    status: string;
    status_display: string;
    notes: string;
};

export function SeasonCalendar() {
    const { token } = useAuth();
    const { selectedField } = useField();
    const [events, setEvents] = useState<CalendarEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [currentMonth, setCurrentMonth] = useState(new Date());

    const [formData, setFormData] = useState({
        title: "",
        activity_type: "",
        description: "",
        start_date: "",
        end_date: "",
        notes: "",
    });

    const fetchEvents = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (selectedField) params.append("field_id", String(selectedField.id));
            const response = await apiFetch<CalendarEvent[]>(`/planning/calendar?${params}`);
            setEvents(response);
        } catch (err) {
            console.error("Failed to fetch events:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, [token, selectedField]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedField || !formData.title || !formData.start_date) return;

        setSubmitting(true);
        try {
            await apiFetch("/planning/calendar", {
                method: "POST",
                body: JSON.stringify({
                    field: selectedField.id,
                    title: formData.title,
                    activity_type: formData.activity_type || "other",
                    description: formData.description,
                    start_date: formData.start_date,
                    end_date: formData.end_date || formData.start_date,
                    notes: formData.notes,
                }),
            });
            setFormData({
                title: "",
                activity_type: "",
                description: "",
                start_date: "",
                end_date: "",
                notes: "",
            });
            setShowAddForm(false);
            fetchEvents();
        } catch (err) {
            console.error("Failed to add event:", err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleStatusChange = async (event: CalendarEvent, newStatus: string) => {
        try {
            await apiFetch(`/planning/calendar/${event.id}`, {
                method: "PUT",
                body: JSON.stringify({ status: newStatus }),
            });
            fetchEvents();
        } catch (err) {
            console.error("Failed to update status:", err);
        }
    };

    const handleDelete = async (id: number) => {
        try {
            await apiFetch(`/planning/calendar/${id}`, { method: "DELETE" });
            fetchEvents();
        } catch (err) {
            console.error("Failed to delete event:", err);
        }
    };

    const getActivityInfo = (type: string) => ACTIVITY_TYPES.find((a) => a.value === type) || ACTIVITY_TYPES[6];
    const getStatusInfo = (status: string) => STATUS_OPTIONS.find((s) => s.value === status) || STATUS_OPTIONS[0];

    // Calendar helpers
    const getDaysInMonth = (date: Date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        return { firstDay, daysInMonth };
    };

    const getEventsForDate = (date: Date) => {
        const dateStr = date.toISOString().split("T")[0];
        return events.filter((e) => e.start_date <= dateStr && e.end_date >= dateStr);
    };

    const { firstDay, daysInMonth } = getDaysInMonth(currentMonth);
    const days: (number | null)[] = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(i);

    if (!selectedField) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-5xl text-muted-foreground mb-4">calendar_month</span>
                    <p className="text-muted-foreground">Please select a field to view the calendar.</p>
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
                    <h1 className="text-2xl font-bold tracking-tight">Season Planner</h1>
                    <p className="text-muted-foreground text-sm mt-1">Plan and track your farming activities</p>
                </div>
                <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
                    <span className="material-symbols-outlined text-lg">{showAddForm ? "close" : "add"}</span>
                    {showAddForm ? "Cancel" : "Add Activity"}
                </Button>
            </div>

            {/* Add Event Form */}
            {showAddForm && (
                <Card>
                    <CardContent className="p-6">
                        <h3 className="font-bold mb-4">Add Farm Activity</h3>
                        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Title</Label>
                                <Input
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    placeholder="e.g., Rice Sowing"
                                    required
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Activity Type</Label>
                                <Select
                                    value={formData.activity_type}
                                    onValueChange={(v) => setFormData({ ...formData, activity_type: v })}
                                >
                                    <SelectTrigger className="bg-background">
                                        <SelectValue placeholder="Select type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {ACTIVITY_TYPES.map((type) => (
                                            <SelectItem key={type.value} value={type.value}>
                                                <div className="flex items-center gap-2">
                                                    <span className="material-symbols-outlined text-sm">{type.icon}</span>
                                                    {type.label}
                                                </div>
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">Start Date</Label>
                                <Input
                                    type="date"
                                    value={formData.start_date}
                                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                                    required
                                    className="bg-background"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label className="text-sm font-medium">End Date</Label>
                                <Input
                                    type="date"
                                    value={formData.end_date}
                                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                                    className="bg-background"
                                />
                            </div>
                            <div className="md:col-span-2 space-y-2">
                                <Label className="text-sm font-medium">Description</Label>
                                <Textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Additional details..."
                                    className="bg-background"
                                />
                            </div>
                            <Button type="submit" disabled={submitting} className="md:col-span-2 gap-2">
                                {submitting ? (
                                    <span className="material-symbols-outlined text-lg animate-spin">progress_activity</span>
                                ) : (
                                    <span className="material-symbols-outlined text-lg">add_task</span>
                                )}
                                Add Activity
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Calendar */}
                <Card className="lg:col-span-8">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
                        <CardTitle className="flex items-center gap-2 text-lg">
                            <span className="material-symbols-outlined text-primary">calendar_month</span>
                            {currentMonth.toLocaleDateString("en-IN", { month: "long", year: "numeric" })}
                        </CardTitle>
                        <div className="flex gap-2">
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                            >
                                <span className="material-symbols-outlined">chevron_left</span>
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setCurrentMonth(new Date())}
                            >
                                Today
                            </Button>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                            >
                                <span className="material-symbols-outlined">chevron_right</span>
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="p-4">
                        {/* Weekday headers */}
                        <div className="grid grid-cols-7 gap-1 mb-2">
                            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                                <div key={day} className="text-center text-xs font-semibold text-muted-foreground p-2">
                                    {day}
                                </div>
                            ))}
                        </div>
                        {/* Calendar grid */}
                        <div className="grid grid-cols-7 gap-1">
                            {days.map((day, index) => {
                                if (day === null) {
                                    return <div key={index} className="p-2 min-h-[80px]" />;
                                }
                                const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
                                const dayEvents = getEventsForDate(date);
                                const isToday = date.toDateString() === new Date().toDateString();

                                return (
                                    <div
                                        key={index}
                                        className={cn(
                                            "min-h-[80px] p-1.5 rounded-lg border transition-colors hover:bg-muted/50",
                                            isToday ? "border-primary bg-primary/5" : "border-transparent"
                                        )}
                                    >
                                        <div className={cn(
                                            "text-sm font-medium",
                                            isToday && "text-primary"
                                        )}>
                                            {day}
                                        </div>
                                        <div className="space-y-1 mt-1">
                                            {dayEvents.slice(0, 2).map((event) => {
                                                const activity = getActivityInfo(event.activity_type);
                                                return (
                                                    <div
                                                        key={event.id}
                                                        className={cn(
                                                            "text-[10px] px-1.5 py-0.5 rounded truncate text-white font-medium",
                                                            activity.color
                                                        )}
                                                        title={event.title}
                                                    >
                                                        {event.title}
                                                    </div>
                                                );
                                            })}
                                            {dayEvents.length > 2 && (
                                                <div className="text-[10px] text-muted-foreground font-medium">
                                                    +{dayEvents.length - 2} more
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>

                {/* Activity List */}
                <div className="lg:col-span-4 space-y-4">
                    <Card>
                        <CardContent className="p-5">
                            <h3 className="font-bold mb-4">Upcoming Activities</h3>
                            {events.length > 0 ? (
                                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                                    {events.slice(0, 8).map((event) => {
                                        const activity = getActivityInfo(event.activity_type);
                                        const statusInfo = getStatusInfo(event.status);

                                        return (
                                            <div key={event.id} className="p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors">
                                                <div className="flex items-start gap-3">
                                                    <div className={cn("size-8 rounded-lg flex items-center justify-center text-white shrink-0", activity.color)}>
                                                        <span className="material-symbols-outlined text-sm">{activity.icon}</span>
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="font-medium text-sm truncate">{event.title}</p>
                                                        <p className="text-xs text-muted-foreground">
                                                            {new Date(event.start_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}
                                                            {event.end_date !== event.start_date && (
                                                                <> - {new Date(event.end_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}</>
                                                            )}
                                                        </p>
                                                    </div>
                                                    <Badge className={cn("text-[10px] shrink-0", statusInfo.color)}>
                                                        {event.status_display || statusInfo.label}
                                                    </Badge>
                                                </div>
                                                <div className="flex justify-end gap-1 mt-2">
                                                    <Select
                                                        value={event.status}
                                                        onValueChange={(v) => handleStatusChange(event, v)}
                                                    >
                                                        <SelectTrigger className="h-7 text-xs w-24">
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            {STATUS_OPTIONS.map((s) => (
                                                                <SelectItem key={s.value} value={s.value} className="text-xs">
                                                                    {s.label}
                                                                </SelectItem>
                                                            ))}
                                                        </SelectContent>
                                                    </Select>
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-7 w-7 text-destructive hover:text-destructive"
                                                        onClick={() => handleDelete(event.id)}
                                                    >
                                                        <span className="material-symbols-outlined text-sm">delete</span>
                                                    </Button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    <span className="material-symbols-outlined text-4xl mb-2">event_busy</span>
                                    <p className="text-sm">No activities planned yet.</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Quick Stats */}
                    <Card>
                        <CardContent className="p-5">
                            <h3 className="font-bold mb-4">This Month</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="text-center">
                                    <p className="text-2xl font-bold text-primary">{events.filter(e => e.status === "completed").length}</p>
                                    <p className="text-xs text-muted-foreground">Completed</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold text-yellow-600">{events.filter(e => e.status === "in_progress").length}</p>
                                    <p className="text-xs text-muted-foreground">In Progress</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold text-blue-600">{events.filter(e => e.status === "planned").length}</p>
                                    <p className="text-xs text-muted-foreground">Planned</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold">{events.length}</p>
                                    <p className="text-xs text-muted-foreground">Total</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
