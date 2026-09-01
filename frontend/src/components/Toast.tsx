import { motion, AnimatePresence } from "motion/react";
import { CheckCircle, XCircle, X } from "lucide-react";
import type { ToastState } from "../hooks/useToast";

interface ToastProps {
  toast: ToastState | null;
  onDismiss?: () => void;
}

export default function Toast({ toast, onDismiss }: ToastProps) {
  return (
    <div className="toast-container">
      <AnimatePresence>
        {toast && (
          <motion.div
            key={toast.id}
            className={`toast ${toast.type}`}
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
                style={{
                  background: "transparent",
                  color: "inherit",
                  marginLeft: 6,
                  padding: 2,
                  display: "flex",
                  alignItems: "center",
                  opacity: 0.75,
                }}
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
