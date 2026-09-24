"""Tests for coordinate grid overlay."""

from medsee.services.image_grid import add_coordinate_grid
from tests.factories import MINIMAL_PNG


def test_add_coordinate_grid_returns_jpeg_bytes() -> None:
    gridded = add_coordinate_grid(MINIMAL_PNG)
    assert gridded.startswith(b"\xff\xd8\xff")
    assert len(gridded) > len(MINIMAL_PNG)
