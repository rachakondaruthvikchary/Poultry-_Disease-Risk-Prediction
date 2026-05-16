"use client";

import { motion } from "framer-motion";

export function AlertPanel({ alerts }: { alerts: any[] }) {
  return (
    <div className="glass rounded-3xl p-4">
      <h3 className="text-sm font-bold text-red-900 dark:text-red-50 mb-3">🚨 Alert Panel</h3>
      <div className="space-y-2 max-h-[260px] overflow-auto pr-1">
        {alerts.length === 0 && <p className="text-sm text-red-600 dark:text-red-300">No alerts yet.</p>}
        {alerts.map((alert) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-red-200 dark:border-red-700 p-3 bg-red-50/50 dark:bg-red-900/20"
          >
            <div className="flex items-center justify-between">
              <p className="font-medium text-sm text-red-900 dark:text-red-50">{alert.title}</p>
              <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-200">{alert.severity}</span>
            </div>
            <p className="text-xs mt-1 text-red-700 dark:text-red-300">{alert.message}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
