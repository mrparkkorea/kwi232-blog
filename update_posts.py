import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
import re

RSS_URL = "https://rss.blog.naver.com/kwi232.xml"
OUTPUT_FILE = "posts.json"
MAX_POSTS = 30


def clean_text(value: str) -> str:
    """HTML 태그와 불필요한 공백을 제거합니다."""
    if not value:
        return ""

    value = unescape(value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def format_date(value: str) -> str:
    """RSS 날짜를 YYYY.MM.DD 형식으로 변환합니다."""
    if not value:
        return ""

    try:
        parsed = parsedate_to_datetime(value)
        return parsed.strftime("%Y.%m.%d")
    except (TypeError, ValueError):
        return value


def fetch_rss() -> bytes:
    """네이버 블로그 RSS를 불러옵니다."""
    request = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 RSS Reader for "
                "mrparkkorea.github.io/kwi232-blog"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def parse_rss(xml_data: bytes) -> list[dict]:
    """RSS XML에서 글 정보를 추출합니다."""
    root = ET.fromstring(xml_data)
    posts = []

    for item in root.findall(".//item")[:MAX_POSTS]:
        title = clean_text(item.findtext("title"))
        link = clean_text(item.findtext("link"))
        description = clean_text(item.findtext("description"))
        pub_date = clean_text(item.findtext("pubDate"))
        category = clean_text(item.findtext("category"))

        if not title or not link:
            continue

        posts.append(
            {
                "title": title,
                "link": link,
                "description": description[:180],
                "date": format_date(pub_date),
                "category": category or "네이버 블로그",
            }
        )

    return posts


def save_posts(posts: list[dict]) -> None:
    """글 목록을 JSON 파일로 저장합니다."""
    payload = {
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "posts": posts,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def main() -> None:
    xml_data = fetch_rss()
    posts = parse_rss(xml_data)

    if not posts:
        raise RuntimeError("RSS에서 글을 찾지 못했습니다.")

    save_posts(posts)
    print(f"{len(posts)}개의 글을 {OUTPUT_FILE}에 저장했습니다.")


if __name__ == "__main__":
    main()
