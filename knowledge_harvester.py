import argparse
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from collections import deque
from pathlib import Path
import re
import hashlib
from markdownify import markdownify as md
from bs4 import BeautifulSoup

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
    return re.sub(r"[^a-zA-Z0-9_-]", "_", urlparse(url).path) or "root"


def hash_content(text):
    return hashlib.sha256(text.encode()).hexdigest()


# -------------------------
# CLEAN / EXTRACT
# -------------------------

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # remove lixo comum
    for tag in soup([
        "nav", "footer", "header", "aside",
        "script", "style", "noscript",
        "svg", "button"
    ]):
        tag.decompose()

    # remove classes comuns de docs
    for cls in [
        "sidebar", "menu", "navigation", "toc",
        "breadcrumbs", "pagination"
    ]:
        for el in soup.select(f".{cls}"):
            el.decompose()

    return soup


def extract_main(soup):
    main = (
        soup.find("main") or
        soup.find("article") or
        soup.find("div", {"role": "main"})
    )
    return main if main else soup.body


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
# CHUNK (SEMÂNTICO + TAMANHO)
# -------------------------

def chunk_semantic(text, max_size=1500):
    chunks = []
    current = ""
    title = "unknown"

    for line in text.split("\n"):
        if line.startswith("#"):
            if current and len(current) > 200:
                chunks.append((title, current.strip()))
                current = ""

            title = line.strip()
            current += line + "\n"

        else:
            current += line + "\n"

        # fallback por tamanho
        if len(current) > max_size:
            chunks.append((title, current.strip()))
            current = ""

    if current:
        chunks.append((title, current.strip()))

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

            soup = clean_html(html)
            main = extract_main(soup)

            if not main:
                continue

            markdown = md(str(main))
            relevance = score(markdown, config["keywords"])

            if relevance < config["min_score"]:
                continue

            name = sanitize(url)
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

            # CHUNKED (otimizado)
            chunks = chunk_semantic(markdown)

            for i, (title, content) in enumerate(chunks):
                enriched = f"""source: {url}
title: {title}
categories: {",".join(categories)}
chunk_id: {i}

{content}
"""
                (CHUNK / f"{name}_{i}.md").write_text(enriched, encoding="utf-8")

            # LINKS (SPA-safe)
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