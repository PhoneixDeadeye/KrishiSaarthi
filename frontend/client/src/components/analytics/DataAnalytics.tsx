import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/useTranslation";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { apiFetch } from "@/lib/api";
import { CarbonCreditResponse, AWDResponse } from "@/types/field";
import { IndicesReport } from "./IndicesReport";

// Helper component to update map view
function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

export function DataAnalytics() {
  const { t } = useTranslation();
  const { token } = useAuth();
  const { selectedField } = useField();

  const [location, setLocation] = useState("");
  const [mapCenter, setMapCenter] = useState<[number, number]>([20.5937, 78.9629]); // India center default
  const [ccData, setCcData] = useState<CarbonCreditResponse | null>(null);
  const [ccLoading, setCcLoading] = useState(true);
  const [ccError, setCcError] = useState<unknown>(null);
  const [awdData, setAwdData] = useState<AWDResponse | null>(null);
  const [awdLoading, setAwdLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setCcLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        let url = "/field/cc";
        if (selectedField) url += `?field_id=${selectedField.id}`;
        const json = await apiFetch<CarbonCreditResponse>(url);
        setCcData(json);
      } catch (err) {
        console.error("Carbon Credits fetch error:", err);
        setCcError(err);
      } finally {
        setCcLoading(false);
      }
    };
    fetchData();

    // Fetch AWD data
    const fetchAWD = async () => {
      try {
        let url = "/field/awd";
        if (selectedField) url += `?field_id=${selectedField.id}`;
        const json = await apiFetch<AWDResponse>(url);
        setAwdData(json);
      } catch (err) {
        console.error("AWD fetch error:", err);
      } finally {
        setAwdLoading(false);
      }
    };
    fetchAWD();

    if (selectedField) {
      apiFetch<{ lat: number; lon: number }>(
        `/field/coord?field_id=${selectedField.id}`
      )
        .then((data) => {
          if (data.lat && data.lon) {
            setMapCenter([data.lat, data.lon]);
            setLocation("My Field Location");
          }
        })
        .catch(() => { /* Could not fetch coords for analytics map */ });
    }
  }, [token, selectedField]);

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">
            analytics
          </span>
          {t("data_analytics")}
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Environmental insights and carbon credits
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <IndicesReport />

          {/* Carbon Credit + Tree Count */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Carbon Credits */}
            <Card className="overflow-hidden flex flex-col h-full">
              <CardHeader className="border-b px-6 py-4">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">
                    eco
                  </span>
                  <CardTitle>{t("carbon_credits")}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="p-6 flex-1">
                {ccLoading ? (
                  <div className="flex justify-center items-center h-32">
                    <span className="material-symbols-outlined text-3xl animate-spin text-primary">
                      progress_activity
                    </span>
                  </div>
                ) : ccError || !ccData ? (
                  <div className="text-center text-muted-foreground py-8 flex flex-col items-center justify-center h-full">
                    <span className="material-symbols-outlined text-3xl mb-2">
                      pin_drop
                    </span>
                    <p className="text-sm">Save field location to see credits</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="text-center">
                      <div className="text-4xl font-extrabold text-primary">
                        {ccData?.carbon_credits?.toFixed(2)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {t("credits_earned")}
                      </div>
                    </div>
                    <div className="space-y-3 text-sm border-t pt-4">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">
                          {t("area_hectare")}
                        </span>
                        <span className="font-medium bg-secondary px-2 py-0.5 rounded">
                          {ccData?.area_hectare?.toFixed(2)} ha
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">
                          {t("methane_reduction")}
                        </span>
                        <span className="font-medium bg-secondary px-2 py-0.5 rounded">
                          {(ccData?.methane_reduction_kg / 1000).toFixed(1)}{" "}
                          tCO₂e
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">
                          {t("water_saving")}
                        </span>
                        <span className="font-medium bg-secondary px-2 py-0.5 rounded">
                          {ccData?.water_saved_cubic_m?.toFixed(1)} m³
                        </span>
                      </div>
                    </div>
                    <div className="p-3 bg-primary/10 rounded-lg text-center mt-4 border border-primary/20">
                      <p className="text-sm font-bold text-primary">
                        Est. Value: ₹{ccData?.estimated_value_inr?.toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tree Count */}
            <Card className="overflow-hidden flex flex-col h-full">
              <CardHeader className="border-b px-6 py-4">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary">
                    forest
                  </span>
                  <CardTitle>{t("tree_count")}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="p-6 flex-1 flex flex-col justify-center">
                <div className="text-center space-y-4">
                  <div className="size-24 bg-primary/10 rounded-full mx-auto flex items-center justify-center border-4 border-background shadow-inner">
                    <span className="material-symbols-outlined text-4xl text-primary">
                      forest
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Tree canopy detection is not yet available for your field.
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                      This feature uses satellite imagery to count trees. Coming soon.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* AWD Water Management Card */}
          <Card className="overflow-hidden">
            <CardHeader className="border-b px-6 py-4">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">
                  water_drop
                </span>
                <CardTitle>AWD Water Management</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {awdLoading ? (
                <div className="flex justify-center items-center h-24">
                  <span className="material-symbols-outlined text-3xl animate-spin text-primary">
                    progress_activity
                  </span>
                </div>
              ) : !awdData ? (
                <div className="text-center text-muted-foreground py-6">
                  <span className="material-symbols-outlined text-3xl mb-2">
                    water_damage
                  </span>
                  <p className="text-sm">No AWD data available</p>
                </div>
              ) : (
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-primary/5 rounded-lg">
                    <div className={`text-2xl font-bold ${awdData.awd_detected ? 'text-primary' : 'text-muted-foreground'}`}>
                      {awdData.awd_detected ? 'Yes' : 'No'}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">AWD Detected</div>
                  </div>
                  <div className="text-center p-4 bg-blue-500/10 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {awdData.cycles_count}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Wetting Cycles</div>
                  </div>
                  <div className="text-center p-4 bg-amber-500/10 rounded-lg">
                    <div className="text-2xl font-bold text-amber-600">
                      {awdData.dry_days_detected}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">Dry Days</div>
                  </div>
                </div>
              )}
              <p className="text-xs text-muted-foreground mt-4 text-center">
                Alternate Wetting & Drying reduces methane emissions and conserves water
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Map */}
        <div className="flex flex-col gap-6">
          <Card className="overflow-hidden h-fit flex flex-col">
            <CardHeader className="border-b px-6 py-4">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">
                  map
                </span>
                <CardTitle>{t("market_price")}</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              {/* Field Location Map */}
              {!location && (
                <div className="text-center text-sm text-muted-foreground py-2">
                  <span className="material-symbols-outlined text-lg mr-1">info</span>
                  Select a field to see its location on the map.
                </div>
              )}

              {/* Search */}
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <span className="absolute left-2.5 top-2.5 material-symbols-outlined text-muted-foreground text-[18px]">search</span>
                  <input
                    type="text"
                    placeholder="Search location"
                    className="w-full pl-9 pr-3 py-2 border rounded-md text-sm bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </div>
              </div>

              {/* Map */}
              <div className="h-64 rounded-lg overflow-hidden border shadow-inner relative z-0">
                {/* @ts-ignore */}
                <MapContainer
                  center={mapCenter}
                  zoom={12}
                  scrollWheelZoom={false}
                  className="h-full w-full"
                >
                  <MapUpdater center={mapCenter} />
                  {/* @ts-ignore */}
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <Marker position={mapCenter}>
                    <Popup>{location}</Popup>
                  </Marker>
                </MapContainer>
              </div>

              <Button className="w-full gap-2" size="lg" variant="outline" disabled>
                <span className="material-symbols-outlined text-lg">
                  directions
                </span>
                {t("view_directions")}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
