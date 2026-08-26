import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles.css";
import "./overrides.css";
import "./component-overrides.css";
import "./page-overrides.css";
import "./dropdown-overrides.css";
import "./roadmap-overrides.css";
import "./workflow-overrides.css";
import "./gradcam-overrides.css";
import { AuthProvider } from "./context/AuthContext";

const queryClient = new QueryClient();
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
