"""Call 1: findings extraction via Pydantic AI."""

from typing import Any

from pydantic_ai import Agent, BinaryContent

from medsee.core.config import Settings
from medsee.llm.openai_model import create_openai_chat_model
from medsee.models.findings import FindingsResult
from medsee.models.intake import IntakeMetadata
from medsee.services.image_grid import GRID_DIVISIONS, add_coordinate_grid

FINDINGS_INSTRUCTIONS = f"""You are a radiology AI assistant analyzing medical images.
The study image includes a {GRID_DIVISIONS}x{GRID_DIVISIONS} reference grid
(columns A–J, rows 1–{GRID_DIVISIONS}). Each cell spans 0.1 normalized units.

Extract structured findings with:
- location: anatomical location of the finding
- description: concise clinical description
- severity: mild, moderate, or severe
- confidence_score: float between 0 and 1
- region: bounding box using normalized coordinates (0–1) relative to the full
  image: x = left edge, y = top edge, width, height. Use the grid to localize
  each finding, then convert the covered cells into one tight box.
  Omit region only if localization is impossible.

Return only structured output matching the FindingsResult schema."""


def create_findings_agent(settings: Settings) -> Agent[None, FindingsResult]:
    model = create_openai_chat_model(settings)
    return Agent(
        model,
        output_type=FindingsResult,
        instructions=FINDINGS_INSTRUCTIONS,
    )


async def extract_findings(
    agent: Agent[None, FindingsResult],
    image_bytes: bytes,
    content_type: str,
    metadata: IntakeMetadata,
    pipeline_config: dict[str, Any],
) -> FindingsResult:
    """Run Call 1: analyze the image and return structured findings."""
    prompt = (
        f"Analyze this {metadata.modality} study of the {metadata.body_part}.\n"
        f"Clinical context: {metadata.clinical_context}\n"
        f"Pipeline: {pipeline_config.get('description', 'standard imaging pipeline')}\n"
        "Extract all significant findings."
    )
    gridded_image = add_coordinate_grid(image_bytes)
    result = await agent.run(
        [
            prompt,
            BinaryContent(data=gridded_image, media_type="image/jpeg"),
        ]
    )
    return result.output
