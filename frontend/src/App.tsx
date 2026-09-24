import { useState } from "react";
import { submitReport } from "./api";
import ImageFindingsViewer from "./ImageFindingsViewer";
import type { PipelineResponse, UrgencyFlag } from "./types";

const MODALITIES = ["MRI", "CT", "XRAY"] as const;

function urgencyStyles(urgency: UrgencyFlag) {
  if (urgency === "CRITICAL") return "bg-flame text-surface";
  if (urgency === "IMPORTANT") return "bg-ink text-surface";
  return "bg-muted text-ink";
}

function confidenceLabel(value: number | null) {
  if (value === null) return "—";
  return `${Math.round(value * 100)}%`;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [modality, setModality] = useState<(typeof MODALITIES)[number]>("MRI");
  const [bodyPart, setBodyPart] = useState("lumbar spine");
  const [clinicalContext, setClinicalContext] = useState(
    "chronic low back pain with left leg radiculopathy",
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [activeFindingIndex, setActiveFindingIndex] = useState<number | null>(null);

  const canSubmit = Boolean(file && bodyPart.trim() && clinicalContext.trim() && !loading);

  function onFileChange(next: File | null) {
    if (preview) URL.revokeObjectURL(preview);
    setFile(next);
    setPreview(next ? URL.createObjectURL(next) : null);
    setError(null);
    setResult(null);
    setActiveFindingIndex(null);
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const response = await submitReport(file, {
        modality,
        body_part: bodyPart.trim(),
        clinical_context: clinicalContext.trim(),
      });
      setResult(response);
      setActiveFindingIndex(null);
    } catch (err) {
      setResult(null);
      setActiveFindingIndex(null);
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-canvas text-ink">
      <header className="shrink-0 border-b border-muted bg-surface">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-6 py-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-ink font-display text-lg font-bold text-flame">
            M
          </div>
          <div>
            <p className="font-display text-xl font-bold tracking-tight">Medsee</p>
            <p className="text-sm text-ink/60">Radiology report pipeline</p>
          </div>
          <div className="ml-auto hidden items-center gap-2 rounded-full border border-muted px-3 py-1 font-mono text-xs text-ink/70 sm:flex">
            <span className="h-2 w-2 rounded-full bg-flame" />
            POST /reports
          </div>
        </div>
      </header>

      <main className="scroll-pane mx-auto grid min-h-0 w-full max-w-7xl flex-1 gap-4 overflow-y-auto px-6 py-4 lg:grid-cols-[minmax(380px,42%)_1fr] lg:overflow-hidden">
        <section className="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-muted bg-surface p-4 shadow-[0_20px_60px_-40px_rgba(25,25,25,0.45)] lg:max-h-full">
          <div className="mb-3 flex shrink-0 items-center gap-3">
            <span className="h-8 w-1 rounded-full bg-flame" />
            <h2 className="font-display text-lg font-bold">Intake</h2>
          </div>

          <form className="flex min-h-0 flex-1 flex-col gap-3 overflow-hidden" onSubmit={onSubmit}>
            <ImageFindingsViewer
              imageUrl={preview}
              fileName={file?.name ?? null}
              findings={result?.findings}
              activeIndex={activeFindingIndex}
              onSelect={setActiveFindingIndex}
              onFileSelect={onFileChange}
              loading={loading}
            />

            <button
              type="submit"
              disabled={!canSubmit}
              className="shrink-0 w-full rounded-lg bg-flame px-4 py-2.5 font-semibold text-surface transition hover:bg-flame-dark disabled:cursor-not-allowed disabled:bg-muted disabled:text-ink/40"
            >
              {loading ? "Running pipeline…" : "Generate report"}
            </button>

            <div className="shrink-0 space-y-2 border-t border-muted pt-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-ink/50">
                    Modality
                  </label>
                  <select
                    value={modality}
                    onChange={(event) =>
                      setModality(event.target.value as (typeof MODALITIES)[number])
                    }
                    className="w-full rounded-lg border border-muted bg-canvas px-2.5 py-2 text-sm outline-none transition focus:border-flame focus:ring-2 focus:ring-flame/20"
                  >
                    {MODALITIES.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-ink/50">
                    Body part
                  </label>
                  <input
                    value={bodyPart}
                    onChange={(event) => setBodyPart(event.target.value)}
                    className="w-full rounded-lg border border-muted bg-canvas px-2.5 py-2 text-sm outline-none transition focus:border-flame focus:ring-2 focus:ring-flame/20"
                  />
                </div>
              </div>

              <div>
                <label className="mb-1 block text-[10px] font-semibold uppercase tracking-wide text-ink/50">
                  Clinical context
                </label>
                <textarea
                  value={clinicalContext}
                  onChange={(event) => setClinicalContext(event.target.value)}
                  rows={2}
                  className="w-full resize-none rounded-lg border border-muted bg-canvas px-2.5 py-2 text-sm outline-none transition focus:border-flame focus:ring-2 focus:ring-flame/20"
                />
              </div>
            </div>

            {error ? (
              <div className="shrink-0 rounded-lg border border-flame/30 bg-flame/10 px-3 py-2 text-sm text-flame-dark">
                {error}
              </div>
            ) : null}
          </form>
        </section>

        <section className="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-muted bg-surface p-5 lg:max-h-full">
          {!result && !loading ? (
            <div className="flex min-h-[280px] flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-muted bg-canvas px-6 text-center lg:min-h-0">
              <p className="font-display text-2xl font-bold text-ink/80">Report output</p>
              <p className="mt-2 max-w-sm text-sm text-ink/50">
                Upload a study and run the pipeline to see findings, impression, and urgency here.
              </p>
            </div>
          ) : null}

          {loading ? (
            <div className="flex min-h-[280px] flex-1 flex-col items-center justify-center gap-4 lg:min-h-0">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-muted border-t-flame" />
              <p className="font-mono text-sm text-ink/60">findings → validate → report</p>
            </div>
          ) : null}

          {result ? (
            <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden">
              <div className="flex shrink-0 flex-wrap items-start justify-between gap-3 border-b border-muted pb-4">
                <div>
                  <p className="font-display text-2xl font-bold">
                    {result.metadata.modality} · {result.metadata.body_part}
                  </p>
                  <p className="mt-1 text-sm text-ink/60">{result.metadata.clinical_context}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.report ? (
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${urgencyStyles(result.report.urgency)}`}
                    >
                      {result.report.urgency}
                    </span>
                  ) : null}
                  <span className="rounded-full border border-muted bg-canvas px-3 py-1 font-mono text-xs">
                    conf {confidenceLabel(result.confidence)}
                  </span>
                  <span className="rounded-full border border-muted bg-canvas px-3 py-1 font-mono text-xs">
                    {result.pipeline_config}
                  </span>
                </div>
              </div>

              <div className="grid min-h-0 flex-1 gap-4 overflow-hidden lg:grid-cols-2">
                <div className="flex min-h-0 flex-col rounded-xl border border-muted bg-canvas">
                  <h3 className="shrink-0 px-4 pt-4 pb-2 font-display text-lg font-bold leading-snug">
                    Findings
                  </h3>
                  {result.findings.length === 0 ? (
                    <p className="px-4 pb-4 text-sm text-ink/50">No findings returned.</p>
                  ) : (
                    <ul className="scroll-pane min-h-0 flex-1 space-y-3 overflow-y-auto px-4 pb-4">
                      {result.findings.map((finding, index) => (
                        <li
                          key={`${finding.location}-${index}`}
                          className={`rounded-lg border bg-surface p-3 transition ${
                            activeFindingIndex === index
                              ? "border-flame ring-2 ring-flame/20"
                              : "border-muted"
                          }`}
                          onMouseEnter={() => setActiveFindingIndex(index)}
                          onMouseLeave={() => setActiveFindingIndex(null)}
                        >
                          <div className="mb-1 flex items-center justify-between gap-2">
                            <span className="font-semibold">
                              <span className="mr-2 inline-flex h-5 w-5 items-center justify-center rounded-full bg-ink font-mono text-xs text-surface">
                                {index + 1}
                              </span>
                              {finding.location}
                            </span>
                            <span className="font-mono text-xs text-ink/50">
                              {Math.round(finding.confidence_score * 100)}%
                            </span>
                          </div>
                          <p className="text-sm text-ink/80">{finding.description}</p>
                          <p className="mt-2 text-xs uppercase tracking-wide text-flame">
                            {finding.severity}
                            {!finding.region ? (
                              <span className="ml-2 normal-case text-ink/40">· not localized</span>
                            ) : null}
                          </p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="flex min-h-0 flex-col rounded-xl border border-muted bg-canvas">
                  <h3 className="shrink-0 px-4 pt-4 pb-2 font-display text-lg font-bold leading-snug">
                    Report
                  </h3>
                  {result.report ? (
                    <div className="scroll-pane min-h-0 flex-1 space-y-4 overflow-y-auto px-4 pb-4">
                      <div>
                        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-ink/50">
                          Impression
                        </p>
                        <p className="text-sm leading-relaxed text-ink/85">
                          {result.report.impression}
                        </p>
                      </div>
                      <div>
                        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink/50">
                          Recommendations
                        </p>
                        <ul className="space-y-2">
                          {result.report.recommendations.map((item, index) => (
                            <li
                              key={index}
                              className="flex gap-2 text-sm leading-relaxed text-ink/85"
                            >
                              <span className="font-mono text-flame">{index + 1}.</span>
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-ink/50">Report step did not complete.</p>
                  )}
                </div>
              </div>
            </div>
          ) : null}
        </section>
      </main>
    </div>
  );
}
