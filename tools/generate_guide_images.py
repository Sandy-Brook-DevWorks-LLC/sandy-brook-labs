#!/usr/bin/env python3
"""
Guide Image Generator
=====================
Generates editorial guide images with Gemini's image model and saves them into
static guide image folders. The RAG guide ships with SVG placeholders so the site
works without API access; run this script when you want bitmap replacements.

Usage:
    python3 tools/generate_guide_images.py --guide rag
    python3 tools/generate_guide_images.py --guide rag --only chapter01
    python3 tools/generate_guide_images.py --guide rag --list

Requires:
    GEMINI_API_KEY
    pip install google-genai pillow
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE_DIR = ROOT / "guides" / "rag"
OUTPUT_DIR = GUIDE_DIR / "images"
MODEL = "gemini-2.5-flash-image"

BASE_NOTES = """Create an editorial image for a technical guide about retrieval-augmented generation (RAG). The image should feel like a pleasant blog illustration that breaks up a wall of text, in the spirit of early-2000s technical blogs using memorable, sometimes loosely related images. Use Sandy Brook teal (#1a5f6b), slate, off-white, and one restrained secondary accent. No text, no readable letters, no logos, no trademarks, no code glyphs that form real words. Landscape 16:9. Fill the canvas."""

IMAGES = [
    {"name": "rag-guide-og", "description": "Guide hero", "prompt": BASE_NOTES + " Show a document library, small evidence cards, and a glowing path into a calm answer panel with citation markers as abstract shapes."},
    {"name": "chapter01", "description": "Solution topology", "prompt": BASE_NOTES + " Show a tidy tabletop model of five small buildings connected by footpaths, representing API, worker, core, orchestration, and tests."},
    {"name": "chapter02", "description": "Aspire control plane", "prompt": BASE_NOTES + " Show a small control room with levers connected to containers, database blocks, and a dashboard-like window."},
    {"name": "chapter03", "description": "Contracts", "prompt": BASE_NOTES + " Show clean interface plugs and sockets connecting interchangeable model blocks, storage blocks, and vector blocks."},
    {"name": "chapter04", "description": "Metadata", "prompt": BASE_NOTES + " Show a neat card catalog drawer with status tabs, timestamps, and progress bars represented only as abstract lines."},
    {"name": "chapter05", "description": "Upload", "prompt": BASE_NOTES + " Show a book or PDF sliding into a quiet inbox tray while a small queued marker waits beside it."},
    {"name": "chapter06", "description": "Object storage", "prompt": BASE_NOTES + " Show original documents stored safely in labeled-but-unreadable archive boxes, with derived vector shards nearby."},
    {"name": "chapter07", "description": "Worker", "prompt": BASE_NOTES + " Show a conveyor belt moving papers through extraction, chunking, embedding, and indexing machines as abstract stations."},
    {"name": "chapter08", "description": "Chunking", "prompt": BASE_NOTES + " Show a long scroll being cut into overlapping translucent panels with soft teal alignment marks."},
    {"name": "chapter09", "description": "Literary artifacts", "prompt": BASE_NOTES + " Show a book club table with character cards, theme tokens, and evidence notes as abstract shapes."},
    {"name": "chapter10", "description": "Providers", "prompt": BASE_NOTES + " Show several interchangeable model cartridges fitting into the same calm machine slot."},
    {"name": "chapter11", "description": "Qdrant", "prompt": BASE_NOTES + " Show a constellation of points in a vector space with small citation payload cards attached."},
    {"name": "chapter12", "description": "Ask flow", "prompt": BASE_NOTES + " Show a question traveling through branching retrieval paths and returning with selected evidence cards."},
    {"name": "chapter13", "description": "Citations", "prompt": BASE_NOTES + " Show an answer page with numbered evidence tabs as abstract circles, no readable text."},
    {"name": "chapter14", "description": "Testing", "prompt": BASE_NOTES + " Show a lab bench with small green check lights testing chunk, provider, and answer modules."},
    {"name": "chapter15", "description": "Local development", "prompt": BASE_NOTES + " Show a developer desk with a small local dashboard, containers, and terminal-like panels with no readable text."},
]


def create_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    try:
        from google import genai
    except ImportError:
        print("ERROR: google-genai is not installed. Run: pip install google-genai pillow", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)


def generate_one(client, entry: dict[str, str], retries: int = 3) -> bool:
    try:
        from google.genai import types
        from PIL import Image
    except ImportError:
        print("ERROR: google-genai and pillow are required. Run: pip install google-genai pillow", file=sys.stderr)
        sys.exit(1)

    output_path = OUTPUT_DIR / f"{entry['name']}.png"
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[types.Part.from_text(text=entry["prompt"])],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="16:9"),
                ),
            )
            for candidate in response.candidates or []:
                if not candidate.content:
                    continue
                for part in candidate.content.parts:
                    if part.inline_data is None:
                        continue
                    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                    image = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
                    image.save(output_path, "PNG", optimize=True)
                    print(f"saved {output_path}")
                    return True
            print(f"no image returned for {entry['name']} (attempt {attempt}/{retries})")
        except Exception as exc:
            print(f"error generating {entry['name']} (attempt {attempt}/{retries}): {exc}")
        if attempt < retries:
            time.sleep(6 * attempt)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate guide images with Gemini")
    parser.add_argument("--guide", choices=["rag"], default="rag")
    parser.add_argument("--only", help="image name to generate, for example chapter01")
    parser.add_argument("--list", action="store_true", help="list configured images")
    args = parser.parse_args()

    selected = IMAGES
    if args.only:
        selected = [entry for entry in IMAGES if entry["name"] == args.only]
        if not selected:
            print(f"Unknown image name: {args.only}", file=sys.stderr)
            sys.exit(2)

    if args.list:
        for entry in selected:
            print(f"{entry['name']}: {entry['description']}")
        return

    client = create_client()
    successes = 0
    for entry in selected:
        print(f"generating {entry['name']} — {entry['description']}")
        successes += 1 if generate_one(client, entry) else 0
        time.sleep(2)
    print(f"done: {successes}/{len(selected)} images generated")


if __name__ == "__main__":
    main()
