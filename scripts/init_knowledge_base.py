#!/usr/bin/env python3
"""
Initialize the knowledge base with sample cutter data.

This script demonstrates:
- Creating domain objects via factories
- Using command handlers for ingestion
- Batch data loading

Usage:
    python scripts/init_knowledge_base.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.domain.models.cutter import CutterType, MaterialSpec, GeometryParams
from src.application.commands.ingest_cutter import IngestCutterCommand
from src.application.handlers.cutter_handler import CutterCommandHandler
from src.infrastructure.persistence.chroma_repo import ChromaCutterRepository


SAMPLE_CUTTERS = [
    {
        "name": "10mm Carbide End Mill - Square",
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
            "vc_stainless": 100.0,
            "fz_steel": 0.05,
            "fz_aluminum": 0.08,
        },
        "usage_guidelines": [
            "General purpose milling for steel and stainless steel",
            "Use coolant for best tool life",
            "Avoid interrupted cuts when possible",
            "Recommended for roughing and finishing",
        ],
        "compatible_materials": ["steel", "stainless_steel", "cast_iron", "aluminum"],
    },
    {
        "name": "6mm HSS Drill Bit",
        "category": "drill",
        "subcategory": "twist",
        "coating": "TiN",
        "substrate": "hss",
        "diameter": 6.0,
        "length": 60.0,
        "flute_length": 30.0,
        "number_of_flutes": 2,
        "helix_angle": 30.0,
        "corner_radius": 0.0,
        "recommended_parameters": {
            "vc_steel": 30.0,
            "vc_aluminum": 80.0,
            "fz_steel": 0.15,
            "fz_aluminum": 0.20,
        },
        "usage_guidelines": [
            "Standard drilling for general applications",
            "Use cutting fluid for steel",
            "Peck drill for deep holes",
        ],
        "compatible_materials": ["steel", "aluminum", "brass", "plastic"],
    },
    {
        "name": "12mm Carbide Reamer",
        "category": "reamer",
        "subcategory": "straight",
        "coating": "Uncoated",
        "substrate": "carbide",
        "diameter": 12.0,
        "length": 100.0,
        "flute_length": 50.0,
        "number_of_flutes": 6,
        "helix_angle": 0.0,
        "corner_radius": 0.2,
        "recommended_parameters": {
            "vc_steel": 60.0,
            "vc_cast_iron": 80.0,
            "fz_steel": 0.10,
        },
        "usage_guidelines": [
            "Precision hole finishing",
            "Leave 0.2-0.3mm stock for reaming",
            "Use rigid setup to avoid chatter",
        ],
        "compatible_materials": ["steel", "cast_iron", "aluminum"],
    },
    {
        "name": "M8x1.25 HSS Tap",
        "category": "tap",
        "subcategory": "machine",
        "coating": "TiN",
        "substrate": "hss",
        "diameter": 8.0,
        "length": 70.0,
        "flute_length": 20.0,
        "number_of_flutes": 4,
        "helix_angle": 15.0,
        "corner_radius": 0.0,
        "recommended_parameters": {
            "vc_steel": 15.0,
            "vc_aluminum": 25.0,
            "fz_steel": 1.25,  # pitch
        },
        "usage_guidelines": [
            "For M8x1.25 metric threads",
            "Drill 6.8mm pilot hole first",
            "Use tapping fluid for best results",
            "Reverse every half turn to break chips",
        ],
        "compatible_materials": ["steel", "aluminum", "brass", "stainless_steel"],
    },
    {
        "name": "20mm High Feed End Mill",
        "category": "end_mill",
        "subcategory": "high_feed",
        "coating": "AlCrN",
        "substrate": "carbide",
        "diameter": 20.0,
        "length": 100.0,
        "flute_length": 40.0,
        "number_of_flutes": 3,
        "helix_angle": 10.0,
        "corner_radius": 2.0,
        "recommended_parameters": {
            "vc_steel": 180.0,
            "vc_hardened": 100.0,
            "fz_steel": 0.15,
            "fz_hardened": 0.08,
        },
        "usage_guidelines": [
            "Optimized for high feed rates",
            "Use trochoidal milling strategy",
            "Excellent for hardened steels up to 55 HRC",
            "Low radial engagement, high axial depth",
        ],
        "compatible_materials": ["steel", "hardened_steel", "titanium", "inconel"],
    },
]


def main():
    """Initialize knowledge base with sample data."""
    print("=" * 60)
    print("Tooling RAG Knowledge Base - Initialization")
    print("=" * 60)
    
    # Initialize repository
    print("\n[1/3] Initializing ChromaDB repository...")
    repo = ChromaCutterRepository(
        persist_directory=str(project_root / "vector_store"),
        collection_name="cutter_knowledge",
    )
    print(f"      ✓ Repository initialized at ./vector_store")
    
    # Create command handler
    print("\n[2/3] Creating command handler...")
    handler = CutterCommandHandler(repository=repo)
    print(f"      ✓ Handler ready")
    
    # Ingest sample cutters
    print("\n[3/3] Ingesting sample cutters...")
    ingested_count = 0
    
    for cutter_data in SAMPLE_CUTTERS:
        try:
            command = IngestCutterCommand(**cutter_data)
            result = handler.handle_ingest(command)
            print(f"      ✓ {result.name} (ID: {result.id[:8]}...)")
            ingested_count += 1
        except Exception as e:
            print(f"      ✗ Failed to ingest {cutter_data['name']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Initialization complete! {ingested_count}/{len(SAMPLE_CUTTERS)} cutters loaded.")
    print(f"Total in repository: {repo.count()}")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Start API server: python -m uvicorn src.interface.api.api:app --reload")
    print("  2. Open API docs: http://localhost:8000/docs")
    print("  3. Test search: curl -X POST http://localhost:8000/search -H 'Content-Type: application/json' -d '{\"query\": \"carbide end mill for steel\", \"top_k\": 3}'")


if __name__ == "__main__":
    main()
