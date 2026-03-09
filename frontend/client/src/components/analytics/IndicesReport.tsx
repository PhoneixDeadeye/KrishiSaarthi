import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";
import { useTranslation } from "@/hooks/useTranslation";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { AWDResponse } from "@/types/field";
import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";

export function IndicesReport() {
    const { t } = useTranslation();
    const { token } = useAuth();
    const { selectedField } = useField();

    const [data, setData] = useState<AWDResponse | null>(null);
    const [error, setError] = useState<unknown>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!token) {
            setLoading(false);
            return;
        }

        const fetchData = async () => {
            try {
                let url = "/field/awd";
                if (selectedField) url += `?field_id=${selectedField.id}`;
                const json = await apiFetch<AWDResponse>(url);
                setData(json);
            } catch (err) {
                logger.error("AWD fetch error:", err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [token, selectedField]);

    if (loading) {
        return (
            <Card className="lg:col-span-2 h-full">
                <CardContent className="flex justify-center items-center h-full min-h-[200px]">
                    <span className="material-symbols-outlined text-3xl animate-spin text-primary">
                        progress_activity
                    </span>
                </CardContent>
            </Card>
        );
    }

    if (error || !data) {
        return (
            <Card className="lg:col-span-2 overflow-hidden h-full">
                <CardHeader className="border-b px-6 py-4">
                    <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">
                            show_chart
                        </span>
                        <CardTitle>{t("indices_report")}</CardTitle>
                    </div>
                </CardHeader>
                <CardContent className="p-8 text-center text-muted-foreground flex flex-col items-center justify-center h-[calc(100%-65px)]">
                    <span className="material-symbols-outlined text-4xl mb-2">
                        pin_drop
                    </span>
                    <p className="text-sm">
                        Save your field location to see AWD analytics
                    </p>
                </CardContent>
            </Card>
        );
    }

    const { awd_detected, cycles_count, dry_days_detected } = data;

    return (
        <Card className="lg:col-span-2 overflow-hidden h-full flex flex-col">
            <CardHeader className="border-b px-6 py-4">
                <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">
                        show_chart
                    </span>
                    <CardTitle>{t("indices_report")}</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="p-6 space-y-6 flex-1">
                {/* NDWI Chart */}
                <div className="h-48 bg-gradient-to-br from-primary/5 to-transparent rounded-lg p-4 relative border border-primary/10">
                    <div>
                        <h4 className="font-medium text-primary">NDWI Trend Analysis</h4>
                        <p className="text-sm text-muted-foreground">Last 7 days</p>
                    </div>
                    <div className="absolute bottom-4 left-4 right-4 h-24 flex items-end gap-2">
                        {[60, 45, 35, 40, 25, 30, 20].map((h, i) => (
                            <div
                                key={i}
                                className="flex-1 bg-primary/60 rounded-t-sm hover:bg-primary transition-colors cursor-pointer group relative"
                                style={{ height: `${100 - h}%` }}
                            >
                                <div className="opacity-0 group-hover:opacity-100 absolute -top-8 left-1/2 -translate-x-1/2 bg-popover text-popover-foreground text-xs px-2 py-1 rounded shadow-sm whitespace-nowrap z-10 transition-opacity">
                                    Value: {(100 - h) / 100}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="absolute top-4 right-4 text-sm font-medium text-primary bg-background/50 px-2 py-1 rounded backdrop-blur-sm">
                        Current: 0.75
                    </div>
                </div>

                {/* AWD Stats */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="p-4 text-center rounded-lg border bg-card/50">
                        <p className="text-sm text-muted-foreground">AWD Status</p>
                        <p
                            className={cn(
                                "text-xl font-bold mt-1",
                                awd_detected ? "text-amber-600" : "text-primary"
                            )}
                        >
                            {awd_detected ? "Detected" : "Not Detected"}
                        </p>
                    </div>
                    <div className="p-4 text-center rounded-lg border bg-card/50">
                        <p className="text-sm text-muted-foreground">Cycle Count</p>
                        <p className="text-xl font-bold text-blue-600 mt-1">
                            {cycles_count} cycles
                        </p>
                    </div>
                    <div className="p-4 text-center rounded-lg border bg-card/50">
                        <p className="text-sm text-muted-foreground">Dry Days</p>
                        <p className="text-xl font-bold text-amber-600 mt-1">
                            {dry_days_detected} days
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
