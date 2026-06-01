import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { defaultPeriod, type PeriodSelection } from "../utils/period";

const STORAGE_KEY = "logwork_period";

function loadStoredPeriod(): PeriodSelection {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as PeriodSelection;
      if (parsed.mode && parsed.start && parsed.end && parsed.month) {
        return parsed;
      }
    }
  } catch {
    /* ignore */
  }
  return defaultPeriod();
}

interface PeriodState {
  period: PeriodSelection;
  setPeriod: (p: PeriodSelection) => void;
}

const PeriodContext = createContext<PeriodState | null>(null);

export function PeriodProvider({ children }: { children: ReactNode }) {
  const [period, setPeriodState] = useState<PeriodSelection>(loadStoredPeriod);

  const setPeriod = useCallback((p: PeriodSelection) => {
    setPeriodState(p);
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(p));
    } catch {
      /* ignore */
    }
  }, []);

  const value = useMemo(() => ({ period, setPeriod }), [period, setPeriod]);

  return <PeriodContext.Provider value={value}>{children}</PeriodContext.Provider>;
}

export function usePeriod(): PeriodState {
  const ctx = useContext(PeriodContext);
  if (!ctx) throw new Error("usePeriod must be used within PeriodProvider");
  return ctx;
}
