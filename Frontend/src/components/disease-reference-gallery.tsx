"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { api } from "@/lib/api";
import { loadToken } from "@/lib/auth";
import toast from "react-hot-toast";
import { Loader2 } from "lucide-react";

interface DiseaseImage {
  filename: string;
  size: number;
  url: string;
}

interface DiseaseReferenceData {
  disease_name: string;
  folder_name: string;
  total_images: number;
  images: DiseaseImage[];
}

const DISEASES = [
  "Newcastle disease",
  "Avian Influenza",
  "Infectious Bursal Disease",
  "Marek's Disease",
  "Fowl Pox",
  "Infectious Bronchitis",
  "Salmonellosis/Pullorum",
  "Fowl Cholera",
  "Mycoplasmosis (CRD)",
  "Infectious Coryza",
  "Coccidiosis",
  "Healthy",
];

export function DiseaseReferenceGallery() {
  const [selectedDisease, setSelectedDisease] = useState<string>(DISEASES[0]);
  const [images, setImages] = useState<DiseaseImage[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDiseaseImages();
  }, [selectedDisease]);

  const loadDiseaseImages = async () => {
    const token = loadToken();
    if (!token) return;

    setLoading(true);
    try {
      const response = await api.get(`/predictions/reference-images/${selectedDisease}`);
      setImages(response.data.images || []);
    } catch (error: any) {
      console.error("Failed to load disease images", error);
      if (error?.response?.status !== 401) {
        toast.error("Failed to load reference images");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass rounded-3xl p-6 mt-6">
      <h2 className="text-xl font-semibold mb-4">📷 Disease Reference Gallery</h2>

      {/* Disease Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Select Disease:</label>
        <select
          value={selectedDisease}
          onChange={(e) => setSelectedDisease(e.target.value)}
          className="w-full max-w-xs px-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg dark:bg-slate-900 dark:text-slate-100"
        >
          {DISEASES.map((disease) => (
            <option key={disease} value={disease}>
              {disease}
            </option>
          ))}
        </select>
      </div>

      {/* Images Grid */}
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : images.length === 0 ? (
        <div className="text-center py-8 text-slate-500">
          No reference images available for {selectedDisease}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {images.map((img) => (
            <div key={img.filename} className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
              <div className="relative w-full h-48 bg-slate-100 dark:bg-slate-800">
                <Image
                  src={img.url}
                  alt={img.filename}
                  fill
                  className="object-cover"
                  onError={(e) => {
                    console.error("Image load error:", e);
                  }}
                />
              </div>
              <div className="p-3 text-sm">
                <p className="font-medium truncate">{img.filename}</p>
                <p className="text-slate-500 dark:text-slate-400">
                  {(img.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
