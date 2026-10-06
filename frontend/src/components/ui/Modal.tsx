import { X } from "../icons";
import type { ReactNode } from "react";

interface ModalProps {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}

export default function Modal({ open, title, children, onClose }: ModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-4" role="dialog" aria-modal="true" aria-label={title}>
      <div className="w-full max-w-lg rounded-sm border border-line bg-surface p-6">
        <div className="mb-5 flex items-center justify-between gap-4 border-b border-line pb-4">
          <h2 className="font-display text-xl text-ink">{title}</h2>
          <button className="rounded-sm p-1.5 text-muted hover:bg-canvas hover:text-ink transition-colors" onClick={onClose} aria-label="Close dialog">
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
