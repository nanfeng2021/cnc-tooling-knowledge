#!/usr/bin/env python3
"""
Test query script for the Tooling RAG Knowledge Base.

This script demonstrates:
- Semantic search functionality
- Query handler usage
- Result interpretation

Usage:
    python scripts/test_query.py "your search query"
    
Examples:
    python scripts/test_query.py "carbide end mill for steel"
    python scripts/test_query.py "drill bit for aluminum"
    python scripts/test_query.py "tapping M8 thread"
"""

import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.queries.search_cutters import SearchCuttersQuery
from src.application.handlers.cutter_handler import CutterQueryHandler
from src.infrastructure.persistence.chroma_repo import ChromaCutterRepository


def print_cutter_result(cutter_dto, score: float, rank: int) -> None:
    """Pretty print a search result."""
    print(f"\n{'='*60}")
    print(f"#{rank} - Relevance Score: {score:.3f}")
    print(f"{'='*60}")
    print(f"Name: {cutter_dto.name}")
    print(f"ID: {cutter_dto.id}")
    print(f"\nType: {cutter_dto.cutter_type.category}", end="")
    if cutter_dto.cutter_type.subcategory:
        print(f"/{cutter_dto.cutter_type.subcategory}", end="")
    if cutter_dto.cutter_type.coating:
        print(f" ({cutter_dto.cutter_type.coating})", end="")
    print()
    
    print(f"Material: {cutter_dto.material.substrate}", end="")
    if cutter_dto.material.coating_type:
        print(f" + {cutter_dto.material.coating_type}", end="")
    if cutter_dto.material.hardness_hrc:
        print(f" ({cutter_dto.material.hardness_hrc} HRC)", end="")
    print()
    
    print(f"Geometry: Φ{cutter_dto.geometry.diameter}mm × {cutter_dto.geometry.length}mm, "
          f"{cutter_dto.geometry.number_of_flutes} flutes")
    
    if cutter_dto.compatible_materials:
        print(f"Compatible Materials: {', '.join(cutter_dto.compatible_materials)}")
    
    if cutter_dto.usage_guidelines:
        print(f"\nUsage Guidelines:")
        for i, guideline in enumerate(cutter_dto.usage_guidelines[:3], 1):
            print(f"  {i}. {guideline}")
    
    if cutter_dto.recommended_parameters:
        print(f"\nRecommended Parameters:")
        for key, value in list(cutter_dto.recommended_parameters.items())[:4]:
            print(f"  • {key}: {value}")


def search(query_text: str, top_k: int = 5) -> None:
    """Execute a search query and display results."""
    print(f"\n🔍 Searching for: '{query_text}'")
    print(f"   Top {top_k} results\n")
    
    # Initialize repository and handler
    repo = ChromaCutterRepository(
        persist_directory=str(project_root / "vector_store"),
        collection_name="cutter_knowledge",
    )
    
    handler = CutterQueryHandler(repository=repo)
    
    # Execute query
    query = SearchCuttersQuery(
        query_text=query_text,
        top_k=top_k,
    )
    
    results = handler.handle_search(query)
    
    if not results:
        print("\n❌ No results found.")
        print("\nTips:")
        print("  • Make sure you've initialized the knowledge base first")
        print("  • Run: python scripts/init_knowledge_base.py")
        print("  • Try different keywords or more general terms")
        return
    
    print(f"✅ Found {len(results)} result(s)\n")
    
    # Display results
    for i, result in enumerate(results, 1):
        print_cutter_result(result.cutter, result.relevance_score, i)
    
    print(f"\n{'='*60}")
    print(f"Search complete!")
    print(f"{'='*60}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_query.py <search_query> [top_k]")
        print("\nExamples:")
        print('  python scripts/test_query.py "carbide end mill for steel"')
        print('  python scripts/test_query.py "drill for aluminum" 3')
        print("\nDefault: top_k=5")
        sys.exit(1)
    
    query_text = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    search(query_text, top_k)


if __name__ == "__main__":
    main()
