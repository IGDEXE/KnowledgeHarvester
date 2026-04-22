import argparse
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from collections import deque
from pathlib import Path
import re
import hashlib
from markdownify import markdownify as md

# -------------------------
# CLI
# -------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="KnowledgeHarvester")

    parser.add_argument("--base_url", required=True)
    parser.add_argument("--start_url", required=True)
    parser.add_argument("--link_filter", default="")
    parser.add_argument("--keywords", default="")
    parser.add_argument("--max_pages", type=int, default=200)
    parser.add_argument("--min_score", type=int, default=2)

    return parser.parse_args()


# -------------------------
# HELPERS
# -------------------------

def is_valid(url, base_url, link_filter):
    p = urlparse(url)
    base = urlparse(base_url)

    return (
        p.netloc == base.netloc and
        (link_filter in p.path if link_filter else True)
    )


def sanitize(url):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", urlparse(url).path)


def hash_content(text):
    return hashlib.sha256(text.encode()).hexdigest()


# -------------------------
# SCORING / CLASSIFICATION
# -------------------------

def score(text, keywords):
    t = text.lower()
    return sum(2 for k in keywords if k in t)


def classify(text):
    t = text.lower()
    categories = []

    if "api" in t:
        categories.append("api")
    if "auth" in t or "authentication" in t:
        categories.append("auth")
    if "scan" in t:
        categories.append("scan")
    if "policy" in t:
        categories.append("policy")

    return categories or ["general"]


# -------------------------
# CHUNK
# -------------------------

def chunk_markdown(text, max_size=1800):
    sections = re.split(r"\n## ", text)
    chunks = []
    current = ""

    for sec in sections:
        if len(current) + len(sec) < max_size:
            current += "\n## " + sec
        else:
            chunks.append(current)
            current = sec

    if current:
        chunks.append(current)

    return chunks


# -------------------------
# MAIN
# -------------------------

async def run(config):
    ROOT = Path("output")
    RAW = ROOT / "raw"
    STRUCT = ROOT / "structured"
    CHUNK = ROOT / "chunked"

    for p in [RAW, STRUCT, CHUNK]:
        p.mkdir(parents=True, exist_ok=True)

    visited = set()
    queue = deque([config["start_url"]])
    seen_hashes = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        while queue and len(visited) < config["max_pages"]:
            url = queue.popleft()

            if url in visited:
                continue

            visited.add(url)
            print(f"Visiting: {url}")

            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state("networkidle")
            except:
                continue

            html = await page.content()

            h = hash_content(html)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            markdown = md(html)
            relevance = score(markdown, config["keywords"])

            if relevance < config["min_score"]:
                continue

            name = sanitize(url) or "root"
            categories = classify(markdown)

            # RAW
            (RAW / f"{name}.md").write_text(markdown, encoding="utf-8")

            # STRUCTURED
            structured = f"""source: {url}
score: {relevance}
categories: {",".join(categories)}

{markdown}
"""
            (STRUCT / f"{name}.md").write_text(structured, encoding="utf-8")

            # CHUNKS
            chunks = chunk_markdown(markdown)
            for i, c in enumerate(chunks):
                (CHUNK / f"{name}_{i}.md").write_text(c, encoding="utf-8")

            # LINKS (agora funciona com SPA)
            links = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => e.href)"
            )

            for link in links:
                if is_valid(link, config["base_url"], config["link_filter"]):
                    queue.append(link)

        await browser.close()

    print(f"Done. Pages processed: {len(visited)}")


# -------------------------
# ENTRYPOINT
# -------------------------

if __name__ == "__main__":
    args = parse_args()

    config = {
        "base_url": args.base_url,
        "start_url": args.start_url,
        "link_filter": args.link_filter,
        "keywords": args.keywords.split(",") if args.keywords else [],
        "max_pages": args.max_pages,
        "min_score": args.min_score
    }

    asyncio.run(run(config))