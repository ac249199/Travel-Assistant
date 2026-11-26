
import requests
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


BASE_URL = "https://www.varanasiguru.com/"
DOMAIN = urlparse(BASE_URL).netloc

HEADERS = {
    "User-Agent": "BanarasiBhaukalTravelGuru/0.1"
}

# Words that help identify relevant Varanasi content
RELEVANT_KEYWORDS = [
    "varanasi",
    "kashi",
    "banaras",
    "ghat",
    "temple",
    "food",
    "street",
    "culture",
    "history",
    "festival",
    "travel",
    "heritage",
    "guide",
    "places"
]


def get_robots_info():

    robots_url = urljoin(BASE_URL, "robots.txt")

    try:

        response = requests.get(
            robots_url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code != 200:
            print("robots.txt unavailable")
            return None, []

        lines = response.text.splitlines()

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(lines)

        sitemap_urls = []

        for line in lines:

            if line.lower().startswith("sitemap:"):

                sitemap_url = line.split(":", 1)[1].strip()

                sitemap_urls.append(sitemap_url)

        return parser, sitemap_urls

    except requests.RequestException as e:

        print("Robots error:", e)

        return None, []


def get_page(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as e:

        print("Failed:", url, e)

        return None


def is_internal_url(url):

    parsed = urlparse(url)

    return (
        parsed.scheme in ["http", "https"]
        and parsed.netloc.lower() == DOMAIN.lower()
    )


def parse_sitemap(sitemap_url, discovered_urls, robots,
                  visited_sitemaps=None, depth=0):

    if visited_sitemaps is None:
        visited_sitemaps = set()

    if sitemap_url in visited_sitemaps or depth > 3:
        return

    visited_sitemaps.add(sitemap_url)

    if robots and not robots.can_fetch("*", sitemap_url):
        print("Blocked by robots.txt:", sitemap_url)
        return

    xml_content = get_page(sitemap_url)

    if not xml_content:
        return

    try:

        root = ET.fromstring(xml_content)

        root_type = root.tag.split("}")[-1]

        # Handle sitemap index files
        if root_type == "sitemapindex":

            for sitemap in root:

                loc = sitemap.find(
                    "{*}loc"
                )

                if loc is not None and loc.text:

                    parse_sitemap(
                        loc.text.strip(),
                        discovered_urls,
                        robots,
                        visited_sitemaps,
                        depth + 1
                    )

        # Handle regular URL sitemaps
        elif root_type == "urlset":

            for entry in root:

                loc = entry.find("{*}loc")

                if loc is not None and loc.text:

                    page_url = loc.text.strip()

                    if is_internal_url(page_url):

                        if not robots or robots.can_fetch(
                            "*", page_url
                        ):
                            discovered_urls.add(page_url)

    except ET.ParseError:

        print("Invalid sitemap XML:", sitemap_url)


def discover_homepage_links(robots):

    html = get_page(BASE_URL)

    if not html:
        return set()

    soup = BeautifulSoup(html, "lxml")

    urls = set()

    for anchor in soup.find_all("a", href=True):

        url = urljoin(
            BASE_URL,
            anchor["href"]
        )

        url = url.split("#")[0]

        if is_internal_url(url):

            if not robots or robots.can_fetch("*", url):

                urls.add(url)

    return urls


def is_relevant_url(url):

    path = urlparse(url).path.lower()

    return any(
        keyword in path
        for keyword in RELEVANT_KEYWORDS
    )


def audit_website():

    print("\nStarting website audit...\n")

    robots, sitemap_urls = get_robots_info()

    print("Sitemaps discovered:", sitemap_urls)

    # Common sitemap locations
    sitemap_urls.extend([

        urljoin(BASE_URL, "sitemap.xml"),

        urljoin(BASE_URL, "sitemap_index.xml"),

        urljoin(BASE_URL, "wp-sitemap.xml")

    ])

    discovered_urls = set()

    # Discover URLs from available sitemaps
    for sitemap_url in set(sitemap_urls):

        parse_sitemap(
            sitemap_url,
            discovered_urls,
            robots
        )

    # Fallback to homepage links
    homepage_urls = discover_homepage_links(robots)

    discovered_urls.update(homepage_urls)

    relevant_urls = [
        url for url in discovered_urls
        if is_relevant_url(url)
    ]

    print("\nTotal internal URLs:", len(discovered_urls))

    print(
        "Potentially relevant Varanasi URLs:",
        len(relevant_urls)
    )

    print("\nRelevant URLs:\n")

    for url in sorted(relevant_urls):
        print(url)

    # Save discovered URLs into JSON
    from pathlib import Path

    DATA_DIR = Path("data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "website": BASE_URL,
        "total_urls": len(discovered_urls),
        "relevant_urls_count": len(relevant_urls),
        "relevant_urls": sorted(relevant_urls)
    }

    output_path = DATA_DIR / "varanasi_urls.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print(f"\nURLs saved successfully: {output_path}")

    print("\nWebsite audit completed.")

    return relevant_urls


if __name__ == "__main__":

    audit_website()

