"""
CNC Tooling Vendor Data Scraper.

Scrapes cutting tool data from major vendors:
- Sandvik Coromant
- Kennametal
- Mitsubishi Hitachi
- OSG
- YAMAWA

Note: This is a demo scraper. For production use, you should:
1. Check each vendor's robots.txt and terms of service
2. Use official APIs if available
3. Implement rate limiting and respectful scraping
4. Consider purchasing official product data feeds
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import json
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CutterData:
    """Standardized cutter data structure."""
    name: str
    vendor: str
    series: str
    cutter_type: str
    category: str
    diameter: Optional[float] = None
    length: Optional[float] = None
    number_of_flutes: Optional[int] = None
    substrate: Optional[str] = None
    coating: Optional[str] = None
    workpiece_materials: List[str] = None
    application: Optional[str] = None
    cutting_speed_min: Optional[float] = None
    cutting_speed_max: Optional[float] = None
    feed_min: Optional[float] = None
    feed_max: Optional[float] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    
    def __post_init__(self):
        if self.workpiece_materials is None:
            self.workpiece_materials = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VendorScraper:
    """Base class for vendor scrapers."""
    
    vendor_name = "Unknown"
    base_url = ""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        })
    
    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch URL and return parsed HTML."""
        try:
            logger.info(f"Fetching {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(self.delay)  # Be respectful
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def scrape(self) -> List[CutterData]:
        """Main scraping method. Override in subclasses."""
        raise NotImplementedError


class SandvikScraper(VendorScraper):
    """Sandvik Coromant scraper."""
    
    vendor_name = "Sandvik Coromant"
    base_url = "https://www.sandvik.coromant.com"
    
    def scrape(self, categories: List[str] = None) -> List[CutterData]:
        """
        Scrape Sandvik tool catalog.
        
        Note: This is a simplified example. Real implementation would need
        to handle JavaScript-rendered content and complex navigation.
        """
        cutters = []
        
        # Example: Solid end mills
        # In production, you would iterate through actual category pages
        sample_categories = [
            "/zh-cn/products/solid-end-mills",
            "/zh-cn/products/solid-drills",
        ]
        
        for category in (categories or sample_categories):
            soup = self.fetch(f"{self.base_url}{category}")
            if soup:
                cutters.extend(self._parse_category(soup, category))
        
        # Add sample data for demonstration
        cutters.extend(self._get_sample_sandvik_cutters())
        
        return cutters
    
    def _parse_category(self, soup: BeautifulSoup, category: str) -> List[CutterData]:
        """Parse category page."""
        cutters = []
        # Implementation depends on actual site structure
        return cutters
    
    def _get_sample_sandvik_cutters(self) -> List[CutterData]:
        """Sample Sandvik cutters for demonstration."""
        return [
            CutterData(
                name="CoroMill® Plura",
                vendor="Sandvik Coromant",
                series="CoroMill Plura",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=10.0,
                length=75.0,
                number_of_flutes=4,
                substrate="Carbide",
                coating="AlTiN",
                workpiece_materials=["steel", "stainless_steel", "cast_iron"],
                application="General purpose milling",
                cutting_speed_min=150.0,
                cutting_speed_max=300.0,
                url="https://www.sandvik.coromant.com/products/coromill-plura",
            ),
            CutterData(
                name="CoroDrill® 880",
                vendor="Sandvik Coromant",
                series="CoroDrill 880",
                cutter_type="drill",
                category="indexable_drill",
                diameter=20.0,
                length=150.0,
                substrate="Steel body",
                coating="TiAlN inserts",
                workpiece_materials=["steel", "stainless_steel"],
                application="High productivity drilling",
                cutting_speed_min=100.0,
                cutting_speed_max=250.0,
                url="https://www.sandvik.coromant.com/products/corodrill-880",
            ),
            CutterData(
                name="CoroThread® 266",
                vendor="Sandvik Coromant",
                series="CoroThread 266",
                cutter_type="threading_tool",
                category="threading",
                substrate="Carbide",
                workpiece_materials=["steel", "stainless_steel", "aluminum"],
                application="Thread turning",
                url="https://www.sandvik.coromant.com/products/corocord-266",
            ),
        ]


class KennametalScraper(VendorScraper):
    """Kennametal scraper."""
    
    vendor_name = "Kennametal"
    base_url = "https://www.kennametal.com"
    
    def scrape(self) -> List[CutterData]:
        """Scrape Kennametal catalog."""
        cutters = self._get_sample_kennametal_cutters()
        return cutters
    
    def _get_sample_kennametal_cutters(self) -> List[CutterData]:
        """Sample Kennametal cutters."""
        return [
            CutterData(
                name="Harvi™ I UE",
                vendor="Kennametal",
                series="Harvi I UE",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=12.0,
                length=83.0,
                number_of_flutes=4,
                substrate="Ultra-grain carbide",
                coating="TiAlN",
                workpiece_materials=["steel", "stainless_steel"],
                application="Universal milling",
                cutting_speed_min=120.0,
                cutting_speed_max=280.0,
                url="https://www.kennametal.com/harvi-i-ue",
            ),
            CutterData(
                name="KenTIP™ FS",
                vendor="Kennametal",
                series="KenTIP FS",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=8.0,
                number_of_flutes=3,
                substrate="Carbide tip",
                coating="TiN",
                workpiece_materials=["aluminum", "non-ferrous"],
                application="High speed aluminum milling",
                cutting_speed_min=500.0,
                cutting_speed_max=1500.0,
                url="https://www.kennametal.com/kentip-fs",
            ),
            CutterData(
                name="KSEM™ HP",
                vendor="Kennametal",
                series="KSEM HP",
                cutter_type="drill",
                category="solid_carbide_drill",
                diameter=10.0,
                length=100.0,
                substrate="Carbide",
                coating="TiAlN",
                workpiece_materials=["steel", "cast_iron"],
                application="High performance drilling",
                cutting_speed_min=80.0,
                cutting_speed_max=200.0,
                url="https://www.kennametal.com/ksem-hp",
            ),
        ]


class MitsubishiScraper(VendorScraper):
    """Mitsubishi Hitachi scraper."""
    
    vendor_name = "Mitsubishi Hitachi"
    base_url = "https://www.mitsubishicarbide.net"
    
    def scrape(self) -> List[CutterData]:
        """Scrape Mitsubishi catalog."""
        cutters = self._get_sample_mitsubishi_cutters()
        return cutters
    
    def _get_sample_mitsubishi_cutters(self) -> List[CutterData]:
        """Sample Mitsubishi cutters."""
        return [
            CutterData(
                name="STAR-COAT AQUA",
                vendor="Mitsubishi Hitachi",
                series="STAR-COAT AQUA",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=6.0,
                number_of_flutes=4,
                substrate="Micro-grain carbide",
                coating="AQUA coating",
                workpiece_materials=["steel", "stainless_steel", "hardened_steel"],
                application="Wet machining",
                cutting_speed_min=100.0,
                cutting_speed_max=250.0,
                url="https://www.mitsubishicarbide.net/star-coat-aqua",
            ),
            CutterData(
                name="IMPACT MIRACLE",
                vendor="Mitsubishi Hitachi",
                series="IMPACT MIRACLE",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=10.0,
                number_of_flutes=3,
                substrate="Ultra-fine carbide",
                coating="Miracle coating",
                workpiece_materials=["aluminum", "copper", "graphite"],
                application="Non-ferrous high speed milling",
                cutting_speed_min=300.0,
                cutting_speed_max=1000.0,
                url="https://www.mitsubishicarbide.net/impact-miracle",
            ),
            CutterData(
                name="MVX",
                vendor="Mitsubishi Hitachi",
                series="MVX",
                cutter_type="mill",
                category="indexable_mill",
                substrate="Steel body",
                workpiece_materials=["steel", "cast_iron"],
                application="Face milling",
                url="https://www.mitsubishicarbide.net/mvx",
            ),
        ]


class OSGScraper(VendorScraper):
    """OSG scraper - taps and drills specialist."""
    
    vendor_name = "OSG"
    base_url = "https://www.osgtool.com"
    
    def scrape(self) -> List[CutterData]:
        """Scrape OSG catalog."""
        cutters = self._get_sample_osg_cutters()
        return cutters
    
    def _get_sample_osg_cutters(self) -> List[CutterData]:
        """Sample OSG taps and drills."""
        return [
            CutterData(
                name="EXOTAP",
                vendor="OSG",
                series="EXOTAP",
                cutter_type="tap",
                category="threading",
                substrate="HSS-E",
                coating="TiCN",
                workpiece_materials=["steel", "stainless_steel"],
                application="General purpose tapping",
                thread_size="M6-M12",
                url="https://www.osgtool.com/exotap",
            ),
            CutterData(
                name="ADO-MICRO",
                vendor="OSG",
                series="ADO-MICRO",
                cutter_type="drill",
                category="solid_carbide_drill",
                diameter=5.0,
                length=60.0,
                substrate="Carbide",
                coating="Oil Hole",
                workpiece_materials=["steel", "cast_iron"],
                application="Deep hole drilling",
                cutting_speed_min=60.0,
                cutting_speed_max=150.0,
                url="https://www.osgtool.com/ado-micro",
            ),
        ]


class YAMAWAScraper(VendorScraper):
    """YAMAWA scraper - threading tools specialist."""
    
    vendor_name = "YAMAWA"
    base_url = "https://www.yamawa.eu"
    
    def scrape(self) -> List[CutterData]:
        """Scrape YAMAWA catalog."""
        cutters = self._get_sample_yamawa_cutters()
        return cutters
    
    def _get_sample_yamawa_cutters(self) -> List[CutterData]:
        """Sample YAMAWA taps."""
        return [
            CutterData(
                name="DCT",
                vendor="YAMAWA",
                series="DCT",
                cutter_type="tap",
                category="threading",
                substrate="HSS",
                coating="Uncoated",
                workpiece_materials=["steel"],
                application="Cutting tap for steel",
                thread_standard="ISO metric",
                url="https://www.yamawa.eu/dct",
            ),
            CutterData(
                name="N-RZ",
                vendor="YAMAWA",
                series="N-RZ",
                cutter_type="tap",
                category="threading",
                substrate="HSS-E",
                coating="TiN",
                workpiece_materials=["stainless_steel"],
                application="Roll tap for stainless",
                thread_standard="ISO metric",
                url="https://www.yamawa.eu/n-rz",
            ),
        ]


class ZCCScraper(VendorScraper):
    """ZCC (株洲钻石) scraper - Chinese manufacturer."""
    
    vendor_name = "ZCC 株洲钻石"
    base_url = "https://www.zcccuttingtools.com"
    
    def scrape(self) -> List[CutterData]:
        """Scrape ZCC catalog."""
        cutters = self._get_sample_zcc_cutters()
        return cutters
    
    def _get_sample_zcc_cutters(self) -> List[CutterData]:
        """Sample ZCC cutters."""
        return [
            CutterData(
                name="BlackJack",
                vendor="ZCC 株洲钻石",
                series="BlackJack",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=10.0,
                number_of_flutes=4,
                substrate="Ultra-fine carbide",
                coating="AlCrN",
                workpiece_materials=["steel", "hardened_steel"],
                application="Hard material milling",
                cutting_speed_min=80.0,
                cutting_speed_max=200.0,
                url="https://www.zcccuttingtools.com/blackjack",
            ),
            CutterData(
                name="ALU-POWER",
                vendor="ZCC 株洲钻石",
                series="ALU-POWER",
                cutter_type="end_mill",
                category="solid_end_mill",
                diameter=8.0,
                number_of_flutes=3,
                substrate="Carbide",
                coating="Uncoated",
                workpiece_materials=["aluminum", "non-ferrous"],
                application="High speed aluminum milling",
                cutting_speed_min=400.0,
                cutting_speed_max=1200.0,
                url="https://www.zcccuttingtools.com/alupower",
            ),
        ]


def scrape_all_vendors(output_dir: str = "./data/raw") -> List[CutterData]:
    """
    Scrape all vendors and save to files.
    
    Args:
        output_dir: Directory to save scraped data
        
    Returns:
        List of all scraped cutter data
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    scrapers = [
        SandvikScraper(),
        KennametalScraper(),
        MitsubishiScraper(),
        OSGScraper(),
        YAMAWAScraper(),
        ZCCScraper(),
    ]
    
    all_cutters = []
    
    for scraper in scrapers:
        logger.info(f"Scraping {scraper.vendor_name}...")
        try:
            cutters = scraper.scrape()
            all_cutters.extend(cutters)
            
            # Save individual vendor file
            vendor_file = output_path / f"{scraper.vendor_name.replace(' ', '_').lower()}_cutters.json"
            with open(vendor_file, 'w', encoding='utf-8') as f:
                json.dump([c.to_dict() for c in cutters], f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(cutters)} cutters to {vendor_file}")
            
        except Exception as e:
            logger.error(f"Failed to scrape {scraper.vendor_name}: {e}")
    
    # Save combined file
    combined_file = output_path / "all_cutters.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump([c.to_dict() for c in all_cutters], f, indent=2, ensure_ascii=False)
    
    logger.info(f"Total: {len(all_cutters)} cutters saved to {combined_file}")
    
    return all_cutters


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape CNC tooling vendor data")
    parser.add_argument("--output", "-o", default="./data/raw", help="Output directory")
    parser.add_argument("--vendor", "-v", choices=["sandvik", "kennametal", "mitsubishi", "osg", "yamawa", "zcc", "all"], 
                       default="all", help="Vendor to scrape")
    args = parser.parse_args()
    
    if args.vendor == "all":
        scrape_all_vendors(args.output)
    else:
        scraper_map = {
            "sandvik": SandvikScraper,
            "kennametal": KennametalScraper,
            "mitsubishi": MitsubishiScraper,
            "osg": OSGScraper,
            "yamawa": YAMAWAScraper,
            "zcc": ZCCScraper,
        }
        scraper = scraper_map[args.vendor]()
        cutters = scraper.scrape()
        
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"{args.vendor}_cutters.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([c.to_dict() for c in cutters], f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(cutters)} cutters to {output_file}")


if __name__ == "__main__":
    main()
