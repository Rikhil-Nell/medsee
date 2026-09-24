import { useCallback, useEffect, useId, useRef, useState } from "react";
import type { Finding } from "./types";

function severityColor(severity: string) {
  const value = severity.toLowerCase();
  if (value.includes("severe")) return "#c93f18";
  if (value.includes("moderate")) return "#f15025";
  return "#191919";
}

interface ImageLayout {
  left: number;
  top: number;
  width: number;
  height: number;
}

interface ImageFindingsViewerProps {
  imageUrl: string | null;
  fileName: string | null;
  findings?: Finding[];
  activeIndex: number | null;
  onSelect: (index: number | null) => void;
  onFileSelect: (file: File | null) => void;
  loading?: boolean;
}

export default function ImageFindingsViewer({
  imageUrl,
  fileName,
  findings = [],
  activeIndex,
  onSelect,
  onFileSelect,
  loading = false,
}: ImageFindingsViewerProps) {
  const inputId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const [layout, setLayout] = useState<ImageLayout | null>(null);
  const [overlayReveal, setOverlayReveal] = useState(100);
  const [controlsVisible, setControlsVisible] = useState(false);

  const annotated = findings.filter((finding) => finding.region);
  const hasOverlays = findings.length > 0 && annotated.length > 0;
  const overlaysVisible = hasOverlays && overlayReveal > 0;

  const updateLayout = useCallback(() => {
    const container = containerRef.current;
    const image = imageRef.current;
    if (!container || !image || !image.naturalWidth || !image.naturalHeight) return;

    const scale = Math.min(
      container.clientWidth / image.naturalWidth,
      container.clientHeight / image.naturalHeight,
    );
    const width = image.naturalWidth * scale;
    const height = image.naturalHeight * scale;

    setLayout({
      left: (container.clientWidth - width) / 2,
      top: (container.clientHeight - height) / 2,
      width,
      height,
    });
  }, []);

  useEffect(() => {
    updateLayout();
    window.addEventListener("resize", updateLayout);
    return () => window.removeEventListener("resize", updateLayout);
  }, [updateLayout, imageUrl]);

  useEffect(() => {
    if (hasOverlays) setOverlayReveal(100);
  }, [hasOverlays, findings]);

  useEffect(() => {
    setControlsVisible(false);
  }, [imageUrl]);

  function toggleControls() {
    setControlsVisible((current) => !current);
  }

  function stopControlClick(event: React.MouseEvent | React.KeyboardEvent) {
    event.stopPropagation();
  }

  function toggleOverlays(event: React.MouseEvent) {
    event.stopPropagation();
    setOverlayReveal((current) => (current > 0 ? 0 : 100));
  }

  const topControlClass = controlsVisible
    ? "pointer-events-auto translate-y-0 opacity-100"
    : "pointer-events-none -translate-y-1 opacity-0";

  const bottomControlClass = controlsVisible
    ? "pointer-events-auto translate-y-0 opacity-100"
    : "pointer-events-none translate-y-1 opacity-0";

  return (
    <div className="flex min-h-[260px] min-w-0 flex-1 flex-col overflow-hidden rounded-xl border border-muted bg-ink">
      <input
        id={inputId}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(event) => onFileSelect(event.target.files?.[0] ?? null)}
      />

      <div
        ref={containerRef}
        className="relative min-h-0 flex-1 bg-black/90"
        onClick={imageUrl ? toggleControls : undefined}
        onKeyDown={
          imageUrl
            ? (event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  toggleControls();
                }
              }
            : undefined
        }
        role={imageUrl ? "button" : undefined}
        tabIndex={imageUrl ? 0 : undefined}
        aria-label={imageUrl ? "Toggle study viewer controls" : undefined}
      >
        {!imageUrl ? (
          <label
            htmlFor={inputId}
            className="flex h-full min-h-[220px] w-full cursor-pointer flex-col items-center justify-center"
          >
            <div className="mb-2 flex h-14 w-14 items-center justify-center rounded-full bg-white/10 font-display text-2xl text-white/50">
              +
            </div>
            <span className="text-sm font-medium text-white/80">Drop image or browse</span>
          </label>
        ) : (
          <>
            <img
              ref={imageRef}
              src={imageUrl}
              alt="Study"
              className="h-full w-full object-contain"
              draggable={false}
              onLoad={updateLayout}
            />

            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-white/20 border-t-flame" />
              </div>
            ) : null}

            {overlaysVisible && layout ? (
              <div
                className="absolute inset-0 overflow-hidden"
                style={{ clipPath: `inset(0 ${100 - overlayReveal}% 0 0)` }}
              >
                {findings.map((finding, index) => {
                  if (!finding.region) return null;
                  const { x, y, width, height } = finding.region;
                  const active = activeIndex === index;
                  const color = severityColor(finding.severity);
                  const pct = Math.round(finding.confidence_score * 100);

                  return (
                    <div key={`overlay-${finding.location}-${index}`}>
                      <div
                        className="pointer-events-none absolute border-2"
                        style={{
                          left: layout.left + x * layout.width,
                          top: layout.top + y * layout.height,
                          width: width * layout.width,
                          height: height * layout.height,
                          borderColor: color,
                          backgroundColor: active ? `${color}55` : `${color}28`,
                        }}
                      />
                      <div
                        className="pointer-events-none absolute px-1.5 py-0.5 font-mono text-[10px] font-medium text-white"
                        style={{
                          left: layout.left + x * layout.width,
                          top: Math.max(layout.top + y * layout.height - 18, layout.top),
                          backgroundColor: color,
                        }}
                      >
                        {index + 1} · {pct}%
                      </div>
                      {overlayReveal > 40 ? (
                        <button
                          type="button"
                          aria-label={`Highlight ${finding.location}`}
                          className="absolute border-0 bg-transparent p-0"
                          style={{
                            left: layout.left + x * layout.width,
                            top: layout.top + y * layout.height,
                            width: width * layout.width,
                            height: height * layout.height,
                          }}
                          onClick={stopControlClick}
                          onMouseEnter={() => onSelect(index)}
                          onMouseLeave={() => onSelect(null)}
                        />
                      ) : null}
                    </div>
                  );
                })}
              </div>
            ) : null}

            {hasOverlays && overlayReveal > 0 && overlayReveal < 100 ? (
              <div
                className={`pointer-events-none absolute top-0 z-10 w-0.5 bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)] ${
                  controlsVisible ? "bottom-14" : "bottom-0"
                }`}
                style={{ left: `${overlayReveal}%` }}
              />
            ) : null}

            <div
              className={`absolute inset-x-0 top-0 z-20 border-b border-white/10 bg-gradient-to-b from-black/85 to-black/40 px-3 py-2 transition-all duration-200 ${topControlClass}`}
              onClick={stopControlClick}
              onKeyDown={stopControlClick}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="truncate font-mono text-xs text-white/70">
                  {fileName ?? "Study"}
                </p>
                <div className="flex shrink-0 items-center gap-2">
                  {hasOverlays ? (
                    <>
                      <p className="hidden font-mono text-xs text-white/60 sm:block">
                        {annotated.length}/{findings.length} localized
                      </p>
                      <button
                        type="button"
                        onClick={toggleOverlays}
                        className="rounded-md border border-white/15 px-2 py-0.5 text-xs text-white/80 transition hover:border-flame hover:text-flame"
                      >
                        {overlaysVisible ? "Hide boxes" : "Show boxes"}
                      </button>
                    </>
                  ) : (
                    <p className="text-xs text-white/40">PNG, JPG, WEBP</p>
                  )}
                  <label
                    htmlFor={inputId}
                    className="cursor-pointer text-xs text-flame hover:text-flame/80"
                    onClick={stopControlClick}
                  >
                    Change
                  </label>
                </div>
              </div>
            </div>

            {hasOverlays ? (
              <div
                className={`absolute inset-x-0 bottom-0 z-20 border-t border-white/10 bg-gradient-to-t from-black/85 to-black/40 px-3 py-2 transition-all duration-200 ${bottomControlClass}`}
                onClick={stopControlClick}
                onKeyDown={stopControlClick}
              >
                <div className="mb-1 flex items-center justify-between text-[10px] uppercase tracking-wide text-white/50">
                  <span>Clean</span>
                  <span>Annotated</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={overlayReveal}
                  onChange={(event) => setOverlayReveal(Number(event.target.value))}
                  onClick={stopControlClick}
                  onMouseDown={stopControlClick}
                  className="h-1.5 w-full cursor-ew-resize accent-flame"
                  aria-label="Compare clean and annotated views"
                />
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}
