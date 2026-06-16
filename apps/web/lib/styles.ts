export interface StylePreset {
  id: string;
  name: string;
  /** Short style descriptor concatenated into the page-generation prompt. */
  promptFragment: string;
  /** Two-stop CSS linear-gradient pair for the tile background. */
  gradient: [string, string];
  /** Text color over the tile background, tuned per preset. */
  textColor: string;
}

export const STYLE_PRESETS: readonly StylePreset[] = [
  {
    id: "flipbook",
    name: "Flipbook",
    promptFragment:
      "Flipbook.page demo style, generated pixels inside rounded browser chrome, light canvas, isometric scene, labels, arrows, callouts, insets",
    gradient: ["#f8fafc", "#dbeafe"],
    textColor: "#111827",
  },
  {
    id: "atlas",
    name: "Atlas",
    promptFragment:
      "modern visual atlas page, clean white canvas, annotated map-like layout, compact information panels, connector lines, clear clickable regions",
    gradient: ["#e0f2fe", "#bae6fd"],
    textColor: "#0f172a",
  },
  {
    id: "cutaway",
    name: "Cutaway",
    promptFragment:
      "architectural cutaway diagram, crisp black linework, soft fills, section labels, arrows, zoom insets, readable spatial hierarchy",
    gradient: ["#f1f5f9", "#cbd5e1"],
    textColor: "#111827",
  },
  {
    id: "dashboard",
    name: "Dashboard",
    promptFragment:
      "browser-native information dashboard inside the image, left-side table, small charts, labeled regions, clean Apple-like spacing",
    gradient: ["#f5f5f7", "#d1d5db"],
    textColor: "#111827",
  },
  {
    id: "blueprint",
    name: "Blueprint",
    promptFragment:
      "clean technical blueprint on a pale blue-white canvas, precise thin lines, callout labels, exploded views, numbered regions",
    gradient: ["#dbeafe", "#93c5fd"],
    textColor: "#0f172a",
  },
  {
    id: "notebook",
    name: "Notebook",
    promptFragment:
      "modern research notebook page, off-white canvas, neat hand-drawn diagrams, small annotations, arrows, tables, and margin notes",
    gradient: ["#fff7ed", "#fed7aa"],
    textColor: "#1f2937",
  },
  {
    id: "pixelmap",
    name: "Pixel Map",
    promptFragment:
      "light pixel-rendered browser page, small imperfect text, icons, region boxes, arrows, and a clean isometric map composition",
    gradient: ["#ecfeff", "#a7f3d0"],
    textColor: "#0f172a",
  },
  {
    id: "studio",
    name: "Studio",
    promptFragment:
      "Apple-like product studio diagram, soft gray canvas, restrained accent color, layered panels, precise labels, elegant spacing",
    gradient: ["#fafafa", "#e5e7eb"],
    textColor: "#111827",
  },
];

export const PRESET_ANCHOR_PREFIX = "preset:";

export function getStylePreset(id: string): StylePreset | undefined {
  return STYLE_PRESETS.find((p) => p.id === id);
}

export function presetNodeId(presetId: string): string {
  return `${PRESET_ANCHOR_PREFIX}${presetId}`;
}

export function isPresetAnchor(nodeId: string): boolean {
  return nodeId.startsWith(PRESET_ANCHOR_PREFIX);
}
