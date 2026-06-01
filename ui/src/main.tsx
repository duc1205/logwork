import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { initApiConfig } from "./api/base";
import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { PeriodProvider } from "./context/PeriodContext";
import "./index.css";

const root = document.getElementById("root")!;

initApiConfig().then(() => {
  createRoot(root).render(
    <StrictMode>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <AuthProvider>
          <PeriodProvider>
            <App />
          </PeriodProvider>
        </AuthProvider>
      </BrowserRouter>
    </StrictMode>,
  );
});
