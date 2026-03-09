import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { logger } from "@/lib/logger";

export interface WeatherData {
    temp: number | string;
    condition: string;
    humidity: number;
    wind: number;
    icon?: string;
}

export interface ForecastEntry {
    dt: number;
    main: { temp: number; humidity: number };
    weather: { main: string; icon: string }[];
    wind: { speed: number };
}

interface UseWeatherReturn {
    weather: WeatherData | null;
    forecast: ForecastEntry[];
    isLoading: boolean;
    error: string | null;
    refetch: () => void;
}

export function useWeather(): UseWeatherReturn {
    const { token } = useAuth();
    const { selectedField } = useField();

    const [weather, setWeather] = useState<WeatherData | null>(null);
    const [forecast, setForecast] = useState<ForecastEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchWeather = useCallback(async () => {
        if (!token) {
            setIsLoading(false);
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            let coordEndpoint = '/field/coord';
            if (selectedField) coordEndpoint += `?field_id=${selectedField.id}`;
            const coordData = await apiFetch<any>(coordEndpoint);
            const coord = coordData?.coord || coordData?.location || null;
            let lon: number | undefined, lat: number | undefined;

            if (Array.isArray(coord)) {
                [lon, lat] = coord;
            } else if (coord && typeof coord === "object") {
                lon = coord.lon ?? coord.x;
                lat = coord.lat ?? coord.y;
            }

            if (lat === undefined || lon === undefined) {
                setWeather(null);
                setIsLoading(false);
                return;
            }

            const weatherData = await apiFetch<any>(`/field/weather?lat=${lat}&lon=${lon}`);

            setWeather({
                temp: Math.round(weatherData.current.main.temp),
                condition: weatherData.current.weather[0].main,
                humidity: weatherData.current.main.humidity,
                wind: Math.round(weatherData.current.wind.speed * 3.6),
                icon: weatherData.current.weather[0].icon,
            });

            setForecast(weatherData.forecast?.slice(0, 8) || []);
        } catch (err) {
            logger.error("Weather fetch error:", err);
            setError("Unable to load weather data");
            setWeather(null);
        } finally {
            setIsLoading(false);
        }
    }, [selectedField, token]);

    useEffect(() => {
        fetchWeather();
    }, [fetchWeather]);

    return { weather, forecast, isLoading, error, refetch: fetchWeather };
}
