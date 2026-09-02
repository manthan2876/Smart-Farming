import { Outlet } from "react-router-dom";
import Sidebar from "./SideBar";
import { motion } from "motion/react";

export default function AppShell() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main-content">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="content-wrapper"
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  );
}