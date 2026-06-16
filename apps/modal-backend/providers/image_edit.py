"""Direct Google Gemini-backed image editing.

Bypasses Fal.ai to use Gemini's editing capabilities (if supported)
or fallback to regenerating via Imagen 3.
"""

from __future__ import annotations

from .image import GeneratedImage, generate_image


async def edit_image(
    *,
    image_data_url: str,
    instruction: str | None = None,
    prompt: str | None = None,
    tier: str | None = None,
    model_override: str | None = None,
) -> GeneratedImage:
    """
    Fallback to simple generation for now as Imagen editing API
    differs from standard generation.
    """
    # In a full implementation, we would use Gemini's vision-to-image
    # or Imagen's edit API. For now, we reuse the generate logic
    # to keep the system running.
    edit_prompt = instruction or prompt
    if not edit_prompt:
        raise RuntimeError("edit_image requires instruction or prompt")

    return await generate_image(
        prompt=edit_prompt,
        aspect_ratio="16:9", # Default
        tier=tier,
        model_override=model_override
    )
