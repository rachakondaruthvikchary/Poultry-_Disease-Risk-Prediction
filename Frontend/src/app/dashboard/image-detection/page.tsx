"use client";

import { useState, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { DashboardShell } from "@/components/dashboard-shell";
import { UploadCloud, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import Image from "next/image";

type DiseaseInfo = {
  category: "Viral" | "Bacterial" | "General";
  description: string;
  signs: string[];
  precautions: string[];
  action: string;
};

const DISEASE_REFERENCE: Record<string, DiseaseInfo> = {
  "Newcastle disease": {
    category: "Viral",
    description: "Highly contagious disease causing respiratory problems, paralysis, and green diarrhea.",
    signs: ["Respiratory distress", "Nervous signs/paralysis", "Green diarrhea", "Sudden drop in production"],
    precautions: ["Vaccinate birds on schedule", "Keep new birds quarantined", "Disinfect feeders, waterers, and housing regularly"],
    action: "Isolate affected birds immediately and contact a veterinarian.",
  },
  "Avian Influenza": {
    category: "Viral",
    description: "Severe viral disease with high spread potential and high mortality.",
    signs: ["Severe respiratory distress", "Head/facial swelling", "Sudden mortality", "Weakness"],
    precautions: ["Use strict biosecurity and visitor control", "Avoid contact with wild birds", "Report suspicious cases immediately"],
    action: "Trigger emergency biosecurity protocol and report urgently to veterinary authorities.",
  },
  "Infectious Bursal Disease": {
    category: "Viral",
    description: "Primarily affects young chickens and weakens the immune system.",
    signs: ["Depression", "Ruffled feathers", "Diarrhea", "Higher susceptibility to other infections"],
    precautions: ["Protect chicks with proper vaccination", "Keep litter dry and clean", "Separate sick birds quickly"],
    action: "Isolate affected flock section and review vaccination and hygiene plan.",
  },
  "Marek's Disease": {
    category: "Viral",
    description: "Viral disease linked to tumors and nerve damage.",
    signs: ["Leg/wing paralysis", "Weight loss", "Vision issues", "Tumor-related weakness"],
    precautions: ["Vaccinate chicks early", "Maintain clean hatchery and brooder conditions", "Remove and isolate weak birds promptly"],
    action: "Separate affected birds and consult veterinarian for flock-level control strategy.",
  },
  "Fowl Pox": {
    category: "Viral",
    description: "Causes skin lesions and can affect upper respiratory tract in severe cases.",
    signs: ["Scabby skin lesions", "Mouth/throat lesions", "Reduced feed intake", "Breathing difficulty"],
    precautions: ["Control mosquitoes and biting insects", "Vaccinate where risk is high", "Keep housing dry and sanitary"],
    action: "Improve vector control, sanitation, and isolate severe symptomatic birds.",
  },
  "Infectious Bronchitis": {
    category: "Viral",
    description: "Highly contagious respiratory disease in chickens.",
    signs: ["Coughing/sneezing", "Nasal discharge", "Drop in egg quality/production", "Noisy breathing"],
    precautions: ["Improve ventilation", "Avoid overcrowding", "Vaccinate according to local veterinary guidance"],
    action: "Enhance ventilation and biosecurity, then seek veterinary treatment guidance.",
  },
  "Salmonellosis/Pullorum": {
    category: "Bacterial",
    description: "Bacterial disease causing diarrhea and high chick mortality.",
    signs: ["Diarrhea", "Lethargy", "Poor appetite", "High mortality in chicks"],
    precautions: ["Buy chicks from clean, tested sources", "Sanitize hatchery and coop equipment", "Separate and cull chronic carriers as advised"],
    action: "Isolate affected groups immediately and perform strict sanitation and testing.",
  },
  "Fowl Cholera": {
    category: "Bacterial",
    description: "Acute bacterial disease often associated with diarrhea and swelling.",
    signs: ["Greenish diarrhea", "Swollen wattles", "Fever", "Sudden deaths"],
    precautions: ["Keep water sources clean", "Control rodents and wild birds", "Disinfect housing and equipment regularly"],
    action: "Start urgent veterinary intervention and strengthen disinfection routine.",
  },
  "Mycoplasmosis (CRD)": {
    category: "Bacterial",
    description: "Chronic respiratory disease affecting flock performance.",
    signs: ["Coughing", "Nasal discharge", "Sinus swelling", "Reduced feed conversion"],
    precautions: ["Maintain good ventilation", "Avoid overcrowding", "Quarantine new birds before mixing"],
    action: "Improve ventilation and apply veterinarian-recommended treatment plan.",
  },
  "Infectious Coryza": {
    category: "Bacterial",
    description: "Bacterial respiratory disease causing facial and eye swelling.",
    signs: ["Facial swelling", "Eye swelling/discharge", "Nasal discharge", "Breathing difficulty"],
    precautions: ["Isolate symptomatic birds", "Keep drinking water and feeders clean", "Practice strong flock hygiene"],
    action: "Separate symptomatic birds and implement strict flock hygiene controls.",
  },
  "Coccidiosis": {
    category: "General",
    description: "Parasitic intestinal disease commonly seen in poultry.",
    signs: ["Diarrhea", "Poor growth", "Low feed intake", "Dehydration"],
    precautions: ["Keep litter dry", "Use clean water and feeders", "Apply anticoccidial prevention as advised"],
    action: "Improve litter management and apply anticoccidial treatment as advised.",
  },
  "Healthy": {
    category: "General",
    description: "No obvious disease pattern detected by the model.",
    signs: ["Normal posture", "Active behavior", "Stable feed/water intake"],
    precautions: ["Continue routine vaccination", "Maintain daily cleaning and disinfection", "Monitor birds for early changes in appetite or behavior"],
    action: "Continue routine monitoring, vaccination schedule, and good biosecurity.",
  },
};


const normalizeDiseaseKey = (value: string) =>
  value
    .trim()
    .toLowerCase()
    .replace(/['’]/g, "")
    .replace(/[_\-\/()]/g, " ")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const DISEASE_LOOKUP = new Map<string, DiseaseInfo>(
  Object.entries(DISEASE_REFERENCE).map(([name, info]) => [normalizeDiseaseKey(name), info])
);

function getDiseaseInfo(name: string): DiseaseInfo | null {
  return DISEASE_LOOKUP.get(normalizeDiseaseKey(name)) ?? null;
}

export default function ImageDetectionPage() {
  const [farmId, setFarmId] = useState<number | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);
  const [result, setResult] = useState<any>(null);
  const diseaseInfo = result?.disease_name ? getDiseaseInfo(result.disease_name) : null;

  useEffect(() => {
    loadFarm();
  }, []);

  const loadFarm = async () => {
    try {
      const res = await api.get("/farms");
      if (res.data.length > 0) {
        setFarmId(res.data[0].id);
      } else {
        const created = await api.post("/farms", {
          name: "My Farm",
          location: "Default Location",
          flock_size: 100,
        });
        setFarmId(created.data.id);
      }
    } catch (error) {
      console.error("Failed to load farm", error);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    multiple: false,
    accept: { "image/*": [".png", ".jpg", ".jpeg", ".webp"] },
    maxSize: 5 * 1024 * 1024, // 5MB
    onDropRejected: (fileRejections) => {
      const error = fileRejections[0]?.errors[0];
      if (error?.code === "file-too-large") {
        toast.error("Image too large! Please use files under 5MB.");
      } else if (error?.code === "file-invalid-type") {
        toast.error("Invalid file type! Please use JPEG, PNG, or WEBP images.");
      } else {
        toast.error("Upload failed. Please try again.");
      }
    },
    onDrop: async (files) => {
      if (!farmId) {
        toast.error("Farm not found. Please refresh the page.");
        return;
      }
      if (!files[0]) return;

      const file = files[0];
      if (preview) {
        URL.revokeObjectURL(preview);
      }
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await api.post(`/predictions/${farmId}/image`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setResult(response.data);
        toast.success("Prediction complete!");
      } catch (error: any) {
        toast.error(error?.response?.data?.detail || "Prediction failed");
      } finally {
        setLoading(false);
      }
    },
  });

  return (
    <DashboardShell>
      <div className="glass rounded-3xl p-6">
        <h2 className="text-xl font-bold text-red-900 dark:text-red-50 mb-4">🔍 AI Disease Detection</h2>
        <p className="text-sm text-red-700 dark:text-red-300 mb-6">
          Upload a poultry image to detect diseases using our CNN model.
        </p>

        {!farmId ? (
          <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-3xl p-12 text-center">
            <UploadCloud className="h-12 w-12 mx-auto text-slate-400 mb-3" />
            <p className="font-medium text-slate-500">Loading farm data...</p>
            <p className="text-sm text-slate-400 mt-1">Please wait</p>
          </div>
        ) : (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-3xl p-12 text-center cursor-pointer transition-all duration-200 ${
              isDragActive
                ? "border-red-500 bg-red-100/50 scale-[1.02] dark:border-red-400 dark:bg-red-900/30"
                : "border-red-300/40 hover:border-red-400/60 hover:bg-red-50/50 dark:hover:bg-red-900/30"
            }`}
          >
            <input {...getInputProps()} />
            <UploadCloud className="h-16 w-16 mx-auto text-red-600 dark:text-red-400 mb-4" />
            <p className="text-lg font-bold text-red-900 dark:text-red-50 mb-2">
              {isDragActive ? "Drop your image here" : "Upload Chicken Image"}
            </p>
            <p className="text-sm text-red-700 dark:text-red-300 mb-4">
              Drag & drop your image here, or click to browse
            </p>
            <button
              type="button"
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold shadow-lg transition-colors inline-flex items-center gap-2 dark:bg-red-500 dark:hover:bg-red-600"
            >
              <UploadCloud className="h-5 w-5" />
              Browse Files
            </button>
            <p className="text-xs text-red-600 dark:text-red-400 mt-4">
              Supported formats: JPEG, PNG, WEBP · Max size: 5MB
            </p>
          </div>
        )}

        {preview && (
          <div className="mt-6 glass rounded-3xl p-4">
            <h3 className="text-sm font-medium mb-3">Preview</h3>
            <div className="relative aspect-video w-full max-w-md mx-auto rounded-2xl overflow-hidden">
              <Image src={preview} alt="Preview" fill className="object-cover" />
            </div>
          </div>
        )}

        {loading && (
          <div className="mt-6 glass rounded-3xl p-8 text-center">
            <Loader2 className="h-8 w-8 mx-auto animate-spin text-red-600 dark:text-red-400" />
            <p className="mt-3 text-sm text-red-700 dark:text-red-300">Analyzing image...</p>
          </div>
        )}

        {result && !loading && (
          <div className="mt-6 space-y-4">
            <div className="glass rounded-3xl p-6">
              <h3 className="text-lg font-bold text-red-900 dark:text-red-50 mb-4">Latest Prediction</h3>
              <p className="text-sm text-red-700 dark:text-red-300 mb-4">
                This section summarizes what the uploaded image indicates for the chicken.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-2xl border border-red-200 dark:border-red-700 p-4 bg-red-50/50 dark:bg-red-900/20">
                  <p className="text-sm text-red-700 dark:text-red-400">Detected Disease</p>
                  <p className="text-xl font-bold text-red-900 dark:text-red-50 mt-1">{result.disease_name}</p>
                </div>

                <div className="rounded-2xl border border-red-200 dark:border-red-700 p-4 bg-red-50/50 dark:bg-red-900/20">
                  <p className="text-sm text-red-700 dark:text-red-400">Risk Level</p>
                  <span
                    className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-medium ${
                      result.risk_level === "High"
                        ? "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-300"
                        : result.risk_level === "Medium"
                        ? "bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-300"
                        : "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-300"
                    }`}
                  >
                    {result.risk_level}
                  </span>
                </div>
              </div>

              <div className="mt-4">
                <p className="text-sm text-red-700 dark:text-red-400">Confidence</p>
                <div className="flex items-center gap-3 mt-2">
                  <div className="flex-1 bg-red-200 dark:bg-red-700 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-red-600 to-red-700 h-full rounded-full transition-all duration-700"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <span className="font-bold text-red-900 dark:text-red-50">{(result.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>

              <div className="mt-4">
                <p className="text-sm text-red-700 dark:text-red-400 mb-2">Immediate Suggested Action</p>
                <p className="text-sm bg-red-100 dark:bg-red-900/30 p-3 rounded-xl text-red-900 dark:text-red-50">
                  {result.suggested_action}
                </p>
              </div>
            </div>

            <div className="glass rounded-3xl p-6">
              <h3 className="text-lg font-semibold mb-4">Disease Details</h3>
              {diseaseInfo ? (
                <div className="space-y-4">
                  <div className="rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-sm text-slate-500 dark:text-slate-400">Category</p>
                    <p className="font-semibold mt-1">{diseaseInfo.category}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-sm text-slate-500 dark:text-slate-400">About This Disease</p>
                    <p className="text-sm mt-1">{diseaseInfo.description}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Common Signs</p>
                    <ul className="list-disc ml-5 space-y-1 text-sm">
                      {diseaseInfo.signs.map((sign) => (
                        <li key={sign}>{sign}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Precautions</p>
                    <ul className="list-disc ml-5 space-y-1 text-sm">
                      {diseaseInfo.precautions.map((precaution) => (
                        <li key={precaution}>{precaution}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
                    <p className="text-sm text-slate-500 dark:text-slate-400">Recommended Response</p>
                    <p className="text-sm mt-1">{diseaseInfo.action}</p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Detailed reference is not available for this label yet.
                </p>
              )}
            </div>
          </div>
        )}

        <div className="mt-6 glass rounded-3xl p-6">
          <h3 className="text-lg font-semibold mb-4">Poultry Disease Reference</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
            Included disease names and quick notes for monitoring and early response.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {Object.entries(DISEASE_REFERENCE).map(([name, info]) => (
              <div key={name} className="rounded-2xl border border-slate-200 dark:border-slate-700 p-4">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-semibold text-sm">{name}</p>
                  <span className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                    {info.category}
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">{info.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardShell>
  );
}
