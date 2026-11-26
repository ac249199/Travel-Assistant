import requests
import trafilatura


from urllib.parse import urlparse

def detect_content_type(url):

    path = urlparse(url).path.lower().strip("/")

    # Web stories
    if path.startswith("web-stories/"):
        return "web_story"

    # Category pages
    if path.startswith("category/"):
        return "category_page"

    # Specific booking pages
    booking_pages = [
        "temple-trail-varanasi-temples-tour"
    ]

    if path in booking_pages:
        return "booking_page"

    # General booking pages
    if (
        path.startswith("book-")
        or "booking" in path
        or path.startswith("book/")
    ):
        return "booking_page"

    # Specific tour pages
    tour_pages = [
        "kashi-temples-tour",
        "banarasi-silk-weavers-village-walk"
    ]

    if path in tour_pages:
        return "tour_page"

    # General tour and walk pages
    if path.startswith("tours/") or any(
        word in path for word in [
            "guided-tour",
            "guided-walk",
            "heritage-walk",
            "village-walk"
        ]
    ):
        return "tour_page"

    return "article"

def load_website(url):

    print(f"\nFetching webpage: {url}")

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "BanarasiBhaukalTravelGuru/0.1"
            },
            timeout=30
        )

        response.raise_for_status()

        downloaded = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=True,
            output_format="txt"
        )

        metadata = trafilatura.extract_metadata(response.text)

        if not downloaded:
            print("No main content extracted.")
            return None

        document = {
            "url": url,
            "title": metadata.title if metadata else None,
            "author": metadata.author if metadata else None,
            "date": metadata.date if metadata else None,
            "content": downloaded,
            "content_type": detect_content_type(url)
        }

        return document

    except requests.RequestException as e:
        print("Website loading error:", e)
        return None