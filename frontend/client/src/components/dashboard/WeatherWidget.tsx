import { Card, CardContent } from "@/components/ui/card";
import { Loader2, CloudOff } from "lucide-react";

interface WeatherData {
    temp: number | string;
    condition: string;
    humidity: number;
    wind: number;
}

interface WeatherWidgetProps {
    weather: WeatherData | null;
    isLoading?: boolean;
    error?: string | null;
}

export function WeatherWidget({ weather, isLoading, error }: WeatherWidgetProps) {
    return (
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-900 dark:to-slate-900 border-none text-white shadow-lg relative overflow-hidden h-full">
            <CardContent className="p-6 h-full flex flex-col justify-between">
                <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
                    <span className="material-symbols-outlined text-9xl">wb_sunny</span>
                </div>

                {isLoading ? (
                    <div className="relative z-10 flex flex-col items-center justify-center h-full gap-2 py-4">
                        <Loader2 className="h-8 w-8 animate-spin text-blue-100" />
                        <p className="text-sm text-blue-100">Loading weather...</p>
                    </div>
                ) : error || !weather ? (
                    <div className="relative z-10 flex flex-col items-center justify-center h-full gap-2 py-4">
                        <CloudOff className="h-8 w-8 text-blue-100" />
                        <p className="text-sm text-blue-100">{error || "Weather data unavailable"}</p>
                        <p className="text-xs text-blue-200">Save a field location to see weather</p>
                    </div>
                ) : (
                    <div className="relative z-10 flex flex-col h-full justify-between">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-medium text-blue-100">Current Weather</h3>
                                <div className="flex items-center mt-2">
                                    <span className="text-5xl font-bold tracking-tighter">{weather.temp}°</span>
                                    <div className="ml-3">
                                        <p className="text-lg font-medium">{weather.condition}</p>
                                        <p className="text-sm text-blue-100">Humidity: {weather.humidity}%</p>
                                    </div>
                                </div>
                            </div>
                            <span className="material-symbols-outlined text-4xl text-yellow-300">wb_sunny</span>
                        </div>
                        <div className="mt-6 pt-4 border-t border-white/20">
                            <div className="grid grid-cols-2 gap-2 text-center">
                                <div className="flex flex-col items-center gap-1">
                                    <span className="text-xs text-blue-100">Wind</span>
                                    <span className="material-symbols-outlined text-sm">air</span>
                                    <span className="font-bold text-sm">{weather.wind} km/h</span>
                                </div>
                                <div className="flex flex-col items-center gap-1">
                                    <span className="text-xs text-blue-100">Humidity</span>
                                    <span className="material-symbols-outlined text-sm">water_drop</span>
                                    <span className="font-bold text-sm">{weather.humidity}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
