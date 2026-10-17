#!/usr/bin/env python3
"""Fill quad-manifest.json: cover hook + inline visual_type per H2 (one quad canvas)."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Reuse type picker from visual manifest module inline
TYPE_PRIORITY = [
    "checklist_board",
    "comparison_table_ui",
    "progression_board",
    "gear_flatlay",
    "stance_diagram",
    "fall_technique",
    "trick_term_card",
    "city_season_card",
]
SHORT_HOOKS = {
    "B01": "Сначала бокс потом рейл",
    "B02": "Сначала 50-50 потом бокс",
    "B03": "Джиб круглый год",
}
COVER_PRINT = {
    "B01": "СНАЧАЛА БОКС, ПОТОМ РЕЙЛ",
    "B02": "СНАЧАЛА 50-50, ПОТОМ БОКС",
    "B03": "ДЖИБ КРУГЛЫЙ ГОД",
    "B04": "СНАЧАЛА ШЛЕМ, ПОТОМ ДОСКА",
    "B07": "МЯГКИЕ КОЛЕНИ",
    "B09": "В СНЕГ ЭТО БАЗА",
}
TOPIC_COVER_SCENES = {}
TOPIC_INLINE_JOBS = {}
TOPIC_INLINE_SCENES = {}
DEFAULT_SLOT_MAP = {
    "cover": "top_left",
    "inline_1": "top_right",
    "inline_2": "bottom_left",
    "inline_3": "bottom_right",
}


def project_root() -> Path:
    env_root = os.environ.get("EXCALIBUR_PROJECT_ROOT", "").strip()
    if env_root:
        return Path(env_root)
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_h2_titles(article_html: Path) -> list[str]:
    if not article_html.is_file():
        return []
    text = article_html.read_text(encoding="utf-8")
    titles: list[str] = []
    for match in re.finditer(r"<h2[^>]*>(.*?)</h2>", text, flags=re.I | re.S):
        title = re.sub(r"<[^>]+>", "", match.group(1))
        title = re.sub(r"\s+", " ", title).strip()
        if not title:
            continue
        if title.lower() in {"частые вопросы", "faq"}:
            break
        titles.append(title)
    return titles


def score_type(h2: str, type_def: dict) -> int:
    hay = h2.lower()
    score = 0
    for kw in type_def.get("keywords") or []:
        if kw.strip().lower() in hay:
            score += 2
    return score


def pick_visual_type(h2: str, types_catalog: dict, used: set[str]) -> str:
    types = types_catalog.get("types") or {}
    scored: list[tuple[int, str]] = []
    for type_id, type_def in types.items():
        scored.append((score_type(h2, type_def), type_id))
    scored.sort(key=lambda item: (-item[0], TYPE_PRIORITY.index(item[1]) if item[1] in TYPE_PRIORITY else 99))
    for score, type_id in scored:
        if score > 0 and type_id not in used:
            return type_id
    for type_id in TYPE_PRIORITY:
        if type_id not in used:
            return type_id
    return TYPE_PRIORITY[0]


def print_title_for_type(type_id: str, types_catalog: dict) -> str:
    type_def = (types_catalog.get("types") or {}).get(type_id) or {}
    return str(type_def.get("print_title") or "")


def scene_hint_for_type(type_id: str, h2: str, types_catalog: dict) -> str:
    job = ((types_catalog.get("types") or {}).get(type_id) or {}).get("job") or "packed scrap collage"
    return f"Improvise {job} explaining: {h2}. Unique objects for this topic only."


def alt_for_type(type_id: str, h2: str, types_catalog: dict) -> str:
    label = ((types_catalog.get("types") or {}).get(type_id) or {}).get("label_ru") or type_id
    return f"{label}: {h2}"


def build_manifest(article_dir: Path, root: Path, preserve: dict | None) -> dict[str, Any]:
    meta_path = article_dir / "article.meta.json"
    meta = load_json(meta_path) if meta_path.is_file() else {}
    types_catalog = load_json(root / "memory/cover/inline-visual-types.json")
    h2s = extract_h2_titles(article_dir / "article.html")
    topic_id = meta.get("topic_id") or article_dir.name.split("-")[0]
    article_topic = meta.get("h1") or article_dir.name

    old_cover = ((preserve or {}).get("slots") or {}).get("cover") or {}
    cover = {
        "quadrant": "top_left",
        "role": "cover_meme_hero",
        "alt": old_cover.get("alt") or f"Обложка: {article_topic}",
        "print_title": COVER_PRINT.get(str(topic_id), ""),
        "scene_hint": TOPIC_COVER_SCENES.get(str(topic_id))
        or (
            "STANDING with a unique topic prop for this article, not tricking. "
            f"Improvise a fresh scrap mix. Topic: {article_topic}."
        ),
        "meme_caption_ru": "",
    }

    used: set[str] = set()
    slots: dict[str, Any] = {"cover": cover}
    forced_jobs = TOPIC_INLINE_JOBS.get(str(topic_id))
    topic_inline_scenes = TOPIC_INLINE_SCENES.get(str(topic_id))
    for idx, slot_key in enumerate(("inline_1", "inline_2", "inline_3"), start=1):
        h2 = h2s[idx - 1] if idx - 1 < len(h2s) else f"Секция {idx}"
        if forced_jobs and idx - 1 < len(forced_jobs):
            visual_type = forced_jobs[idx - 1]
        else:
            visual_type = pick_visual_type(h2, types_catalog, used)
        used.add(visual_type)
        old = ((preserve or {}).get("slots") or {}).get(slot_key) or {}
        print_title = print_title_for_type(visual_type, types_catalog)
        if topic_inline_scenes and idx - 1 < len(topic_inline_scenes):
            scene_hint = topic_inline_scenes[idx - 1]
        else:
            scene_hint = scene_hint_for_type(visual_type, h2, types_catalog)
        slots[slot_key] = {
            "quadrant": DEFAULT_SLOT_MAP[slot_key],
            "h2_anchor": old.get("h2_anchor") or h2,
            "visual_type": visual_type,
            "print_title": print_title,
            "scene_hint": scene_hint,
            "alt": alt_for_type(visual_type, old.get("h2_anchor") or h2, types_catalog),
        }

    cover_hook = (preserve or {}).get("cover_hook") or SHORT_HOOKS.get(str(topic_id), "Сноуборд")

    return {
        "topic_id": topic_id,
        "canvas_file": "cover/canvas-quad.png",
        "layout": "2x2",
        "pipeline": "quad_canvas_1x_mcp",
        "style_preset": "lenin_cream_zine",
        "style_file": "memory/cover/cover-design-code.json",
        "blog_hero": "memory/cover/blog-hero.json",
        "inline_types_catalog": "memory/cover/inline-visual-types.json",
        "cover_hook": cover_hook,
        "cover_print": COVER_PRINT.get(str(topic_id), ""),
        "mcp_note": "ONE gpt-image-2 call with input_urls=[reference_url_hosted], then split",
        "slots": slots,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--article-dir", required=True)
    ap.add_argument("--out", default="cover/quad-manifest.json")
    ap.add_argument("--merge", action="store_true")
    args = ap.parse_args()

    root = project_root()
    article_dir = Path(args.article_dir)
    if not article_dir.is_absolute():
        article_dir = root / article_dir

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = article_dir / out_path

    preserve = load_json(out_path) if args.merge and out_path.is_file() else None
    manifest = build_manifest(article_dir, root, preserve)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save_json(out_path, manifest)
    print(f"OK manifest={out_path}")
    for key in ("inline_1", "inline_2", "inline_3"):
        s = manifest["slots"][key]
        print(f"  {key}: {s['visual_type']} -> {s['h2_anchor']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
