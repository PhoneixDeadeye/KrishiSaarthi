import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useAuth } from "./AuthContext";
import { API_BASE_URL } from "@/lib/api";
import { FieldPolygon } from "@/types/field";
import { logger } from "@/lib/logger";

export interface Field {
    id: number;
    name: string;
    cropType: string;
    polygon: FieldPolygon;
    created_at: string;
    area?: number;
}

interface FieldContextType {
    fields: Field[];
    selectedField: Field | null;
    loading: boolean;
    setSelectedField: (field: Field | null) => void;
    refreshFields: () => Promise<void>;
    deleteField: (fieldId: number) => Promise<boolean>;
}

const FieldContext = createContext<FieldContextType | undefined>(undefined);

export const FieldProvider = ({ children }: { children: ReactNode }) => {
    const { token } = useAuth();
    const [fields, setFields] = useState<Field[]>([]);
    const [selectedField, setSelectedField] = useState<Field | null>(null);
    const [loading, setLoading] = useState(false);

    // Fetch fields from backend
    const refreshFields = async () => {
        if (!token) {
            setFields([]);
            setSelectedField(null);
            return;
        }

        setLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/field/data`, {
                headers: {
                    Authorization: `Token ${token}`,
                },
            });

            if (res.ok) {
                const data = await res.json();
                setFields(data);

                // Select first field by default if none selected or if selected is not in list
                if (data.length > 0) {
                    // If we have a selected field, check if it still exists
                    if (selectedField) {
                        const exists = data.find((f: Field) => f.id === selectedField.id);
                        if (!exists) setSelectedField(data[0]);
                    } else {
                        setSelectedField(data[0]);
                    }
                } else {
                    setSelectedField(null);
                }
            } else {
                logger.error("Failed to fetch fields");
            }
        } catch (error) {
            logger.error("Error fetching fields:", error);
        } finally {
            setLoading(false);
        }
    };

    // Delete a field by ID
    const deleteField = async (fieldId: number): Promise<boolean> => {
        if (!token) return false;

        try {
            const res = await fetch(`${API_BASE_URL}/field/data/${fieldId}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Token ${token}`,
                },
            });

            if (res.ok || res.status === 204) {
                // If deleted field was selected, clear selection
                if (selectedField?.id === fieldId) {
                    setSelectedField(null);
                }
                // Refresh the fields list
                await refreshFields();
                return true;
            } else {
                logger.error("Failed to delete field");
                return false;
            }
        } catch (error) {
            logger.error("Error deleting field:", error);
            return false;
        }
    };

    useEffect(() => {
        refreshFields();
    }, [token]);

    return (
        <FieldContext.Provider value={{ fields, selectedField, loading, setSelectedField, refreshFields, deleteField }}>
            {children}
        </FieldContext.Provider>
    );
};

export const useField = () => {
    const context = useContext(FieldContext);
    if (!context) {
        throw new Error("useField must be used within a FieldProvider");
    }
    return context;
};
