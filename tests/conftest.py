"""
Pytest configuration and shared fixtures.

This module provides:
- Global pytest hooks
- Shared fixtures for test reuse
- Test utilities
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_cutter_dict():
    """Provide sample cutter data as dictionary."""
    return {
        "name": "10mm Carbide End Mill",
        "category": "end_mill",
        "subcategory": "square",
        "coating": "TiAlN",
        "substrate": "carbide",
        "diameter": 10.0,
        "length": 75.0,
        "flute_length": 30.0,
        "number_of_flutes": 4,
        "helix_angle": 30.0,
        "corner_radius": 0.0,
        "recommended_parameters": {
            "vc_steel": 120.0,
            "vc_aluminum": 200.0,
            "fz_steel": 0.05,
        },
        "usage_guidelines": [
            "Use for steel and stainless steel",
            "Avoid interrupted cuts",
        ],
        "compatible_materials": ["steel", "stainless_steel", "cast_iron"],
    }


@pytest.fixture
def sample_cutters_list():
    """Provide list of sample cutters for batch operations."""
    return [
        {
            "name": "6mm HSS Drill",
            "category": "drill",
            "diameter": 6.0,
            "length": 60.0,
            "flute_length": 30.0,
            "number_of_flutes": 2,
            "substrate": "hss",
            "compatible_materials": ["steel", "aluminum"],
        },
        {
            "name": "12mm Carbide Reamer",
            "category": "reamer",
            "diameter": 12.0,
            "length": 100.0,
            "flute_length": 50.0,
            "number_of_flutes": 6,
            "substrate": "carbide",
            "compatible_materials": ["steel", "cast_iron"],
        },
        {
            "name": "M8 Tap",
            "category": "tap",
            "diameter": 8.0,
            "length": 70.0,
            "flute_length": 20.0,
            "number_of_flutes": 4,
            "substrate": "hss",
            "coating_type": "TiN",
            "compatible_materials": ["steel", "aluminum", "brass"],
        },
    ]


@pytest.fixture(autouse=True)
def reset_test_state():
    """
    Reset state before each test.
    
    This fixture runs automatically before every test.
    Use it to clean up any global state.
    """
    # Setup (before test)
    yield
    # Teardown (after test)
    # Clean up any test artifacts here
