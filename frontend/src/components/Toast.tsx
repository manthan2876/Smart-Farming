import { motion, AnimatePresence } from "motion/react";
import { CheckCircle, XCircle, X } from "lucide-react";
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
            className={`pointer-events-auto flex max-w-sm items-center gap-3 rounded-sm border px-4 py-3 text-sm font-semibold shadow-lift ${toast.type === "success" ? "border-farmer-200 bg-farmer-50 text-farmer-800" : "border-red-200 bg-red-50 text-danger"}`}
            initial={{ opacity: 0, y: 24, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.95 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
          >
            {toast.type === "success" ? (
              <CheckCircle size={15} />
            ) : (
              <XCircle size={15} />
            )}
            <span>{toast.message}</span>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="ml-auto flex p-0.5 opacity-75 hover:opacity-100"
                aria-label="Dismiss"
              >
                <X size={13} />
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
