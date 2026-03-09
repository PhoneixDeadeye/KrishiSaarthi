import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";

interface WeatherData {
    temp_max: number | null;
    temp_min: number | null;
    rain_chance: number;
    rain_mm: number;
    humidity: number | null;
    description: string;
    icon: string;
}

interface Recommendation {
    action: string;
    icon: string;
    confidence: number;
    reason: string;
}

interface ScheduleDay {
    date: string;
    day_of_week: string;
    weather: WeatherData;
    recommendation: Recommendation;
    irrigated: boolean;
    log: unknown | null;
}

interface ScheduleData {
    field_id: number;
    field_name: string;
    crop_type: string;
    schedule: ScheduleDay[];
    summary: {
        water_used_this_week: number;
        irrigation_count: number;
        next_recommended_irrigation: string | null;
    };
}

interface IrrigationSource {
    value: string;
    label: string;
}

export function IrrigationScheduler() {
    const { selectedField } = useField();
    const [schedule, setSchedule] = useState<ScheduleData | null>(null);
    const [sources, setSources] = useState<IrrigationSource[]>([]);
    const [loading, setLoading] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [selectedDate, setSelectedDate] = useState<string>("");

    const [logForm, setLogForm] = useState({
        water_amount: "",
        duration_minutes: "",
        source: "other",
        notes: ""
    });

    useEffect(() => {
        if (selectedField) {
            fetchSchedule();
            fetchSources();
        }
    }, [selectedField]);

    const fetchSchedule = async () => {
        if (!selectedField) return;
        setLoading(true);
        try {
            const data = await apiFetch(`/field/irrigation-schedule?field_id=${selectedField.id}`) as ScheduleData;
            setSchedule(data);
        } catch (error) {
            logger.error("Failed to fetch irrigation schedule:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchSources = async () => {
        try {
            const data = await apiFetch("/field/irrigation-logs") as { sources?: IrrigationSource[] };
            setSources(data.sources || []);
        } catch (error) {
            logger.error("Failed to fetch sources:", error);
        }
    };

    const handleLogIrrigation = async () => {
        if (!selectedField || !selectedDate) return;

        try {
            await apiFetch("/field/irrigation-logs", {
                method: "POST",
                body: JSON.stringify({
                    field_id: selectedField.id,
                    date: selectedDate,
                    water_amount: logForm.water_amount ? parseFloat(logForm.water_amount) : null,
                    duration_minutes: logForm.duration_minutes ? parseInt(logForm.duration_minutes) : null,
                    source: logForm.source,
                    notes: logForm.notes
                })
            });

            setDialogOpen(false);
            setLogForm({ water_amount: "", duration_minutes: "", source: "other", notes: "" });
            fetchSchedule();
        } catch (error) {
            logger.error("Failed to log irrigation:", error);
        }
    };

    const getWeatherIcon = (rainChance: number) => {
        if (rainChance >= 70) return "rainy";
        if (rainChance >= 30) return "cloud";
        return "wb_sunny";
    };

    const getRecommendationStyle = (action: string) => {
        switch (action) {
            case 'irrigate': return { bg: 'bg-blue-500/10', text: 'text-blue-600', border: 'border-blue-500/30' };
            case 'skip': return { bg: 'bg-primary/10', text: 'text-primary', border: 'border-primary/30' };
            case 'monitor': return { bg: 'bg-amber-500/10', text: 'text-amber-600', border: 'border-amber-500/30' };
            case 'done': return { bg: 'bg-gray-500/10', text: 'text-gray-500', border: 'border-gray-500/30' };
            default: return { bg: 'bg-muted', text: 'text-muted-foreground', border: 'border-muted' };
        }
    };

    if (!selectedField) {
        return (
            <Card className="text-center">
                <CardContent className="p-12 flex flex-col items-center">
                    <span className="material-symbols-outlined text-5xl text-muted-foreground mb-4">water_drop</span>
                    <p className="text-muted-foreground">Select a field to view irrigation schedule</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500 pb-10">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <span className="material-symbols-outlined text-blue-500">water_drop</span>
                        Smart Irrigation
                    </h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        AI-powered recommendations for {schedule?.field_name || selectedField.name}
                    </p>
                </div>
                <Button onClick={fetchSchedule} variant="outline" disabled={loading} className="gap-2">
                    <span className={cn("material-symbols-outlined text-lg", loading && "animate-spin")}>
                        {loading ? "progress_activity" : "refresh"}
                    </span>
                    {loading ? "Loading" : "Refresh"}
                </Button>
            </div>

            {/* Summary Cards */}
            {schedule && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <Card>
                        <CardContent className="p-5">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Water Used (7 days)</p>
                                    <p className="text-2xl font-bold mt-1 text-blue-600">{schedule.summary.water_used_this_week.toFixed(0)}L</p>
                                </div>
                                <div className="size-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500">
                                    <span className="material-symbols-outlined">water_drop</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-5">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Irrigations This Week</p>
                                    <p className="text-2xl font-bold mt-1 text-primary">{schedule.summary.irrigation_count}</p>
                                </div>
                                <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                                    <span className="material-symbols-outlined">check_circle</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-5">
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-sm text-muted-foreground">Next Recommended</p>
                                    <p className="text-2xl font-bold mt-1">
                                        {schedule.summary.next_recommended_irrigation
                                            ? new Date(schedule.summary.next_recommended_irrigation).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric' })
                                            : 'None soon'}
                                    </p>
                                </div>
                                <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-600">
                                    <span className="material-symbols-outlined">event</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* 7-Day Schedule */}
            <Card>
                <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-4 border-b">
                    <span className="material-symbols-outlined text-primary">calendar_month</span>
                    <CardTitle className="text-lg">7-Day Irrigation Schedule</CardTitle>
                </CardHeader>
                <CardContent className="p-5">
                    {loading ? (
                        <div className="text-center py-8">
                            <span className="material-symbols-outlined text-4xl animate-spin text-primary">progress_activity</span>
                        </div>
                    ) : schedule ? (
                        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
                            {schedule.schedule.map((day) => {
                                const style = getRecommendationStyle(day.recommendation.action);
                                return (
                                    <div
                                        key={day.date}
                                        className={cn(
                                            "p-3 rounded-lg border-2 transition-all hover:shadow-md",
                                            style.bg, style.border
                                        )}
                                    >
                                        {/* Day Header */}
                                        <div className="text-center mb-2">
                                            <p className={cn("font-semibold text-sm", style.text)}>{day.day_of_week.slice(0, 3)}</p>
                                            <p className="text-xs text-muted-foreground">
                                                {new Date(day.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                                            </p>
                                        </div>

                                        {/* Weather */}
                                        <div className="flex items-center justify-center gap-1 mb-2">
                                            <span className={cn(
                                                "material-symbols-outlined text-lg",
                                                day.weather.rain_chance >= 70 ? "text-blue-500" :
                                                    day.weather.rain_chance >= 30 ? "text-gray-400" : "text-amber-500"
                                            )}>
                                                {getWeatherIcon(day.weather.rain_chance)}
                                            </span>
                                            <span className="text-sm font-medium">{day.weather.temp_max}°</span>
                                        </div>

                                        {/* Rain Chance */}
                                        <div className="text-center mb-2">
                                            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
                                                <span className="material-symbols-outlined text-xs">rainy</span>
                                                <span>{day.weather.rain_chance}%</span>
                                            </div>
                                        </div>

                                        {/* Recommendation */}
                                        <div className="text-center mb-2">
                                            <span className="text-xl">{day.recommendation.icon}</span>
                                            <p className={cn("text-xs mt-1 font-medium capitalize", style.text)}>
                                                {day.recommendation.action}
                                            </p>
                                        </div>

                                        {/* Log Button */}
                                        {!day.irrigated && day.recommendation.action !== 'done' && (
                                            <Dialog open={dialogOpen && selectedDate === day.date} onOpenChange={(open) => {
                                                setDialogOpen(open);
                                                if (open) setSelectedDate(day.date);
                                            }}>
                                                <DialogTrigger asChild>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="w-full mt-2 h-7 text-xs gap-1"
                                                        onClick={() => setSelectedDate(day.date)}
                                                    >
                                                        <span className="material-symbols-outlined text-sm">add</span>
                                                        Log
                                                    </Button>
                                                </DialogTrigger>
                                                <DialogContent>
                                                    <DialogHeader>
                                                        <DialogTitle className="flex items-center gap-2">
                                                            <span className="material-symbols-outlined text-blue-500">water_drop</span>
                                                            Log Irrigation - {day.day_of_week}
                                                        </DialogTitle>
                                                    </DialogHeader>
                                                    <div className="space-y-4 py-4">
                                                        <div className="grid grid-cols-2 gap-4">
                                                            <div className="space-y-2">
                                                                <Label className="text-sm font-medium">Water Amount (L)</Label>
                                                                <Input
                                                                    type="number"
                                                                    placeholder="e.g. 500"
                                                                    value={logForm.water_amount}
                                                                    onChange={(e) => setLogForm({ ...logForm, water_amount: e.target.value })}
                                                                    className="bg-background"
                                                                />
                                                            </div>
                                                            <div className="space-y-2">
                                                                <Label className="text-sm font-medium">Duration (minutes)</Label>
                                                                <Input
                                                                    type="number"
                                                                    placeholder="e.g. 30"
                                                                    value={logForm.duration_minutes}
                                                                    onChange={(e) => setLogForm({ ...logForm, duration_minutes: e.target.value })}
                                                                    className="bg-background"
                                                                />
                                                            </div>
                                                        </div>

                                                        <div className="space-y-2">
                                                            <Label className="text-sm font-medium">Water Source</Label>
                                                            <Select value={logForm.source} onValueChange={(v) => setLogForm({ ...logForm, source: v })}>
                                                                <SelectTrigger className="bg-background">
                                                                    <SelectValue />
                                                                </SelectTrigger>
                                                                <SelectContent>
                                                                    {sources.map(s => (
                                                                        <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                                                                    ))}
                                                                </SelectContent>
                                                            </Select>
                                                        </div>

                                                        <div className="space-y-2">
                                                            <Label className="text-sm font-medium">Notes</Label>
                                                            <Textarea
                                                                placeholder="Any observations..."
                                                                value={logForm.notes}
                                                                onChange={(e) => setLogForm({ ...logForm, notes: e.target.value })}
                                                                className="bg-background"
                                                            />
                                                        </div>

                                                        <Button onClick={handleLogIrrigation} className="w-full gap-2">
                                                            <span className="material-symbols-outlined text-lg">check_circle</span>
                                                            Save Irrigation Log
                                                        </Button>
                                                    </div>
                                                </DialogContent>
                                            </Dialog>
                                        )}

                                        {day.irrigated && (
                                            <div className="mt-2 text-center">
                                                <span className="inline-flex items-center gap-1 text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                                                    <span className="material-symbols-outlined text-xs">check</span>
                                                    Logged
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-muted-foreground">
                            No schedule data available
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Quick Tips */}
            <Card>
                <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-4 border-b">
                    <span className="material-symbols-outlined text-amber-500">tips_and_updates</span>
                    <CardTitle className="text-lg">Irrigation Tips for {schedule?.crop_type || selectedField.cropType}</CardTitle>
                </CardHeader>
                <CardContent className="p-5">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                            <span className="material-symbols-outlined text-blue-500">schedule</span>
                            <p className="text-sm text-muted-foreground">Best time: Early morning (6-8 AM) or evening (5-7 PM)</p>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                            <span className="material-symbols-outlined text-amber-500">thermostat</span>
                            <p className="text-sm text-muted-foreground">Avoid irrigation during peak heat (12-3 PM)</p>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                            <span className="material-symbols-outlined text-blue-500">water_drop</span>
                            <p className="text-sm text-muted-foreground">Deep watering is better than frequent light watering</p>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                            <span className="material-symbols-outlined text-gray-500">rainy</span>
                            <p className="text-sm text-muted-foreground">Skip irrigation if rain expected within 24 hours</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
