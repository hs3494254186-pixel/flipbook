"use client";

interface Props {
  onDismiss: () => void;
  onShowHelp: () => void;
}

export function FirstRunCoach({ onDismiss, onShowHelp }: Props) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 bottom-6 z-40 flex justify-center px-4"
    >
      <div className="pointer-events-auto flex items-center gap-3 rounded-full border border-black/10 bg-white/82 px-4 py-2 text-sm shadow-[0_18px_60px_rgba(15,23,42,0.16)] backdrop-blur-2xl dark:border-white/10 dark:bg-black/68">
        <span className="opacity-80">Click any region to explore.</span>
        <span className="opacity-35">/</span>
        <button
          type="button"
          onClick={onShowHelp}
          className="rounded-full border border-[var(--color-edge)] px-2 py-0.5 font-mono text-xs hover:bg-[var(--color-ink)]/10"
          title="Show all shortcuts"
        >
          ?
        </button>
        <span className="opacity-80">shortcuts</span>
        <span className="opacity-35">/</span>
        <span className="font-mono text-xs opacity-80">T</span>
        <span className="opacity-80">scrubber</span>
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss tip"
          className="ml-1 rounded-full px-2 py-0.5 text-xs font-semibold opacity-60 hover:opacity-100"
        >
          Done
        </button>
      </div>
    </div>
  );
}
