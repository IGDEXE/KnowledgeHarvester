import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from pathlib import Path
import argparse
import re
import hashlib
import time
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
    parser.add_argument("--max_pages", type=int, default=500)
    parser.add_argument("--delay", type=float, default=0.2)
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


def clean_html(soup):
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup


def extract_main(soup):
    return (
        soup.find("main") or
        soup.find("article") or
        soup.find("div", {"role": "main"}) or
        soup.body
    )


def hash_content(text):
    return hashlib.md5(text.encode()).hexdigest()


# -------------------------
# SCORING / CLASSIFICATION
# -------------------------

def score(text, keywords):
    t = text.lower()
    s = 0

    for k in keywords:
        if k in t:
            s += 2

    return s


def classify(text):
    # classificação leve genérica
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

def run(config):
    ROOT = Path("output")
    RAW = ROOT / "raw"
    STRUCT = ROOT / "structured"
    CHUNK = ROOT / "chunked"

    for p in [RAW, STRUCT, CHUNK]:
        p.mkdir(parents=True, exist_ok=True)

    visited = set()
    queue = deque([config["start_url"]])
    seen_hashes = set()

    while queue and len(visited) < config["max_pages"]:
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
        except:
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        soup = clean_html(soup)

        main = extract_main(soup)
        if not main:
            continue

        content = md(str(main))

        h = hash_content(content)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        relevance = score(content, config["keywords"])
        if relevance < config["min_score"]:
            continue

        name = sanitize(url)
        categories = classify(content)

        # RAW
        (RAW / f"{name}.md").write_text(content, encoding="utf-8")

        # STRUCTURED
        structured = f"""source: {url}
score: {relevance}
categories: {",".join(categories)}

{content}
"""
        (STRUCT / f"{name}.md").write_text(structured, encoding="utf-8")

        # CHUNKS
        chunks = chunk_markdown(content)
        for i, c in enumerate(chunks):
            (CHUNK / f"{name}_{i}.md").write_text(c, encoding="utf-8")

        # LINKS
        for a in soup.find_all("a", href=True):
            href = urljoin(config["base_url"], a["href"])
            if is_valid(href, config["base_url"], config["link_filter"]):
                queue.append(href)

        time.sleep(config["delay"])

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
        "delay": args.delay,
        "min_score": args.min_score
    }

    run(config)