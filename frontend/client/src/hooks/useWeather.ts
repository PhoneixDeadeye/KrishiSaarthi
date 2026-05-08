import { useMemo } from "react";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
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
    const { token, user } = useAuth();
    const { selectedField } = useField();

    const queryKey = useMemo(
        () => ["weather", user?.id ?? "guest", selectedField?.id ?? "all"],
        [selectedField?.id, user?.id]
    );

    const query = useQuery({
        queryKey,
        enabled: !!token,
        queryFn: async () => {
            let coordEndpoint = "/field/coord";
            if (selectedField) coordEndpoint += `?field_id=${selectedField.id}`;

            const coordData = await apiFetch<any>(coordEndpoint, {}, { timeout: 10000, retries: 1 });
            const coord = coordData?.coord || coordData?.location || null;
            let lon: number | undefined;
            let lat: number | undefined;

            if (Array.isArray(coord)) {
                [lon, lat] = coord;
            } else if (coord && typeof coord === "object") {
                lon = coord.lon ?? coord.x;
                lat = coord.lat ?? coord.y;
            }

            if (lat === undefined || lon === undefined) {
                return { weather: null, forecast: [] as ForecastEntry[] };
            }

            const weatherData = await apiFetch<any>(`/field/weather?lat=${lat}&lon=${lon}`, {}, { timeout: 10000, retries: 1 });

            return {
                weather: {
                    temp: Math.round(weatherData.current.main.temp),
                    condition: weatherData.current.weather[0].main,
                    humidity: weatherData.current.main.humidity,
                    wind: Math.round(weatherData.current.wind.speed * 3.6),
                    icon: weatherData.current.weather[0].icon,
                } as WeatherData,
                forecast: weatherData.forecast?.slice(0, 8) || [],
            };
        },
        retry: 1,
        staleTime: 2 * 60 * 1000,
    });

    if (query.error) {
        logger.error("Weather fetch error:", query.error);
    }

    return {
        weather: query.data?.weather ?? null,
        forecast: query.data?.forecast ?? [],
        isLoading: query.isLoading || query.isFetching,
        error: query.error ? "Unable to load weather data" : null,
        refetch: () => { void query.refetch(); },
    };
}
