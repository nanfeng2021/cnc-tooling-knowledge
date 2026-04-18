"""
Import vendor cutter data into the knowledge base.

Usage:
    python scripts/import_vendor_data.py
    
This script:
1. Reads scraped vendor data from data/raw/
2. Transforms to domain model format
3. Imports into ChromaDB vector store
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from application.handlers.cutter_handler import CutterCommandHandler
from application.commands.ingest_cutter import IngestCutterCommand
from infrastructure.persistence.chroma_repo import ChromaCutterRepository
from infrastructure.persistence.embeddings import EmbeddingService
from domain.models.cutter import (
    Cutter,
    CutterType,
    MaterialSpec,
    GeometryParams,
)


def transform_vendor_cutter(vendor_data: Dict[str, Any]) -> Cutter:
    """
    Transform vendor scraper data to domain Cutter model.
    
    Args:
        vendor_data: Raw data from vendor scraper
        
    Returns:
        Cutter domain object
    """
    # Map vendor category to our standard categories
    category_map = {
        "solid_end_mill": "end_mill",
        "indexable_mill": "face_mill",
        "solid_carbide_drill": "drill",
        "indexable_drill": "drill",
        "threading": "threading_tool",
    }
    
    # Map workpiece materials to our standard format
    material_map = {
        "steel": "P",
        "stainless_steel": "M",
        "cast_iron": "K",
        "aluminum": "N",
        "non-ferrous": "N",
        "titanium": "S",
        "hardened_steel": "H",
        "inconel": "S",
    }
    
    compatible_materials = []
    for mat in vendor_data.get("workpiece_materials", []):
        if mat in material_map:
            compatible_materials.append(material_map[mat])
    
    # Create value objects
    cutter_type = CutterType(
        category=category_map.get(vendor_data.get("category", "end_mill"), "end_mill"),
        subcategory=vendor_data.get("cutter_type", "end_mill"),
    )
    
    geometry = GeometryParams(
        diameter=vendor_data.get("diameter"),
        length=vendor_data.get("length"),
        number_of_flutes=vendor_data.get("number_of_flutes"),
        corner_radius=None,
        helix_angle=None,
    )
    
    material = MaterialSpec(
        substrate=vendor_data.get("substrate"),
        coating=vendor_data.get("coating"),
        grade=None,
    )
    
    # Build usage guidelines from available data
    guidelines = []
    
    if vendor_data.get("application"):
        guidelines.append(f"Application: {vendor_data['application']}")
    
    if vendor_data.get("cutting_speed_min") and vendor_data.get("cutting_speed_max"):
        guidelines.append(
            f"Cutting speed: {vendor_data['cutting_speed_min']}-{vendor_data['cutting_speed_max']} m/min"
        )
    
    if vendor_data.get("feed_min") and vendor_data.get("feed_max"):
        guidelines.append(
            f"Feed: {vendor_data['feed_min']}-{vendor_data['feed_max']} mm/tooth"
        )
    
    return Cutter(
        name=f"{vendor_data['vendor']} - {vendor_data['name']}",
        cutter_type=cutter_type,
        geometry=geometry,
        material=material,
        compatible_materials=list(set(compatible_materials)),
        usage_guidelines=guidelines,
        vendor_info={
            "vendor": vendor_data.get("vendor"),
            "series": vendor_data.get("series"),
            "url": vendor_data.get("url"),
            "image_url": vendor_data.get("image_url"),
        },
    )


def import_vendor_data(
    data_dir: str = "./data/raw",
    vector_store_dir: str = "./vector_store",
) -> int:
    """
    Import all vendor data into knowledge base.
    
    Args:
        data_dir: Directory containing scraped vendor JSON files
        vector_store_dir: ChromaDB persistence directory
        
    Returns:
        Number of cutters imported
    """
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Data directory not found: {data_path}")
        print("Please run scripts/scrape_vendor_data.py first.")
        return 0
    
    # Initialize repository and handler
    embedding_service = EmbeddingService(model_name="all-MiniLM-L6-v2")
    repository = ChromaCutterRepository(
        persist_directory=vector_store_dir,
        collection_name="cutter_knowledge",
        embedding_service=embedding_service,
    )
    handler = CutterCommandHandler(repository=repository)
    
    # Find all vendor JSON files
    vendor_files = list(data_path.glob("*_cutters.json"))
    
    if not vendor_files:
        print(f"No vendor data files found in {data_path}")
        return 0
    
    total_imported = 0
    
    for vendor_file in vendor_files:
        print(f"\n📥 Importing {vendor_file.name}...")
        
        with open(vendor_file, 'r', encoding='utf-8') as f:
            vendor_data = json.load(f)
        
        imported = 0
        errors = 0
        
        for item in vendor_data:
            try:
                cutter = transform_vendor_cutter(item)
                command = IngestCutterCommand(cutter=cutter)
                handler.handle_ingest(command)
                imported += 1
            except Exception as e:
                print(f"  ⚠️  Error importing {item.get('name', 'Unknown')}: {e}")
                errors += 1
        
        print(f"  ✅ Imported: {imported}, ❌ Errors: {errors}")
        total_imported += imported
    
    print(f"\n{'='*50}")
    print(f"🎉 Total imported: {total_imported} cutters")
    print(f"📍 Vector store: {Path(vector_store_dir).absolute()}")
    print(f"{'='*50}")
    
    return total_imported


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import vendor cutter data into knowledge base")
    parser.add_argument("--data-dir", "-d", default="./data/raw", help="Directory with vendor JSON files")
    parser.add_argument("--vector-store", "-v", default="./vector_store", help="ChromaDB persistence directory")
    args = parser.parse_args()
    
    imported = import_vendor_data(args.data_dir, args.vector_store)
    
    if imported > 0:
        print(f"\n✅ Successfully imported {imported} cutters!")
        print("\nNext steps:")
        print("  1. Start the server: ./start_server.sh")
        print("  2. Open Web UI: open webui/index.html")
        print("  3. Test search: python scripts/test_query.py 'stainless steel end mill'")
    else:
        print("\n⚠️  No cutters imported. Check for errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
