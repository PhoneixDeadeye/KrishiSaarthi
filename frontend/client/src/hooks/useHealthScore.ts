import { useMemo } from "react";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { HealthScoreResponse } from "@/types/field";
import { logger } from "@/lib/logger";

interface UseHealthScoreReturn {
    healthData: HealthScoreResponse | null;
    isLoading: boolean;
    error: string | null;
    refetch: () => void;
}

export function useHealthScore(): UseHealthScoreReturn {
    const { token, user } = useAuth();
    const { selectedField } = useField();

    const queryKey = useMemo(
        () => ["healthScore", user?.id ?? "guest", selectedField?.id ?? "all"],
        [selectedField?.id, user?.id]
    );

    const query = useQuery({
        queryKey,
        enabled: !!token,
        queryFn: async () => {
            let endpoint = "/field/healthscore";
            if (selectedField) endpoint += `?field_id=${selectedField.id}`;
            return apiFetch<HealthScoreResponse>(endpoint, {}, { timeout: 15000, retries: 1 });
        },
        retry: 1,
        staleTime: 2 * 60 * 1000,
    });

    if (query.error) {
        logger.error("Health score fetch error:", query.error);
    }

    return {
        healthData: query.data ?? null,
        isLoading: query.isLoading || query.isFetching,
        error: query.error ? "Unable to load health data" : null,
        refetch: () => { void query.refetch(); },
    };
}
