import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface HealthGaugeProps {
    score: number;
    rating: string;
    title: string;
    accentColor?: string;
    className?: string;
    indicators?: { label: string; icon: string }[];
}

export function HealthGauge({
    score,
    rating,
    title,
    accentColor = "text-primary",
    className,
    indicators,
}: HealthGaugeProps) {
    return (
        <Card className={cn("h-full", className)}>
            <CardContent className="p-6 flex items-center gap-6 h-full">
                <div className="relative size-24 shrink-0">
                    <svg
                        className="size-full -rotate-90"
                        viewBox="0 0 36 36"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            className="text-muted"
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="3"
                        />
                        <path
                            className={accentColor}
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="currentColor"
                            strokeDasharray={`${score}, 100`}
                            strokeLinecap="round"
                            strokeWidth="3"
                        />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center flex-col">
                        <span className="text-xl font-bold">{score}%</span>
                    </div>
                </div>
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                        <h4 className="text-lg font-bold">{title}</h4>
                        <span
                            className={cn(
                                "text-xs font-bold px-2 py-1 rounded",
                                rating === "Excellent" && "bg-primary/20 text-primary",
                                rating === "Good" &&
                                "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400",
                                rating === "Fair" &&
                                "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400",
                                !["Excellent", "Good", "Fair"].includes(rating) &&
                                "bg-muted text-muted-foreground"
                            )}
                        >
                            {rating}
                        </span>
                    </div>
                    {indicators && indicators.length > 0 && (
                        <div className="space-y-1 mt-2">
                            {indicators.map((ind, idx) => (
                                <div key={idx} className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <span className="material-symbols-outlined text-base">
                                        {ind.icon}
                                    </span>
                                    <span>{ind.label}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
