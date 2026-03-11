// src/components/field/FieldAlerts.tsx

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";

type Alert = {
    id: number;
    field_id: number | null;
    log: number | null;
    date: string;
    message: string;
    is_read: boolean;
    created_at: string;
};

const ALERT_ICONS: Record<string, { icon: string; color: string }> = {
    Water: { icon: "water_drop", color: "text-blue-500 bg-blue-500/10" },
    Fertilizer: { icon: "compost", color: "text-green-500 bg-green-500/10" },
    Pesticide: { icon: "bug_report", color: "text-amber-500 bg-amber-500/10" },
    irrigation: { icon: "waves", color: "text-cyan-500 bg-cyan-500/10" },
    Check: { icon: "visibility", color: "text-teal-500 bg-teal-500/10" },
    Reminder: { icon: "notifications", color: "text-primary bg-primary/10" },
    default: { icon: "warning", color: "text-orange-500 bg-orange-500/10" },
};

function getAlertStyle(message: string) {
    for (const key of Object.keys(ALERT_ICONS)) {
        if (message.toLowerCase().includes(key.toLowerCase())) {
            return ALERT_ICONS[key];
        }
    }
    return ALERT_ICONS.default;
}

export function FieldAlerts() {
    const { token } = useAuth();
    const { selectedField } = useField();
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchAlerts = async () => {
        if (!token) return;
        setLoading(true);
        try {
            const params = selectedField ? `?field_id=${selectedField.id}` : "";
            const data = await apiFetch<Alert[]>(`/field/alerts${params}`);
            setAlerts(data);
        } catch (err) {
            logger.error("Failed to fetch alerts:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();
    }, [token, selectedField]);

    const markAsRead = async (alertId: number) => {
        try {
            await apiFetch(`/field/alerts/${alertId}`, { method: "PATCH" });
            setAlerts((prev) =>
                prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a))
            );
        } catch (err) {
            logger.error("Failed to mark alert as read:", err);
        }
    };

    const markAllAsRead = async () => {
        try {
            await apiFetch(`/field/alerts/all`, { method: "PATCH" });
            setAlerts((prev) => prev.map((a) => ({ ...a, is_read: true })));
        } catch (err) {
            logger.error("Failed to mark all alerts as read:", err);
        }
    };

    const unreadCount = alerts.filter((a) => !a.is_read).length;
    const sortedAlerts = [...alerts].sort(
        (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
    );

    if (loading) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-4xl animate-spin text-primary">
                        progress_activity
                    </span>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Field Alerts</h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        {selectedField
                            ? `Alerts for ${selectedField.name}`
                            : "Activity reminders and notifications"}
                    </p>
                </div>
                <div className="flex gap-2">
                    {unreadCount > 0 && (
                        <Button variant="outline" onClick={markAllAsRead} className="gap-2">
                            <span className="material-symbols-outlined text-lg">done_all</span>
                            Mark All Read
                        </Button>
                    )}
                    <Button onClick={fetchAlerts} variant="outline" className="gap-2">
                        <span className="material-symbols-outlined text-lg">refresh</span>
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold">{alerts.length}</p>
                        <p className="text-sm text-muted-foreground">Total Alerts</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold text-destructive">{unreadCount}</p>
                        <p className="text-sm text-muted-foreground">Unread</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold text-primary">
                            {alerts.filter((a) => a.is_read).length}
                        </p>
                        <p className="text-sm text-muted-foreground">Completed</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-5 text-center">
                        <p className="text-2xl font-bold text-amber-500">
                            {
                                alerts.filter(
                                    (a) => new Date(a.date) <= new Date() && !a.is_read
                                ).length
                            }
                        </p>
                        <p className="text-sm text-muted-foreground">Overdue</p>
                    </CardContent>
                </Card>
            </div>

            {/* Alerts List */}
            {alerts.length === 0 ? (
                <Card className="text-center">
                    <CardContent className="p-12 space-y-4 flex flex-col items-center">
                        <div className="size-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                            <span className="material-symbols-outlined text-3xl text-primary">
                                notifications_off
                            </span>
                        </div>
                        <h3 className="text-lg font-bold">No Alerts</h3>
                        <p className="text-muted-foreground text-sm max-w-sm mx-auto">
                            You're all caught up! Alerts will appear here based on your field
                            activities.
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-3">
                    {sortedAlerts.map((alert) => {
                        const style = getAlertStyle(alert.message);
                        const isOverdue =
                            new Date(alert.date) <= new Date() && !alert.is_read;
                        const alertDate = new Date(alert.date);

                        return (
                            <Card
                                key={alert.id}
                                className={cn(
                                    "transition-all hover:shadow-md",
                                    alert.is_read && "opacity-60"
                                )}
                            >
                                <CardContent className="p-4">
                                    <div className="flex items-start gap-4">
                                        {/* Icon */}
                                        <div
                                            className={cn(
                                                "size-12 rounded-xl flex items-center justify-center flex-shrink-0",
                                                style.color
                                            )}
                                        >
                                            <span className="material-symbols-outlined text-xl">
                                                {style.icon}
                                            </span>
                                        </div>

                                        {/* Content */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-start justify-between gap-2">
                                                <div>
                                                    <p
                                                        className={cn(
                                                            "font-medium",
                                                            alert.is_read && "text-muted-foreground"
                                                        )}
                                                    >
                                                        {alert.message}
                                                    </p>
                                                    <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                                                        <span className="material-symbols-outlined text-sm">
                                                            calendar_today
                                                        </span>
                                                        {alertDate.toLocaleDateString("en-IN", {
                                                            day: "numeric",
                                                            month: "short",
                                                            year: "numeric",
                                                        })}
                                                    </div>
                                                </div>

                                                {/* Status Badges */}
                                                <div className="flex items-center gap-2">
                                                    {isOverdue && (
                                                        <Badge className="bg-destructive/10 text-destructive border-0">
                                                            Overdue
                                                        </Badge>
                                                    )}
                                                    {!alert.is_read && !isOverdue && (
                                                        <Badge className="bg-primary/10 text-primary border-0">
                                                            Pending
                                                        </Badge>
                                                    )}
                                                    {alert.is_read && (
                                                        <Badge
                                                            variant="outline"
                                                            className="text-muted-foreground"
                                                        >
                                                            Done
                                                        </Badge>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Action */}
                                        {!alert.is_read && (
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-primary hover:bg-primary/10"
                                                onClick={() => markAsRead(alert.id)}
                                            >
                                                <span className="material-symbols-outlined">
                                                    check_circle
                                                </span>
                                            </Button>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
