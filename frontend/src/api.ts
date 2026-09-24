import type { PipelineResponse } from "./types";

export async function submitReport(
  image: File,
  metadata: { modality: string; body_part: string; clinical_context: string },
): Promise<PipelineResponse> {
  const form = new FormData();
  form.append("image", image);
  form.append("metadata", JSON.stringify(metadata));

  const response = await fetch("/reports", {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string | { msg: string }[] }
      | null;
    const detail =
      typeof body?.detail === "string"
        ? body.detail
        : Array.isArray(body?.detail)
          ? body.detail.map((item) => item.msg).join("; ")
          : `Request failed (${response.status})`;
    throw new Error(detail);
  }

  return response.json() as Promise<PipelineResponse>;
}
