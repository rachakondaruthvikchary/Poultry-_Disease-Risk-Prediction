"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

const MapComponent = dynamic(() => import("./map-component"), { ssr: false });

export const LocationPicker: React.FC<{
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}> = ({ value, onChange, placeholder }) => {
  const [open, setOpen] = useState(false);

  return (
    <div className="space-y-3">
      <div className="flex gap-2 items-center">
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-primary outline-none"
        />
        <button
          type="button"
          onClick={() => setOpen((s) => !s)}
          className="min-w-[112px] px-3 py-2 rounded-xl text-sm font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 transition-colors"
          aria-expanded={open}
          aria-controls="farm-location-map"
        >
          {open ? "Hide map" : "Open map"}
        </button>
      </div>

      <div className="rounded-xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/80 dark:bg-slate-900/40 px-4 py-3 text-xs text-slate-600 dark:text-slate-300">
        Type the farm location, or open the India map and click the exact area. The pin will update the text field with a readable place name.
      </div>

      {value && (
        <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 px-3 py-1 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          Selected location: {value}
        </div>
      )}

      {open && (
        <div id="farm-location-map" className="relative mt-1 h-72 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="absolute top-3 left-3 z-[500] rounded-full bg-white/95 dark:bg-slate-950/90 px-3 py-1 text-xs font-semibold text-slate-700 dark:text-slate-200 shadow">
            India map - click to place the farm pin
          </div>
          <MapComponent value={value} onChange={onChange} />
        </div>
      )}
    </div>
  );
};
