import { motion, AnimatePresence } from "motion/react";
import { CheckCircle, XCircle, X } from "./icons";
import type { ToastState } from "../hooks/useToast";

interface ToastProps {
  toast: ToastState | null;
  onDismiss?: () => void;
}

export default function Toast({ toast, onDismiss }: ToastProps) {
  return (
    <div className="pointer-events-none fixed bottom-6 right-6 z-[1000] flex max-w-[calc(100vw-3rem)] flex-col gap-3">
      <AnimatePresence>
        {toast && (
          <motion.div
            key={toast.id}
            className={`pointer-events-auto flex max-w-sm items-center gap-3 rounded-sm border px-4 py-3 text-sm font-semibold ${
              toast.type === "success" 
                ? "border-farmer-400 bg-surface text-farmer-800 dark:border-farmer-700 dark:text-farmer-200" 
                : "border-red-400 bg-surface text-danger dark:border-red-800 dark:text-red-300"
            }`}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.15 }}
          >
            {toast.type === "success" ? (
              <CheckCircle size={16} />
            ) : (
              <XCircle size={16} />
            )}
            <span>{toast.message}</span>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="ml-auto flex p-0.5 text-muted hover:text-ink transition-colors"
                aria-label="Dismiss"
              >
                <X size={14} />
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
