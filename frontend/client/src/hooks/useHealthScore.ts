import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { apiFetch } from "@/lib/api";
import { HealthScoreResponse } from "@/types/field";
import { logger } from "@/lib/logger";

interface UseHealthScoreReturn {
    healthData: HealthScoreResponse | null;
    isLoading: boolean;
    error: string | null;
    refetch: () => void;
}

export function useHealthScore(): UseHealthScoreReturn {
    const { token } = useAuth();
    const { selectedField } = useField();

    const [healthData, setHealthData] = useState<HealthScoreResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchHealth = useCallback(async () => {
        if (!token) {
            setIsLoading(false);
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            let endpoint = '/field/healthscore';
            if (selectedField) endpoint += `?field_id=${selectedField.id}`;
            const data = await apiFetch<HealthScoreResponse>(endpoint);
            setHealthData(data);
        } catch (err) {
            logger.error("Health score fetch error:", err);
            setError("Unable to load health data");
            setHealthData(null);
        } finally {
            setIsLoading(false);
        }
    }, [selectedField, token]);

    useEffect(() => {
        fetchHealth();
    }, [fetchHealth]);

    return { healthData, isLoading, error, refetch: fetchHealth };
}
