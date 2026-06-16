"use client";

interface Props {
  statusMsg: string | null;
}

export function GeneratingBanner({ statusMsg }: Props) {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-end bg-black/25 backdrop-blur-[1px]">
      <div className="m-4 flex items-center gap-3 rounded-full border border-white/20 bg-black/72 px-4 py-2 text-sm font-medium text-white shadow-lg">
        <span className="inline-block h-2.5 w-2.5 animate-pulse rounded-full bg-white/90" />
        <span>{statusMsg ?? "Generating..."}</span>
      </div>
    </div>
  );
}
