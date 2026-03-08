export interface NDVITimeSeriesPoint {
    date: string; // ISO date string YYYY-MM-DD
    NDVI: number;
}

export interface FieldPolygon {
    type: "Polygon";
    coordinates: number[][][];
}

export interface NDWITimeSeriesPoint {
    date: string;
    NDWI: number;
}

export interface EEDataResponse {
    NDVI: number | null;
    EVI: number | null;
    SAVI: number | null;
    crop_type_class: number | null;
    rainfall_mm: number | null;
    temperature_K: number | null;
    soil_moisture: number | null;
    ndvi_time_series: NDVITimeSeriesPoint[] | null;
    ndwi_time_series: NDWITimeSeriesPoint[] | null;
    error?: string;
    details?: string;
}

export interface CarbonCreditResponse {
    carbon_credits: number;
    area_hectare: number;
    methane_reduction_kg: number;
    water_saved_cubic_m: number;
    co2e_reduction_ton: number;
    estimated_value_inr: number;
}

export interface AWDResponse {
    awd_detected: boolean;
    cycles_count: number;
    dry_days_detected: number;
}

export interface HealthScoreResponse {
    score: number;
    score_percent: number;
    rating: string;
    color: string;
    recommendation: string;
    breakdown: {
        cnn: { value: number; status: string; class?: string; confidence?: string; error?: string };
        ndvi: { value: number; raw: number | null; status: string };
        risk: { value: number; level?: string; recommendation?: string; status: string; error?: string };
    };
    weights: { cnn: number; ndvi: number; risk: number };
}

export interface PestDetectionResult {
    class: string; // e.g., "Healthy", "Rust", etc.
    confidence: number;
    error?: string;
    detected?: string; // What was detected in the image (for validation errors)
    image_validated?: boolean; // Whether the image was validated as a plant
    validation_confidence?: string; // Confidence of plant validation
}

export interface PestReport {
    id: number;
    image: string;
    uploaded_at: string;
    result?: Record<string, unknown>; // JSON field from backend
}

export interface NDVIData {
    current: number;
    trend: string;
    status: { status: string; color: string; icon: string };
    time_series: { date: string; ndvi: number }[];
}

export interface PredictionData {
    field_id: number;
    field_name: string;
    crop_type: string;
    field_area_hectares: number;
    prediction: {
        yield_per_hectare: number;
        total_yield: number;
        unit: string;
        confidence: number;
        range: { low: number; high: number };
    };
    ndvi: NDVIData;
    comparison: {
        regional_average: number;
        vs_regional: number;
        rating: { rating: string; stars: number };
    };
    factors: {
        ndvi_impact: number;
        trend_impact: number;
        base_yield: number;
    };
    recommendations: { type: string; icon: string; text: string }[];
}

export interface AgroAlert {
    id: string;
    type: string;
    location: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    date: string;
}
