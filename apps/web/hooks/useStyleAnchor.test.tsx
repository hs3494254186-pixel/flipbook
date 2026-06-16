import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { isPresetAnchor, presetNodeId, STYLE_PRESETS } from "@/lib/styles";

import { useStyleAnchor } from "./useStyleAnchor";

const SESSION = "test-session-x";

function key(): string {
  return `openflipbook.styleAnchor.${SESSION}`;
}

afterEach(() => {
  window.localStorage.clear();
});

describe("useStyleAnchor.setFromPreset", () => {
  it("stores a synthetic anchor with the preset's prompt fragment", async () => {
    const { result } = renderHook(() => useStyleAnchor(SESSION));
    await waitFor(() => expect(result.current.anchor).toBeNull());

    act(() => result.current.setFromPreset("flipbook"));

    const a = result.current.anchor;
    expect(a).not.toBeNull();
    expect(a!.nodeId).toBe(presetNodeId("flipbook"));
    const flipbook = STYLE_PRESETS.find((p) => p.id === "flipbook");
    expect(a!.style).toBe(flipbook!.promptFragment);
  });

  it("persists the preset choice across remounts", async () => {
    const first = renderHook(() => useStyleAnchor(SESSION));
    await waitFor(() => expect(first.result.current.anchor).toBeNull());
    act(() => first.result.current.setFromPreset("cutaway"));

    const raw = window.localStorage.getItem(key());
    expect(raw).toBeTruthy();
    const parsed = JSON.parse(raw as string);
    expect(parsed.nodeId).toBe(presetNodeId("cutaway"));

    first.unmount();

    const second = renderHook(() => useStyleAnchor(SESSION));
    await waitFor(() => expect(second.result.current.anchor).not.toBeNull());
    expect(second.result.current.anchor!.nodeId).toBe(presetNodeId("cutaway"));
  });

  it("setFromPreset with an unknown id is a no-op", async () => {
    const { result } = renderHook(() => useStyleAnchor(SESSION));
    await waitFor(() => expect(result.current.anchor).toBeNull());

    act(() => result.current.setFromPreset("does-not-exist"));

    expect(result.current.anchor).toBeNull();
    expect(window.localStorage.getItem(key())).toBeNull();
  });

  it("isPresetAnchor identifies preset-backed anchors", () => {
    expect(isPresetAnchor(presetNodeId("studio"))).toBe(true);
    expect(isPresetAnchor("4a9c1b2e-1234-...")).toBe(false);
  });
});
