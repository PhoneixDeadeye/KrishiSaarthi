"use client";

import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import clsx from "clsx";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { useTranslation } from "@/hooks/useTranslation";
import { useTheme } from "@/components/layout/ThemeProvider";
import { ExportButton } from "@/components/common/ExportButton";
import { useVoiceRecording } from "@/hooks/useVoiceRecording";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import "./FieldLog.css";

type ActivityType = "Watering" | "Fertilizer" | "Sowing" | "Pesticide" | "Harvest" | "Other";

interface LogEntry {
  id: number;
  date: string;
  activity: ActivityType;
  details: string;
}

interface AlertEntry {
  id: number;
  date: string;
  message: string;
  is_read: boolean;
}

const activityConfig: Record<ActivityType, { icon: string; color: string; bg: string }> = {
  Watering: { icon: "water_drop", color: "text-blue-600", bg: "bg-blue-100" },
  Fertilizer: { icon: "inventory_2", color: "text-amber-600", bg: "bg-amber-100" },
  Sowing: { icon: "grass", color: "text-primary", bg: "bg-primary/20" },
  Pesticide: { icon: "bug_report", color: "text-red-600", bg: "bg-red-100" },
  Harvest: { icon: "agriculture", color: "text-orange-600", bg: "bg-orange-100" },
  Other: { icon: "eco", color: "text-muted-foreground", bg: "bg-muted" },
};

export function FieldLog() {
  const { token } = useAuth();
  const { t } = useTranslation();
  const { resolvedTheme } = useTheme();
  const { selectedField } = useField();

  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [activity, setActivity] = useState<ActivityType>("Watering");
  const [details, setDetails] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [alerts, setAlerts] = useState<AlertEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const { isRecording, startRecording, stopRecording, transcript, setTranscript } = useVoiceRecording();

  useEffect(() => {
    if (transcript) setDetails(transcript);
  }, [transcript]);

  useEffect(() => {
    if (!showModal) {
      setTranscript("");
      if (isRecording) stopRecording();
    }
  }, [showModal]);

  useEffect(() => {
    if (!token) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        let logsEndpoint = '/field/logs';
        let alertsEndpoint = '/field/alerts';

        if (selectedField) {
          logsEndpoint += `?field_id=${selectedField.id}`;
          alertsEndpoint += `?field_id=${selectedField.id}`;
        }

        const [logsData, alertsData] = await Promise.all([
          apiFetch<LogEntry[]>(logsEndpoint, { headers: { Authorization: `Token ${token}` } }),
          apiFetch<AlertEntry[]>(alertsEndpoint, { headers: { Authorization: `Token ${token}` } }),
        ]);

        setLogs(logsData);
        setAlerts(alertsData);
      } catch (error) {
        console.error("Error fetching field data:", error);
        toast({ title: "Error fetching data", variant: "destructive" });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token, selectedField]);

  const handleAddLog = async () => {
    if (!details.trim()) {
      toast({ title: "Missing details", description: "Please fill in activity details.", variant: "destructive" });
      return;
    }
    if (!token || !selectedDate) return;

    setSubmitting(true);
    try {
      const formattedDate = selectedDate.toISOString().split("T")[0];
      const newLog = await apiFetch<LogEntry>('/field/logs', {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Token ${token}` },
        body: JSON.stringify({ date: formattedDate, activity, details, field_id: selectedField?.id }),
      });

      setLogs([...logs, newLog]);

      let alertsEndpoint = '/field/alerts';
      if (selectedField) alertsEndpoint += `?field_id=${selectedField.id}`;
      const alertsData = await apiFetch<AlertEntry[]>(alertsEndpoint, { headers: { Authorization: `Token ${token}` } });
      setAlerts(alertsData);

      setActivity("Watering");
      setDetails("");
      setShowModal(false);
      toast({ title: "Log saved", description: "Activity recorded successfully." });
    } catch (error) {
      console.error("Error saving log:", error);
      toast({ title: "Failed to save", variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const getTileContent = (date: Date) => {
    const dateStr = date.toISOString().split("T")[0];
    const dayLogs = logs.filter((log) => log.date === dateStr);
    const dayAlerts = alerts.filter((alert) => alert.date === dateStr);

    if (dayLogs.length === 0 && dayAlerts.length === 0) return null;

    return (
      <div className="mt-1 flex flex-col gap-0.5">
        {dayLogs.slice(0, 2).map((log) => (
          <div key={`log-${log.id}`} className={cn("text-[10px] rounded px-1 py-0.5 truncate flex items-center gap-0.5", activityConfig[log.activity].bg, activityConfig[log.activity].color)} title={log.details}>
            <span className="material-symbols-outlined text-[10px]">{activityConfig[log.activity].icon}</span>
            {log.activity}
          </div>
        ))}
        {dayAlerts.slice(0, 1).map((alert) => (
          <div key={`alert-${alert.id}`} className="text-[10px] text-red-600 truncate flex items-center gap-0.5" title={alert.message}>
            <span className="material-symbols-outlined text-[10px]">warning</span>
            Alert
          </div>
        ))}
      </div>
    );
  };

  const getDetailsPlaceholder = () => {
    switch (activity) {
      case "Watering": return "Enter amount (liters) or irrigation type...";
      case "Fertilizer": return "Enter type and quantity (kg)...";
      case "Sowing": return "Enter seeds per row or area...";
      case "Pesticide": return "Enter type and dosage...";
      case "Harvest": return "Enter estimated yield...";
      default: return "Enter notes...";
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">edit_calendar</span>
            {t("field_log")}
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Track your farm activities</p>
        </div>
        <ExportButton
          data={logs}
          filename="field_logs"
          title="Field Activity Log"
          columns={[
            { header: "Date", accessorKey: "date" },
            { header: "Activity", accessorKey: "activity" },
            { header: "Details", accessorKey: "details" }
          ]}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Calendar Section */}
        <Card className="lg:col-span-3">
          <CardContent className="p-4">
            {loading ? (
              <div className="h-[500px] flex items-center justify-center">
                <span className="material-symbols-outlined text-4xl animate-spin text-primary">progress_activity</span>
              </div>
            ) : (
              <Calendar
                onClickDay={(date) => { setSelectedDate(date); setShowModal(true); }}
                tileContent={({ date, view }) => view === "month" && getTileContent(date)}
                className={clsx("w-full border-none text-foreground bg-card", resolvedTheme === 'dark' ? 'react-calendar-dark' : '')}
              />
            )}
          </CardContent>
        </Card>

        {/* Alerts Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-4 border-b">
              <span className="material-symbols-outlined text-amber-500">warning</span>
              <CardTitle className="text-lg">Alerts</CardTitle>
            </CardHeader>
            <CardContent className="p-4 max-h-80 overflow-y-auto">
              {alerts.length === 0 ? (
                <p className="text-muted-foreground text-sm text-center py-8">No pending alerts</p>
              ) : (
                <div className="space-y-3">
                  {alerts.slice(0, 5).map(alert => (
                    <div key={alert.id} className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                      <p className="text-sm font-medium text-red-600 dark:text-red-400">{alert.message}</p>
                      <p className="text-xs text-muted-foreground mt-1">{alert.date}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardContent className="p-4">
              <h4 className="font-medium text-sm mb-3">This Month</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(activityConfig).slice(0, 4).map(([type, config]) => {
                  const count = logs.filter(l => l.activity === type).length;
                  return (
                    <div key={type} className="p-2 rounded-lg bg-muted/50 text-center">
                      <span className={cn("material-symbols-outlined text-lg", config.color)}>{config.icon}</span>
                      <p className="text-lg font-bold">{count}</p>
                      <p className="text-[10px] text-muted-foreground">{type}</p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modal */}
      {showModal && selectedDate && (
        <div className="fixed inset-0 z-50 flex justify-center items-center bg-black/50 animate-in fade-in duration-200">
          <Card className="w-full max-w-md animate-in zoom-in-95 duration-200 mx-4">
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">add_task</span>
                  Log Activity
                </h3>
                <button onClick={() => setShowModal(false)} className="p-1 hover:bg-muted rounded">
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              <p className="text-sm text-muted-foreground">{selectedDate.toDateString()}</p>

              {/* Activity Type */}
              <div>
                <label className="block text-sm font-medium mb-2">Activity Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {(Object.keys(activityConfig) as ActivityType[]).map((type) => (
                    <button
                      key={type}
                      onClick={() => setActivity(type)}
                      className={cn(
                        "p-2 rounded-lg border text-center transition-all",
                        activity === type ? "border-primary bg-primary/10" : "border-border hover:bg-muted"
                      )}
                    >
                      <span className={cn("material-symbols-outlined text-lg", activityConfig[type].color)}>{activityConfig[type].icon}</span>
                      <p className="text-xs mt-1">{type}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Details */}
              <div>
                <label className="block text-sm font-medium mb-2">Details</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="flex-1 p-3 border rounded-lg bg-background text-sm"
                    placeholder={getDetailsPlaceholder()}
                    value={details}
                    onChange={(e) => setDetails(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={cn(
                      "p-3 rounded-lg border transition",
                      isRecording ? "bg-red-500/10 text-red-600 border-red-500/30 animate-pulse" : "hover:bg-muted"
                    )}
                  >
                    <span className="material-symbols-outlined">{isRecording ? "mic_off" : "mic"}</span>
                  </button>
                </div>
                {isRecording && (
                  <p className="text-xs text-red-500 mt-1 animate-pulse">Listening... {transcript && `"${transcript}"`}</p>
                )}
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-2">
                <button className="px-4 py-2 rounded-lg hover:bg-muted transition" onClick={() => setShowModal(false)} disabled={submitting}>
                  Cancel
                </button>
                <button className="bg-primary text-primary-foreground px-4 py-2 rounded-lg flex items-center gap-2" onClick={handleAddLog} disabled={submitting}>
                  {submitting && <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>}
                  Save
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
