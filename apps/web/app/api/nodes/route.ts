import { NextResponse } from "next/server";
import { insertNode } from "@/lib/db";
import { decodeDataUrl, uploadJpeg } from "@/lib/r2";
import { readServerEnv } from "@/lib/env";
import {
  createEphemeralNodeResponse,
  hasRemoteNodePersistence,
  validateCreateNodeBody,
  type CreateNodeBody,
} from "@/lib/node-persistence";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const env = readServerEnv();
  const body = (await req.json()) as CreateNodeBody;
  const validationError = validateCreateNodeBody(body);
  if (validationError) {
    return NextResponse.json(
      { error: validationError },
      { status: 400 }
    );
  }

  if (!hasRemoteNodePersistence(env)) {
    return NextResponse.json(createEphemeralNodeResponse(body));
  }

  const decoded = decodeDataUrl(body.image_data_url);
  const extension = decoded.contentType === "image/png" ? "png" : "jpg";
  const keyPrefix = body.session_id.replace(/[^a-zA-Z0-9._-]/g, "_");
  const objectKey = `${keyPrefix}/${crypto.randomUUID()}.${extension}`;

  const uploaded = await uploadJpeg(objectKey, decoded.bytes, decoded.contentType);

  const row = await insertNode({
    parent_id: body.parent_id ?? null,
    session_id: body.session_id,
    query: body.query,
    page_title: body.page_title,
    image_key: uploaded.key,
    image_model: body.image_model,
    prompt_author_model: body.prompt_author_model,
    aspect_ratio: body.aspect_ratio ?? "16:9",
    final_prompt: body.final_prompt ?? null,
    click_in_parent: body.click_in_parent ?? null,
    sources: Array.isArray(body.sources) ? body.sources.slice(0, 3) : null,
  });

  return NextResponse.json({
    id: row.id,
    image_url: uploaded.url,
    created_at: row.created_at,
  });
}
