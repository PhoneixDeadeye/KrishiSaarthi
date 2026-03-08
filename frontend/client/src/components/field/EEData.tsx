
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Satellite, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import {
  ActivityLogIcon,
  BarChartIcon,
  SunIcon,
  MixerHorizontalIcon,
  Half2Icon,
} from "@radix-ui/react-icons";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

import { apiFetch } from "@/lib/api";
import { EEDataResponse } from "@/types/field";

export function EEData() {
  const { token } = useAuth();
  const { selectedField } = useField();
  const [data, setData] = useState<EEDataResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFieldData = async () => {
      // If no token or no selected field, strictly speaking we might want to wait or clear data
      if (!token) {
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        let endpoint = '/field/ee';
        if (selectedField) {
          endpoint += `?field_id=${selectedField.id}`;
        }

        const json = await apiFetch<EEDataResponse>(endpoint);
        setData(json);
      } catch (err) {
        console.error("EE fetch error:", err);
        setData(null);
      } finally {
        setLoading(false);
      }
    };
    fetchFieldData();
  }, [token, selectedField]);

  // Chart data
  const chartData: ChartData<"line"> = {
    labels: data?.ndvi_time_series?.map((d) => d.date) || [],
    datasets: [
      {
        label: "NDVI",
        data: data?.ndvi_time_series?.map((d) => d.NDVI) || [],
        borderColor: "#16a34a",
        backgroundColor: "rgba(22, 163, 74, 0.2)",
        tension: 0.3,
        pointBackgroundColor: "#16a34a",
      },
    ],
  };

  const chartOptions: ChartOptions<"line"> = {
    responsive: true,
    plugins: {
      legend: { display: true, position: "top", labels: { color: "#065f46" } },
      title: { display: false },
    },
    scales: {
      x: { ticks: { color: "#065f46", maxRotation: 0 } },
      y: { min: 0, max: 1, ticks: { color: "#065f46" } },
    },
  };

  return (
    <Card className="bg-gradient-to-b from-green-50 to-white border-green-200">
      <CardHeader>
        <CardTitle className="flex items-center text-green-700">
          <Satellite className="mr-2 h-5 w-5" />
          Field Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <Loader2 className="h-6 w-6 animate-spin text-green-600" />
            <span className="ml-2 text-sm text-green-600">
              Fetching satellite data...
            </span>
          </div>
        ) : data?.error ? (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800">
            <div className="flex items-center gap-2 mb-2 font-semibold">
              <span className="text-xl">⚠️</span>
              Data Unavailable
            </div>
            <p className="text-sm">{data.error}</p>
            {data.details && <p className="text-xs mt-1 opacity-75">{data.details}</p>}
          </div>
        ) : data ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
            {/* Stats */}
            <div className="space-y-3 text-sm text-green-800 font-medium">
              {data.NDVI !== null && (
                <div className="flex items-center gap-2">
                  <ActivityLogIcon /> <span className="font-bold">NDVI:</span>{" "}
                  {data.NDVI.toFixed(3)}
                </div>
              )}
              {data.EVI !== null && (
                <div className="flex items-center gap-2">
                  <BarChartIcon /> <span className="font-bold">EVI:</span>{" "}
                  {data.EVI.toFixed(3)}
                </div>
              )}
              {data.rainfall_mm !== null && (
                <div className="flex items-center gap-2">
                  <MixerHorizontalIcon />{" "}
                  <span className="font-bold">Rainfall:</span>{" "}
                  {data.rainfall_mm.toFixed(2)} mm
                </div>
              )}
              {data.temperature_K !== null && (
                <div className="flex items-center gap-2">
                  <SunIcon /> <span className="font-bold">Temperature:</span>{" "}
                  {(data.temperature_K - 273.15).toFixed(1)} °C
                </div>
              )}
              {data.soil_moisture !== null && (
                <div className="flex items-center gap-2">
                  <Half2Icon />{" "}
                  <span className="font-bold">Soil Moisture:</span>{" "}
                  {data.soil_moisture.toFixed(3)}
                </div>
              )}
            </div>

            {/* NDVI Chart */}
            <div className="h-40">
              <Line data={chartData} options={chartOptions} />
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Save your field location in "My Field" to see satellite data
          </p>
        )}
      </CardContent>
    </Card>
  );
}
