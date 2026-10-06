import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { Menu } from "./icons";
import { useState } from "react";

export default function AppShell() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <button
        type="button"
        className="fixed left-4 top-4 z-40 inline-flex min-h-10 min-w-10 items-center justify-center rounded-sm border border-line bg-surface text-ink lg:hidden"
        onClick={() => setIsSidebarOpen(true)}
        aria-label="Open navigation"
        aria-expanded={isSidebarOpen}
      >
        <Menu size={18} />
      </button>
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="min-h-screen px-4 pb-12 pt-20 sm:px-6 lg:ml-72 lg:px-8 lg:pt-8">
        <div className="mx-auto w-full max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}