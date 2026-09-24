export type UrgencyFlag = "CRITICAL" | "IMPORTANT" | "ROUTINE";
export type StepStatus = "success" | "failed" | "skipped";

export interface FindingRegion {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Finding {
  location: string;
  description: string;
  severity: string;
  confidence_score: number;
  region?: FindingRegion | null;
}

export interface ReportResult {
  impression: string;
  recommendations: string[];
  urgency: UrgencyFlag;
}

export interface IntakeMetadata {
  modality: string;
  body_part: string;
  clinical_context: string;
}

export interface StepStatusDetail {
  step: string;
  status: StepStatus;
  detail?: string | null;
}

export interface PipelineResponse {
  findings: Finding[];
  report: ReportResult | null;
  metadata: IntakeMetadata;
  pipeline_config: string;
  step_statuses: StepStatusDetail[];
  confidence: number | null;
}

export interface ApiError {
  detail: string;
}
