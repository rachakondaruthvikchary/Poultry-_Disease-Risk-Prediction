"use client";

import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";

export function QuickUpload({ onPick }: { onPick: (file: File) => void }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    multiple: false,
    accept: { "image/*": [".png", ".jpg", ".jpeg", ".webp"] },
    onDrop: (files) => files[0] && onPick(files[0]),
  });

  return (
    <div {...getRootProps()} className="glass soft-noise rounded-[2rem] p-3 cursor-pointer overflow-hidden panel-entrance">
      <input {...getInputProps()} />
      <div className={`rounded-[1.6rem] border-2 border-dashed px-6 py-10 text-center transition ${isDragActive ? "border-red-400 bg-red-50/70 dark:bg-red-950/20" : "border-red-300/50 bg-red-50/35 dark:bg-red-900/25"}`}>
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-[1.4rem] bg-gradient-to-br from-red-600 to-red-700 text-white shadow-lg">
          <UploadCloud className="h-8 w-8" />
        </div>
        <p className="font-display mt-4 text-2xl font-bold tracking-tight text-red-900 dark:text-red-50">Quick Image Upload</p>
        <p className="mt-2 text-sm text-red-800 dark:text-red-200">
          {isDragActive ? "Drop image here" : "Drag and drop a poultry image or tap to upload"}
        </p>
      </div>
    </div>
  );
}
