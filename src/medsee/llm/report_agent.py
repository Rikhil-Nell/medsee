"""Call 2: report assembly via Pydantic AI."""

from pydantic_ai import Agent

from medsee.core.config import Settings
from medsee.llm.openai_model import create_openai_chat_model
from medsee.models.findings import FindingsResult
from medsee.models.intake import IntakeMetadata
from medsee.models.report import ReportResult

REPORT_INSTRUCTIONS = """You are a radiology reporting assistant.
Given validated structured findings from an imaging study, assemble a concise report with:
- impression: summary clinical impression
- recommendations: actionable follow-up recommendations as a list
- urgency: one of CRITICAL, IMPORTANT, or ROUTINE

Base urgency on finding severity and clinical context. Return only structured output."""


def create_report_agent(settings: Settings) -> Agent[None, ReportResult]:
    model = create_openai_chat_model(settings)
    return Agent(
        model,
        output_type=ReportResult,
        instructions=REPORT_INSTRUCTIONS,
    )


async def assemble_report(
    agent: Agent[None, ReportResult],
    findings: FindingsResult,
    metadata: IntakeMetadata,
) -> ReportResult:
    """Run Call 2: generate a report from validated findings."""
    prompt = (
        f"Assemble a radiology report from these validated findings.\n\n"
        f"Study: {metadata.modality} {metadata.body_part}\n"
        f"Clinical context: {metadata.clinical_context}\n\n"
        f"Findings JSON:\n{findings.model_dump_json()}"
    )
    result = await agent.run(prompt)
    return result.output
