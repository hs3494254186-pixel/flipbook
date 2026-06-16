"use client";

import { useEffect, useRef } from "react";

interface QuickbarItem {
  nodeId: string | null;
  title: string;
  query: string;
}

interface Props {
  query: string;
  setQuery: (q: string) => void;
  items: QuickbarItem[];
  onPick: (id: string) => void;
  onClose: () => void;
}

export function Quickbar({ query, setQuery, items, onPick, onClose }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const lower = query.trim().toLowerCase();
  const matches = items
    .filter(
      (p): p is QuickbarItem & { nodeId: string } =>
        !!p.nodeId &&
        (lower
          ? p.title.toLowerCase().includes(lower) ||
            p.query.toLowerCase().includes(lower)
          : true),
    )
    .slice(-8)
    .reverse();

  return (
    <div
      className="fixed inset-0 z-[60] flex items-start justify-center bg-black/32 px-4 pt-[20vh] backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-3xl border border-black/10 bg-white/88 p-3 shadow-[0_30px_90px_rgba(15,23,42,0.25)] backdrop-blur-2xl dark:border-white/10 dark:bg-black/78"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && matches[0]) onPick(matches[0].nodeId);
          }}
          placeholder="Jump to page..."
          className="w-full rounded-2xl border border-[var(--color-edge)] bg-transparent px-4 py-3 text-sm outline-none focus:border-[var(--color-ink)]"
        />
        <ul className="mt-2 max-h-72 overflow-auto text-sm">
          {matches.length === 0 && (
            <li className="px-3 py-3 opacity-60">No matches yet.</li>
          )}
          {matches.map((m) => (
            <li key={m.nodeId}>
              <button
                type="button"
                className="block w-full rounded-2xl px-3 py-2 text-left transition hover:bg-[var(--color-ink)]/8"
                onClick={() => onPick(m.nodeId)}
              >
                <span className="block truncate font-medium">{m.title}</span>
                <span className="block truncate text-xs opacity-55">{m.query}</span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
