"use client";

import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polygon,
  CircleMarker,
  Polyline,
  useMapEvents,
  useMap,
} from "react-leaflet";
import * as turf from "@turf/turf";
import L from "leaflet";
import { GeoSearchControl, OpenStreetMapProvider } from "leaflet-geosearch";
import { useAuth } from "@/context/AuthContext";
import { useField } from "@/context/FieldContext";
import "leaflet/dist/leaflet.css";
import "leaflet-geosearch/dist/geosearch.css";
import "./MapView.css";
import { API_BASE_URL } from "@/lib/api";

// ================= Map Click Handler =================
function MapClickHandler({
  onMapClick,
  isDrawing,
}: {
  onMapClick: (latlng: any) => void;
  isDrawing: boolean;
}) {
  useMapEvents({
    click(e) {
      if (isDrawing) onMapClick(e.latlng);
    },
  });
  return null;
}

// ================= Map Type Toggle =================
function MapTypeControl({
  mapType,
  setMapType,
}: {
  mapType: string;
  setMapType: (t: string) => void;
}) {
  const map = useMap();
  React.useEffect(() => {
    const Control = L.Control.extend({
      onAdd: function () {
        const div = L.DomUtil.create("div", "leaflet-bar leaflet-control");
        div.style.backgroundColor = "white";
        div.style.padding = "5px 10px";
        div.style.cursor = "pointer";
        div.style.borderRadius = "5px";
        div.style.fontSize = "14px";
        div.style.boxShadow = "0 2px 6px rgba(0,0,0,0.3)";
        div.innerHTML = mapType === "street" ? "🛰️ Satellite" : "🌍 Street";
        div.onclick = () =>
          setMapType(mapType === "street" ? "satellite" : "street");
        L.DomEvent.disableClickPropagation(div);
        return div;
      },
    });
    const control = new Control({ position: "topleft" });
    map.addControl(control);
    return () => { map.removeControl(control); };
  }, [map, mapType, setMapType]);
  return null;
}

// ================= Search Control =================
function SearchControl() {
  const map = useMap();
  React.useEffect(() => {
    const provider = new OpenStreetMapProvider();
    // @ts-ignore
    const searchControl = new GeoSearchControl({
      provider,
      style: "bar",
      autoClose: true,
      keepResult: true,
    });
    map.addControl(searchControl);
    return () => { map.removeControl(searchControl); };
  }, [map]);
  return null;
}

// ================= Map Recenter Component =================
function MapRecenter({ center }: { center: [number, number] }) {
  const map = useMap();
  React.useEffect(() => {
    map.setView(center, 13);
  }, [map, center]);
  return null;
}

// ================= Main Component =================
export default function MapView({
  cropType,
  soilType,
  irrigationType,
  readOnly = false,
}: {
  cropType?: string;
  soilType?: string;
  irrigationType?: string;
  readOnly?: boolean;
}) {
  const { token } = useAuth();
  const { selectedField, refreshFields } = useField();
  const [farmPolygon, setFarmPolygon] = useState<any[]>([]);
  const [fieldName, setFieldName] = useState("My Field");
  const [isDrawing, setIsDrawing] = useState(false);
  const [farmArea, setFarmArea] = useState(0);
  const [mapType, setMapType] = useState("street");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Geolocation states
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [locationRequested, setLocationRequested] = useState(false);
  const [centerPosition, setCenterPosition] = useState<[number, number]>([9.1632, 76.6413]); // Kerala default

  // Request user's location on mount
  React.useEffect(() => {
    if (!locationRequested && !selectedField) {
      setLocationRequested(true);
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const userLoc: [number, number] = [
              position.coords.latitude,
              position.coords.longitude,
            ];
            setUserLocation(userLoc);
            setCenterPosition(userLoc);
            console.log("📍 User location detected:", userLoc);
          },
          (error) => {
            console.log("📍 Location access denied or unavailable, using default location");
            console.error(error);
          },
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
          }
        );
      }
    }
  }, [locationRequested, selectedField]);

  // Load selected field polygon
  React.useEffect(() => {
    if (selectedField) {
      setFieldName(selectedField.name);
      if (selectedField.polygon && selectedField.polygon.coordinates) {
        const coords = selectedField.polygon.coordinates[0];
        if (coords) {
          // Convert [lon, lat] to [lat, lon]
          const latlngs = coords.map((c: any) => [c[1], c[0]]);
          // Remove last point if it duplicates first (closed loop)
          if (latlngs.length > 2 && latlngs[0][0] === latlngs[latlngs.length - 1][0] && latlngs[0][1] === latlngs[latlngs.length - 1][1]) {
            latlngs.pop();
          }
          setFarmPolygon(latlngs);

          // Calculate area
          try {
            const area = Number((turf.area(selectedField.polygon) / 10000).toFixed(2));
            setFarmArea(area);
          } catch (e) { console.error(e); }

          // Center map on the selected field
          if (latlngs.length > 0) {
            const fieldCenter: [number, number] = [latlngs[0][0], latlngs[0][1]];
            setCenterPosition(fieldCenter);
          }

          setSubmitted(true);
        }
      }
    } else {
      // New field mode - use user location if available, otherwise default
      setFarmPolygon([]);
      setFarmArea(0);
      setFieldName("My Field");
      setSubmitted(false);
      if (userLocation) {
        setCenterPosition(userLocation);
      }
    }
  }, [selectedField, userLocation]);

  const handleMapClick = (latlng: any) => {
    if (isDrawing) {
      const newPoint = [latlng.lat, latlng.lng];
      const newPolygon = [...farmPolygon, newPoint];
      setFarmPolygon(newPolygon);

      if (newPolygon.length >= 3) {
        const coords = newPolygon.map((p) => [p[1], p[0]]);
        coords.push(coords[0]);
        setFarmArea(
          Number((turf.area(turf.polygon([coords])) / 10000).toFixed(2))
        );
      }
    }
  };

  // Toolbar
  const startDrawing = () => {
    setIsDrawing(true);
    setFarmPolygon([]);
    setFarmArea(0);
    setSubmitted(false);
  };
  const finishDrawing = () => {
    if (farmPolygon.length >= 3) {
      setIsDrawing(false);
      const coords = farmPolygon.map((p) => [p[1], p[0]]);
      coords.push(coords[0]);
      setFarmArea(
        Number((turf.area(turf.polygon([coords])) / 10000).toFixed(2))
      );
    } else alert("Please select at least 3 points!");
  };
  const clearFarm = () => {
    setFarmPolygon([]);
    setIsDrawing(false);
    setFarmArea(0);
    setSubmitted(false);
  };
  const undoLastPoint = () => {
    if (farmPolygon.length > 0) setFarmPolygon(farmPolygon.slice(0, -1));
  };

  const requestLocation = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const userLoc: [number, number] = [
            position.coords.latitude,
            position.coords.longitude,
          ];
          setUserLocation(userLoc);
          setCenterPosition(userLoc);
          console.log("📍 User location updated:", userLoc);
        },
        (error) => {
          alert("📍 Unable to access location. Please enable location services or use the search bar to find your area.");
          console.error(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    } else {
      alert("📍 Geolocation is not supported by your browser. Please use the search bar to find your area.");
    }
  };

  // ================= Submit =================
  const handleSubmit = async () => {
    if (farmPolygon.length < 3) {
      alert("⚠️ Please draw a farm boundary first.");
      return;
    }

    if (!cropType) {
      alert("⚠️ Please select a crop type.");
      return;
    }

    if (!token) {
      alert("⚠️ Please log in to save your field.");
      return;
    }

    const polygonGeoJSON = {
      type: "Polygon",
      coordinates: [
        [
          ...farmPolygon.map((p) => [p[1], p[0]]),
          [farmPolygon[0][1], farmPolygon[0][0]],
        ],
      ],
    };

    const farmData = {
      id: selectedField?.id,
      name: fieldName,
      polygon: polygonGeoJSON,
      cropType: cropType,
      soilType: soilType,
      irrigationType: irrigationType,
      area: farmArea,
    };

    try {
      setLoading(true);

      const res = await fetch(`${API_BASE_URL}/field/set_polygon`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify(farmData),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || "Failed to submit polygon");
      }

      const data = await res.json();
      console.log("✅ Polygon saved:", data);
      setSubmitted(true);
      setIsDrawing(false);
      setSubmitted(true);
      setIsDrawing(false);
      await refreshFields(); // Refresh the list in sidebar
      alert("✅ Farm polygon saved successfully!");
    } catch (err: any) {
      console.error(err);
      alert(`🚨 Error submitting farm data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mapview-container">
      <div className="toolbar">
        <button
          className="btn btn-green-700"
          onClick={startDrawing}
          disabled={isDrawing}
        >
          Start
        </button>
        <button
          className="btn btn-green-600"
          onClick={undoLastPoint}
          disabled={!isDrawing || farmPolygon.length === 0}
        >
          Undo
        </button>
        <button
          className="btn btn-green-500"
          onClick={finishDrawing}
          disabled={!isDrawing || farmPolygon.length < 3}
        >
          Finish
        </button>
        <button className="btn btn-green-800" onClick={clearFarm}>
          Clear
        </button>
        <button
          className="btn btn-blue-600"
          onClick={requestLocation}
          title="Center map at your location"
        >
          📍 My Location
        </button>
      </div>

      <div className="map-container">
        <MapContainer
          center={centerPosition}
          zoom={8}
          style={{ height: "100%", width: "100%" }}
        >
          <MapRecenter center={centerPosition} />
          <SearchControl />
          <MapTypeControl mapType={mapType} setMapType={setMapType} />
          <TileLayer
            url={
              mapType === "street"
                ? "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                : "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            }
            attribution={mapType === "street" ? "" : "Tiles © Esri"}
          />
          <MapClickHandler onMapClick={handleMapClick} isDrawing={isDrawing} />

          {farmPolygon.map((point, idx) => (
            <CircleMarker
              key={idx}
              center={point}
              radius={5}
              pathOptions={{
                color: "#fff",
                fillColor: isDrawing ? "#ff5722" : "#4caf50",
                fillOpacity: 1,
              }}
            />
          ))}

          {farmPolygon.length >= 2 && (
            <Polyline
              positions={farmPolygon}
              pathOptions={{
                color: isDrawing ? "#ff5722" : "#4caf50",
                weight: 3,
                dashArray: isDrawing ? "6,6" : undefined,
              }}
            />
          )}

          {!isDrawing && farmPolygon.length >= 3 && (
            <Polygon
              positions={farmPolygon}
              pathOptions={{ color: "#4caf50", fillColor: "#4caf50" }}
            />
          )}
        </MapContainer>
      </div>

      <div className="area-display">
        {farmArea > 0 ? `Area: ${farmArea} hectares` : "No farm selected"}
        {selectedField && <span className="ml-2 font-bold">({selectedField.name})</span>}
      </div>

      {farmPolygon.length >= 3 && !isDrawing && !readOnly && (
        <div className="submit-section flex flex-col gap-2">
          {!submitted || selectedField ? (
            <>
              <input
                type="text"
                value={fieldName}
                onChange={(e) => setFieldName(e.target.value)}
                className="p-2 border rounded text-black"
                placeholder="Field Name"
              />
              <button
                className="btn btn-green-600"
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? "Saving..." : (selectedField ? "Update Field" : "Save New Field")}
              </button>
            </>
          ) : null}
          {submitted && <p className="text-green-700 mt-2">✅ Saved!</p>}
        </div>
      )}
    </div>
  );
}
