import { describe, expect, it, vi } from "vitest";
import {
  createEphemeralNodeResponse,
  hasRemoteNodePersistence,
  validateCreateNodeBody,
  type CreateNodeBody,
} from "./node-persistence";

const env = {
  MODAL_API_URL: "https://backend.example",
  MONGODB_URI: null,
  MONGODB_DB: null,
  R2_ACCOUNT_ID: null,
  R2_ACCESS_KEY_ID: null,
  R2_SECRET_ACCESS_KEY: null,
  R2_BUCKET: null,
  R2_PUBLIC_BASE_URL: null,
};

const body: CreateNodeBody = {
  parent_id: null,
  session_id: "session_1",
  query: "Hangzhou West Lake",
  page_title: "Hangzhou West Lake",
  image_data_url: "data:image/jpeg;base64,abc",
  image_model: "test-image",
  prompt_author_model: "test-llm",
};

describe("hasRemoteNodePersistence", () => {
  it("requires MongoDB and an R2 bucket before using the durable path", () => {
    expect(hasRemoteNodePersistence(env)).toBe(false);
    expect(
      hasRemoteNodePersistence({
        ...env,
        MONGODB_URI: "mongodb://localhost:27017",
        MONGODB_DB: "openflipbook",
        R2_BUCKET: "openflipbook",
      }),
    ).toBe(true);
  });
});

describe("validateCreateNodeBody", () => {
  it("keeps the original required fields", () => {
    expect(validateCreateNodeBody(body)).toBeNull();
    expect(validateCreateNodeBody({ ...body, image_data_url: "" })).toMatch(
      "missing required fields",
    );
  });
});

describe("createEphemeralNodeResponse", () => {
  it("returns a local node id and keeps the generated image usable", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-4000-8000-000000000001");
    const response = createEphemeralNodeResponse(body);

    expect(response.id).toBe("local_00000000-0000-4000-8000-000000000001");
    expect(response.image_url).toBe(body.image_data_url);
    expect(response.persistence).toBe("ephemeral");
    expect(new Date(response.created_at).toString()).not.toBe("Invalid Date");
  });
});
