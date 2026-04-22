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
    parser = argparse.ArgumentParser(description="KnowledgeHarvester - Single File Mode")

    parser.add_argument("--base_url", required=True)
    parser.add_argument("--start_url", required=True)
    parser.add_argument("--link_filter", default="")
    parser.add_argument("--keywords", default="")
    parser.add_argument("--max_pages", type=int, default=60)
    parser.add_argument("--min_score", type=int, default=2)

    return parser.parse_args()


# -------------------------
# HELPERS
# -------------------------

def normalize_url(url):
    return url.split("#")[0].rstrip("/")


def is_valid(url, base_url, link_filter):
    p = urlparse(url)
    base = urlparse(base_url)

    return (
        p.netloc == base.netloc and
        (link_filter in p.path if link_filter else True)
    )


def hash_content(text):
    return hashlib.sha256(text.encode()).hexdigest()


# -------------------------
# CLEAN / EXTRACT
# -------------------------

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "nav", "footer", "header", "aside",
        "script", "style", "noscript",
        "svg", "button"
    ]):
        tag.decompose()

    for cls in [
        "sidebar", "menu", "navigation", "toc",
        "breadcrumbs", "pagination"
    ]:
        for el in soup.select(f".{cls}"):
            el.decompose()

    return soup


def extract_main(soup):
    return (
        soup.find("main") or
        soup.find("article") or
        soup.find("div", {"role": "main"}) or
        soup.body
    )


# -------------------------
# SCORING
# -------------------------

def score(text, keywords):
    t = text.lower()
    return sum(2 for k in keywords if k in t)


# -------------------------
# STRUCTURE CONTENT
# -------------------------

def structure_page(url, markdown):
    sections = []
    current = ""
    title = "Content"

    for line in markdown.split("\n"):
        if line.startswith("# ") or line.startswith("## "):
            if current.strip():
                sections.append((title, current.strip()))
                current = ""

            title = line.strip().replace("#", "").strip()
        else:
            current += line + "\n"

    if current.strip():
        sections.append((title, current.strip()))

    # monta página estruturada
    page = [f"# {url}"]

    for title, content in sections:
        if len(content) < 200:
            continue

        page.append(f"\n## {title}\n{content}")

    return "\n".join(page)


# -------------------------
# MAIN
# -------------------------

async def run(config):
    output_file = Path("output/knowledge_base.md")
    output_file.parent.mkdir(exist_ok=True)

    visited = set()
    queue = deque([normalize_url(config["start_url"])])
    seen_hashes = set()

    global_content = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        while queue and len(visited) < config["max_pages"]:
            url = normalize_url(queue.popleft())

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

            if len(markdown) < 300:
                continue

            relevance = score(markdown, config["keywords"])
            if relevance < config["min_score"]:
                continue

            structured = structure_page(url, markdown)
            global_content.append(structured)

            # coleta links
            links = await page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => e.href)"
            )

            for link in links:
                link = normalize_url(link)

                if "#" in link:
                    continue

                if is_valid(link, config["base_url"], config["link_filter"]):
                    queue.append(link)

        await browser.close()

    # salva tudo em 1 arquivo
    output_file.write_text("\n\n---\n\n".join(global_content), encoding="utf-8")

    print(f"\nDone. Pages processed: {len(visited)}")
    print(f"Output: {output_file}")


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