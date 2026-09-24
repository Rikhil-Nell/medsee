"""Draw a reference grid on study images to help vision models localize findings."""

from io import BytesIO

from PIL import Image, ImageDraw

GRID_DIVISIONS = 10
_GRID_COLUMNS = "ABCDEFGHIJ"


def add_coordinate_grid(image_bytes: bytes, divisions: int = GRID_DIVISIONS) -> bytes:
    """Return JPEG bytes with a semi-transparent coordinate grid overlay."""
    with Image.open(BytesIO(image_bytes)) as opened:
        base = opened.convert("RGBA")

    width, height = base.size
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for index in range(1, divisions):
        x = int(width * index / divisions)
        y = int(height * index / divisions)
        draw.line([(x, 0), (x, height)], fill=(241, 80, 37, 100), width=1)
        draw.line([(0, y), (width, y)], fill=(241, 80, 37, 100), width=1)

    columns = _GRID_COLUMNS[:divisions]
    for index, column in enumerate(columns):
        x = int(width * (index + 0.5) / divisions)
        draw.text((x - 4, 6), column, fill=(241, 80, 37, 220))

    for index in range(divisions):
        y = int(height * (index + 0.5) / divisions)
        draw.text((6, y - 6), str(index + 1), fill=(241, 80, 37, 220))

    composed = Image.alpha_composite(base, overlay)
    buffer = BytesIO()
    composed.convert("RGB").save(buffer, format="JPEG", quality=92)
    return buffer.getvalue()
