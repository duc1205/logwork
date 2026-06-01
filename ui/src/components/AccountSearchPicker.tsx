import { useEffect, useMemo, useRef, useState } from "react";

import { api, ApiError } from "../api/client";
import type { JiraAccountOption } from "../api/types";

interface Props {
  value: string;
  onChange: (accountId: string) => void;
  placeholder?: string;
  required?: boolean;
  id?: string;
}

export function AccountSearchPicker({
  value,
  onChange,
  placeholder = "Tìm account / tên…",
  required,
  id,
}: Props) {
  const [accounts, setAccounts] = useState<JiraAccountOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [rosterOnly, setRosterOnly] = useState(false);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState(value);
  const [highlightIdx, setHighlightIdx] = useState(0);
  const wrapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setLoadError("");
    api
      .jiraEmployees()
      .then((res) => {
        if (cancelled) return;
        setAccounts(res.items);
        setRosterOnly(res.items.length > 0 && res.items.every((a) => a.source === "roster"));
      })
      .catch((e) => {
        if (!cancelled) {
          setLoadError(e instanceof ApiError ? e.message : String(e));
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!open && value) {
      const hit = accounts.find((a) => a.account_id.toLowerCase() === value.toLowerCase());
      setQuery(hit ? `${hit.account_id} — ${hit.display_name}` : value);
    }
    if (!value) setQuery("");
  }, [value, accounts, open]);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q
      ? accounts.filter(
          (a) =>
            a.account_id.toLowerCase().includes(q) ||
            a.display_name.toLowerCase().includes(q),
        )
      : accounts;
    return list.slice(0, 40);
  }, [accounts, query]);

  useEffect(() => {
    setHighlightIdx(0);
  }, [query, filtered.length]);

  function pick(item: JiraAccountOption) {
    onChange(item.account_id);
    setQuery(`${item.account_id} — ${item.display_name}`);
    setOpen(false);
  }

  function handleInputChange(text: string) {
    setQuery(text);
    setOpen(true);
    const raw = text.split("—")[0]?.trim().toLowerCase() ?? text.trim().toLowerCase();
    const exact = accounts.find((a) => a.account_id.toLowerCase() === raw);
    if (exact) {
      onChange(exact.account_id);
    } else if (!text.trim()) {
      onChange("");
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Escape") {
      setOpen(false);
      return;
    }
    if (!open || filtered.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightIdx((i) => Math.min(i + 1, filtered.length - 1));
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightIdx((i) => Math.max(i - 1, 0));
      return;
    }
    if (e.key === "Enter") {
      e.preventDefault();
      pick(filtered[highlightIdx] ?? filtered[0]);
    }
  }

  return (
    <div className="account-picker" ref={wrapRef}>
      <input
        id={id}
        type="search"
        className="account-picker-input"
        value={query}
        onChange={(e) => handleInputChange(e.target.value)}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
        placeholder={loading ? "Đang tải danh sách…" : placeholder}
        required={required}
        autoComplete="off"
        aria-expanded={open}
        aria-haspopup="listbox"
      />
      {open && !loading && (
        <ul className="account-picker-list" role="listbox">
          {rosterOnly && !loadError && (
            <li className="account-picker-hint muted">Nguồn: roster CSV (Jira plugin tạm không khả dụng)</li>
          )}
          {loadError && <li className="account-picker-empty muted">{loadError}</li>}
          {!loadError && filtered.length === 0 && (
            <li className="account-picker-empty muted">Không tìm thấy account</li>
          )}
          {filtered.map((a, idx) => (
            <li key={a.account_id}>
              <button
                type="button"
                className={`account-picker-option${
                  value.toLowerCase() === a.account_id.toLowerCase() ? " active" : ""
                }${idx === highlightIdx ? " highlighted" : ""}`}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => pick(a)}
                onMouseEnter={() => setHighlightIdx(idx)}
              >
                <code>{a.account_id}</code>
                <span>{a.display_name}</span>
              </button>
            </li>
          ))}
          {!loadError && accounts.length > 40 && filtered.length === 40 && (
            <li className="account-picker-hint muted">Gõ thêm để thu hẹp…</li>
          )}
        </ul>
      )}
    </div>
  );
}
