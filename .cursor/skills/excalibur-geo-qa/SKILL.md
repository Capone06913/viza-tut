---
name: excalibur-geo-qa
description: Excalibur BLOG GEO QA — fact-check, link verify, linter, slop, cannibalization, article-qa PASS.
---

# Excalibur BLOG — GEO QA

## Когда

После `article.html` + `article.meta.json` от Writer. **До** cover/schema (их делает директор параллельно после PASS).

## Скрипты (обязательно)

```bash
python scripts/excalibur_blog_research_notes_gate.py \
  --article-dir memory/blog/articles/<dir> \
  -o research-notes-gate.json

python scripts/excalibur_blog_fact_checker.py \
  memory/blog/articles/<dir>/article.html \
  -o memory/blog/articles/<dir>/fact-check-report.json

python scripts/excalibur_blog_link_verify.py \
  memory/blog/articles/<dir>/article.html \
  -o memory/blog/articles/<dir>/link-verify.json \
  --site-base https://YOUR_SITE

python scripts/excalibur_blog_html_linter.py \
  memory/blog/articles/<dir>/article.html \
  -o memory/blog/articles/<dir>/html-linter-report.json
```

HTML linter **блокирует оглавление в теле** (`<ol>/<ul>` с 3+ ссылками `href="#..."`) и любые теги вне whitelist, включая `<pre>`/`<code>`. При fail — Writer удаляет TOC (после инсайт-блока сразу `<p>`) или заменяет код/шаблон на whitelist-safe HTML (`<blockquote><p>...<br>...</p></blockquote>`, таблицу или список). Инсайт-блок не должен начинаться с шаблонного ярлыка `TL;DR` или фразы `Быстрый инсайт`. `research_notes_gate.py -o research-notes-gate.json` пишет файл внутри `--article-dir`; не передавай туда repo-relative путь с повтором `memory/blog/articles/...`.

```bash
python scripts/excalibur_blog_slop_detector.py \
  memory/blog/articles/<dir>/article.html \
  -o memory/blog/articles/<dir>/slop-detector-report.json

python scripts/excalibur_blog_cannibalization_guard.py \
  --blog-dir memory/blog/articles \
  -o memory/blog/articles/<dir>/cannibalization-report.json

python scripts/excalibur_blog_utility_gate.py \
  --article-dir memory/blog/articles/<dir> \
  --output utility-gate-report.json

python scripts/excalibur_blog_human_voice_gate.py \
  --article-dir memory/blog/articles/<dir> \
  -o human-voice-report.json
```

**Paths / authors registry:** при `EXCALIBUR_PROJECT_ROOT=<site repo>` human-voice резолвит статьи от site root. `shared/authors-registry.json` сначала ищется в project `shared/`, затем fallback на plugin `shared/`. Не копируй реестр вручную каждый run: либо держи brand-автора в project `shared/authors-registry.json`, либо полагайся на plugin fallback. Для `--article-dir` предпочитай абсолютный путь под site `memory/blog/articles/...`, когда скрипты живут в plugin.

**Utility gate stdout:** вердикт это JSON `overall`. Скрипт печатает ASCII `>=` и переводит stdout в utf-8, чтобы Windows cp1251 не ронял exit 1 после PASS. Если print всё же упал, читай `utility-gate-report.json`, не process exit.

**Research notes gate:** `ai` внутри `pain` / `reader_pain` не делает тему technical. Mode B how_to/checklist не требует 3 GitHub URL, пока карточка темы сама не про AI/MCP/агентов.

**Pass:** score ≥ 80, CORE-EEAT ≥ 16/20, link-verify pass, **research notes gate PASS**, **utility gate PASS**, **human voice gate PASS**, **beginner-fit PASS**. В `article-qa.md` отдельно зафиксируй: какая боль новичка решена, где показано решение, какой первый результат получит читатель, какие сложные термины объяснены «на пальцах».

**Beginner-fit blocker:** статья звучит как методичка, не объясняет термин визы простыми словами или не говорит, что проверить и какую страницу услуги открыть.

Schema и cover — **не** твоя зона (отдельные субагенты после PASS).
