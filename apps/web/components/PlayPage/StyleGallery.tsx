"use client";

import { STYLE_PRESETS } from "@/lib/styles";

interface Props {
  onPick: (presetId: string) => void;
  onSkip: () => void;
}

export function StyleGallery({ onPick, onSkip }: Props) {
  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col items-center gap-6 py-12">
      <div className="text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] opacity-45">
          Visual seed
        </p>
        <h2 className="mt-3 text-2xl font-semibold tracking-tight">
          Pick a style, or let the planner choose.
        </h2>
        <p className="mt-2 text-sm opacity-58">
          The selected look becomes the session anchor. You can re-pin any
          generated page later.
        </p>
      </div>

      <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-4">
        {STYLE_PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => onPick(p.id)}
            aria-label={p.name}
            className="group relative aspect-[4/3] overflow-hidden rounded-2xl text-left shadow-sm ring-1 ring-black/10 transition-transform hover:-translate-y-0.5 hover:shadow-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ink)]"
            style={{
              background: `linear-gradient(135deg, ${p.gradient[0]}, ${p.gradient[1]})`,
              color: p.textColor,
            }}
          >
            <span
              aria-hidden
              className="absolute inset-0 bg-gradient-to-b from-transparent to-black/55"
            />
            <span className="absolute bottom-3 left-3 z-10 text-xs font-semibold uppercase tracking-wider drop-shadow-sm">
              {p.name}
            </span>
          </button>
        ))}
      </div>

      <button
        type="button"
        onClick={onSkip}
        className="rounded-full border border-black/10 bg-white/60 px-4 py-2 text-sm font-medium opacity-70 transition hover:opacity-100 dark:border-white/10 dark:bg-white/10"
      >
        Skip, just give me a query box
      </button>
    </div>
  );
}
