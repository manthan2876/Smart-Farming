import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { motion } from "motion/react";
import { Menu } from "lucide-react";
import { useState } from "react";

export default function AppShell() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <button
        type="button"
        className="fixed left-4 top-4 z-40 inline-flex min-h-11 min-w-11 items-center justify-center rounded-sm border border-line bg-surface text-ink shadow-soft lg:hidden"
        onClick={() => setIsSidebarOpen(true)}
        aria-label="Open navigation"
        aria-expanded={isSidebarOpen}
      >
        <Menu size={20} />
      </button>
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="min-h-screen px-4 pb-8 pt-20 sm:px-6 lg:ml-72 lg:px-8 lg:pt-8">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="mx-auto w-full max-w-7xl"
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  );
}