"use client";

interface Props {
  onClose: () => void;
}

/**
 * Modal that lists every keyboard shortcut. Reachable via `?` and from
 * the first-run coach overlay. Click-outside or the explicit Close
 * button dismisses; Esc handling is wired on the page so it stacks
 * properly with the quickbar / context menu.
 */
export function HelpOverlay({ onClose }: Props) {
  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 px-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-[24px] border border-white/20 dark:border-white/10 bg-white/40 dark:bg-black/40 backdrop-blur-xl p-6 shadow-[0_12px_40px_rgba(0,0,0,0.15)]"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="font-display text-lg">Shortcuts</h2>
        <dl className="mt-3 space-y-2 text-sm">
          <Row k="←" v="Back" />
          <Row k="→" v="Forward" />
          <Row k="Backspace" v="Back (Shift = forward)" />
          <Row k="M" v="Toggle map view" />
          <Row k="T" v="Toggle time-scrubber" />
          <Row k="K" v="Toggle codex" />
          <Row k="/" v="Jump to page…" />
          <Row k="?" v="This help" />
          <Row k="Esc" v="Close overlay" />
          <Row k="Right-click" v="Page menu" />
          <Row k="⌘/Ctrl-click" v="Click with a note" />
          <Row k="Shift-drag" v="Circle a region to focus on it" />
        </dl>
        <button
          type="button"
          className="mt-5 w-full rounded-full border border-white/20 dark:border-white/10 bg-white/10 dark:bg-black/10 py-2 text-xs font-semibold hover:bg-white/20 dark:hover:bg-black/20 hover:scale-105 active:scale-95 transition-all text-[var(--color-ink)]"
          onClick={onClose}
        >
          Close
        </button>
      </div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="font-mono text-xs opacity-80">{k}</dt>
      <dd className="text-sm">{v}</dd>
    </div>
  );
}
