"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

type Props = {
  value: string;
  onChange: (v: string) => void;
};

export default function MapComponent({ value, onChange }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);

  const setMarker = (latlng: L.LatLngExpression, label?: string) => {
    if (!mapRef.current) return;

    if (markerRef.current) {
      markerRef.current.setLatLng(latlng);
    } else {
      markerRef.current = L.marker(latlng).addTo(mapRef.current);
    }

    mapRef.current.setView(latlng, 11);

    if (label) {
      onChange(label);
    }
  };

  const geocodeLocation = async (query: string) => {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query)}`,
      {
        headers: {
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) return null;
    const data = await response.json();
    if (!Array.isArray(data) || data.length === 0) return null;

    return {
      lat: Number(data[0].lat),
      lng: Number(data[0].lon),
      label: data[0].display_name as string,
    };
  };

  const reverseGeocode = async (lat: number, lng: number) => {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`,
      {
        headers: {
          Accept: "application/json",
        },
      }
    );

    if (!response.ok) return null;
    const data = await response.json();
    return (data?.display_name as string | undefined) || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  };

  useEffect(() => {
    if (!ref.current) return;
    if (mapRef.current) return;

    const map = L.map(ref.current).setView([20.5937, 78.9629], 5);
    mapRef.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
    }).addTo(map);

    map.on("click", (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;
      void reverseGeocode(lat, lng).then((label) => {
        const readable = label || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        setMarker(e.latlng, readable);
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, [onChange]);

  useEffect(() => {
    if (!mapRef.current) return;
    if (!value) return;

    const parts = value.split(",");
    if (parts.length === 2) {
      const lat = parseFloat(parts[0]);
      const lng = parseFloat(parts[1]);
      if (!Number.isNaN(lat) && !Number.isNaN(lng)) {
        const latlng = L.latLng(lat, lng);
        if (markerRef.current) markerRef.current.setLatLng(latlng);
        else markerRef.current = L.marker(latlng).addTo(mapRef.current);
        mapRef.current.setView(latlng, 11);
      }
      return;
    }

    void geocodeLocation(value).then((result) => {
      if (!result || !mapRef.current) return;
      const latlng = L.latLng(result.lat, result.lng);
      setMarker(latlng, result.label);
    });
  }, [value]);

  return <div ref={ref} className="w-full h-full" />;
}
