"use client";

import type { ChangeEvent, FormEvent, RefObject } from "react";
import type { ImageTier } from "@openflipbook/config";

import {
  SUPPORTED_LOCALES,
  type LocaleStrings,
  type SupportedLocale,
} from "@/lib/i18n";
import { THEMES, type Theme } from "@/hooks/usePersistedTheme";

const TIERS: readonly ImageTier[] = ["fast", "balanced", "pro"] as const;

interface Props {
  t: LocaleStrings;
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  fileInputRef: RefObject<HTMLInputElement | null>;
  onFileInputChange: (e: ChangeEvent<HTMLInputElement>) => void;
  busy: boolean;
  outputLocale: SupportedLocale;
  setOutputLocale: (l: SupportedLocale) => void;
  theme: Theme;
  setTheme: (t: Theme) => void;
  imageTier: ImageTier;
  setImageTier: (t: ImageTier) => void;
}

export function QueryToolbar({
  t,
  input,
  onInputChange,
  onSubmit,
  fileInputRef,
  onFileInputChange,
  busy,
  outputLocale,
  setOutputLocale,
  theme,
  setTheme,
  imageTier,
  setImageTier,
}: Props) {
  return (
    <>
      <form
        onSubmit={onSubmit}
        className="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-2 rounded-[24px] border border-black/10 bg-white/72 px-3 py-2 shadow-[0_18px_60px_rgba(15,23,42,0.10)] backdrop-blur-2xl transition-all dark:border-white/10 dark:bg-white/10 sm:gap-3 sm:rounded-full sm:px-4"
      >
        <input
          autoFocus
          className="min-w-[12rem] flex-1 rounded-full bg-transparent px-2 py-2 text-sm font-medium text-[var(--color-ink)] outline-none placeholder:text-[var(--color-ink)]/42"
          placeholder={t.placeholder}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={busy}
          className="rounded-full border border-black/10 bg-white/55 px-3.5 py-2 text-xs font-semibold text-[var(--color-ink)] transition-all hover:bg-white/90 disabled:opacity-40 dark:border-white/10 dark:bg-white/10 dark:hover:bg-white/15"
          title="Upload an image as the starting page. Tap on it to explore regions."
        >
          {t.upload}
        </button>

        <select
          value={outputLocale}
          onChange={(e) => setOutputLocale(e.target.value as SupportedLocale)}
          disabled={busy}
          aria-label={t.langLabel}
          title={t.langLabel}
          className="cursor-pointer rounded-full border border-black/10 bg-white/45 px-3 py-2 text-xs font-semibold text-[var(--color-ink)] transition-all hover:bg-white/80 disabled:opacity-40 dark:border-white/10 dark:bg-white/10 dark:hover:bg-white/15"
        >
          {SUPPORTED_LOCALES.map((loc) => (
            <option key={loc} value={loc} className="bg-white text-black">
              {loc === "auto" ? t.langAuto : loc}
            </option>
          ))}
        </select>

        <div
          role="group"
          aria-label="Theme"
          className="flex items-center rounded-full border border-black/10 bg-black/[0.035] p-0.5 text-xs dark:border-white/10 dark:bg-white/5"
          title="Theme - light / graphite / dark"
        >
          {THEMES.map((th) => (
            <button
              key={th}
              type="button"
              onClick={() => setTheme(th)}
              aria-pressed={theme === th}
              className={
                "rounded-full px-3 py-1.5 text-xs font-semibold transition-all " +
                (theme === th
                  ? "bg-white text-[var(--color-ink)] shadow-sm dark:bg-black"
                  : "text-[var(--color-ink)]/62 hover:bg-white/55 hover:text-[var(--color-ink)] dark:hover:bg-white/10")
              }
            >
              {th === "light"
                ? t.themeLight
                : th === "graphite"
                  ? t.themeGraphite
                  : t.themeDark}
            </button>
          ))}
        </div>

        <div
          role="group"
          aria-label="Image quality tier"
          className="flex items-center rounded-full border border-black/10 bg-black/[0.035] p-0.5 text-xs dark:border-white/10 dark:bg-white/5"
          title="Image quality tier - fast, balanced, pro"
        >
          <span className="px-2 py-1 text-[10px] font-bold text-[var(--color-ink)]/45">
            image
          </span>
          {TIERS.map((tier) => (
            <button
              key={tier}
              type="button"
              onClick={() => setImageTier(tier)}
              disabled={busy}
              aria-pressed={imageTier === tier}
              className={
                "rounded-full px-3 py-1.5 text-xs font-semibold transition-all disabled:opacity-40 " +
                (imageTier === tier
                  ? "bg-white text-[var(--color-ink)] shadow-sm dark:bg-black"
                  : "text-[var(--color-ink)]/62 hover:bg-white/55 hover:text-[var(--color-ink)] dark:hover:bg-white/10")
              }
            >
              {tier}
            </button>
          ))}
        </div>

        <button
          type="submit"
          disabled={busy || input.trim().length === 0}
          className="rounded-full bg-[var(--color-ink)] px-5 py-2.5 text-xs font-bold text-[var(--color-canvas)] shadow-sm transition-all hover:scale-[1.02] hover:opacity-95 active:scale-95 disabled:opacity-40"
        >
          {busy ? t.generating : t.go}
        </button>
      </form>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onFileInputChange}
      />
    </>
  );
}
