import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Star, ArrowRight, Leaf, AlertTriangle, Lightbulb, CheckCircle } from "lucide-react";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { logger } from "@/lib/logger";

interface Suggestion {
    crop: string;
    score: number;
    rating: { stars: number; label: string };
    reasons: string[];
    season: string;
    benefits: { nitrogen_fix?: boolean; soil_structure?: string; pest_break?: boolean };
}

interface TimelineItem {
    season: string;
    year: number;
    crop: string;
    status: string;
    score?: number;
    icon: string;
}

interface SoilTip {
    type: string;
    icon: string;
    text: string;
}

interface RotationData {
    field_id: number;
    field_name: string;
    current_crop: string;
    current_season: string;
    crop_history: { year: number; season: string; crop: string }[];
    suggestions: Suggestion[];
    timeline: TimelineItem[];
    soil_health_tips: SoilTip[];
}

export function RotationPlanner() {
    const { selectedField } = useField();
    const [data, setData] = useState<RotationData | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (selectedField) {
            fetchRotation();
        }
    }, [selectedField]);

    const fetchRotation = async () => {
        if (!selectedField) return;
        setLoading(true);
        try {
            const result = await apiFetch(`/planning/rotation?field_id=${selectedField.id}`) as RotationData;
            setData(result);
        } catch (error) {
            logger.error("Failed to fetch rotation plan:", error);
        } finally {
            setLoading(false);
        }
    };

    if (!selectedField) {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="py-12 text-center text-muted-foreground">
                        <RefreshCw className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Select a field to view rotation suggestions</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <RefreshCw className="h-6 w-6 text-green-500" />
                        Crop Rotation Planner
                    </h1>
                    <p className="text-muted-foreground">
                        AI suggestions for {data?.field_name || selectedField.name}
                    </p>
                </div>
                <Button onClick={fetchRotation} variant="outline" disabled={loading}>
                    {loading ? "Loading..." : "Refresh"}
                </Button>
            </div>

            {loading ? (
                <Card><CardContent className="py-12 text-center">Analyzing rotation options...</CardContent></Card>
            ) : data ? (
                <>
                    {/* Current Status */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Card className="bg-green-50 dark:bg-green-950/20 border-green-200">
                            <CardContent className="p-4 text-center">
                                <p className="text-sm text-muted-foreground">Current Crop</p>
                                <p className="text-2xl font-bold text-green-700 dark:text-green-400">{data.current_crop}</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4 text-center">
                                <p className="text-sm text-muted-foreground">Current Season</p>
                                <p className="text-2xl font-bold">{data.current_season}</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="p-4 text-center">
                                <p className="text-sm text-muted-foreground">Best Next Crop</p>
                                <p className="text-2xl font-bold text-blue-600">{data.suggestions[0]?.crop || '-'}</p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Rotation Timeline */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Suggested Rotation Timeline</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center gap-2 overflow-x-auto pb-2">
                                {data.timeline.map((item, idx) => (
                                    <div key={idx} className="flex items-center">
                                        <div className={`p-4 rounded-lg min-w-[120px] text-center ${item.status === 'current'
                                            ? 'bg-green-100 dark:bg-green-900/30 border-2 border-green-500'
                                            : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200'
                                            }`}>
                                            <span className="text-2xl">{item.icon}</span>
                                            <p className="font-semibold mt-1">{item.crop}</p>
                                            <p className="text-xs text-muted-foreground">{item.season} {item.year}</p>
                                            {item.status === 'current' && (
                                                <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded mt-1 inline-block">Now</span>
                                            )}
                                        </div>
                                        {idx < data.timeline.length - 1 && (
                                            <ArrowRight className="h-5 w-5 mx-2 text-muted-foreground flex-shrink-0" />
                                        )}
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Suggestions */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base flex items-center gap-2">
                                <Leaf className="h-4 w-4" />
                                Top Rotation Suggestions
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {data.suggestions.map((sug, idx) => (
                                    <div key={idx} className={`p-4 rounded-lg border relative ${idx === 0
                                        ? 'border-green-300 bg-green-50 dark:bg-green-950/20 shadow-md transform scale-[1.02] transition-transform'
                                        : 'border-gray-200 hover:border-green-200 transition-colors'
                                        }`}>
                                        {idx === 0 && (
                                            <div className="absolute -top-3 -right-3 bg-green-500 text-white text-xs px-2 py-1 rounded-full shadow-sm flex items-center gap-1">
                                                <Star className="h-3 w-3 fill-white" />
                                                Top Pick
                                            </div>
                                        )}
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-semibold text-lg">{sug.crop}</span>
                                            <div className="flex flex-col items-end">
                                                <span className="text-sm font-bold text-green-600">{sug.score}% Match</span>
                                                <div className="flex">
                                                    {[...Array(5)].map((_, i) => (
                                                        <Star key={i} className={`h-3 w-3 ${i < sug.rating.stars ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground mb-3 font-medium bg-muted/50 inline-block px-2 py-1 rounded">
                                            Best Season: {sug.season}
                                        </p>
                                        <ul className="space-y-1.5 mb-3">
                                            {sug.reasons.slice(0, 3).map((r, i) => (
                                                <li key={i} className="text-xs flex items-start gap-1.5 text-muted-foreground">
                                                    <CheckCircle className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
                                                    <span>{r}</span>
                                                </li>
                                            ))}
                                        </ul>
                                        <div className="flex flex-wrap gap-1 mt-auto">
                                            {sug.benefits.nitrogen_fix && (
                                                <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded border border-blue-200">
                                                    🌿 Nitrogen Fixer
                                                </span>
                                            )}
                                            {sug.benefits.pest_break && (
                                                <span className="text-[10px] bg-orange-100 text-orange-700 px-2 py-0.5 rounded border border-orange-200">
                                                    🛡️ Pest Break
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Soil Health Tips */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base flex items-center gap-2">
                                <Lightbulb className="h-4 w-4" />
                                Soil Health Tips
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {data.soil_health_tips.map((tip, idx) => (
                                    <div key={idx} className={`p-3 rounded-lg flex items-start gap-3 ${tip.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                                        'bg-blue-50 border border-blue-200'
                                        }`}>
                                        <span className="text-xl">{tip.icon}</span>
                                        <p className="text-sm">{tip.text}</p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Crop History */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Crop History</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2">
                                {data.crop_history.map((h, idx) => (
                                    <div key={idx} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-sm">
                                        {h.season} {h.year}: <span className="font-medium">{h.crop}</span>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </>
            ) : (
                <Card><CardContent className="py-12 text-center text-muted-foreground">Failed to load. Click Refresh.</CardContent></Card>
            )}
        </div>
    );
}
