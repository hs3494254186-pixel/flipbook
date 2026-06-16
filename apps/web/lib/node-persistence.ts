import type { ServerEnv } from "./env";

export interface CreateNodeBody {
  parent_id?: string | null;
  session_id: string;
  query: string;
  page_title: string;
  image_data_url: string;
  image_model: string;
  prompt_author_model: string;
  aspect_ratio?: string;
  final_prompt?: string | null;
  click_in_parent?: { x_pct: number; y_pct: number } | null;
  sources?: { url: string; title: string | null }[] | null;
}

export function hasRemoteNodePersistence(env: ServerEnv): boolean {
  return Boolean(env.MONGODB_URI && env.MONGODB_DB && env.R2_BUCKET);
}

export function validateCreateNodeBody(body: Partial<CreateNodeBody>): string | null {
  if (!body.image_data_url || !body.session_id || !body.page_title) {
    return "missing required fields: session_id, page_title, image_data_url";
  }
  return null;
}

export function createEphemeralNodeResponse(body: CreateNodeBody): {
  id: string;
  image_url: string;
  created_at: string;
  persistence: "ephemeral";
} {
  return {
    id: `local_${crypto.randomUUID()}`,
    image_url: body.image_data_url,
    created_at: new Date().toISOString(),
    persistence: "ephemeral",
  };
}
