# Excalibur BLOG — типичные сбои пайплайна

## Cloud / Task

- Cloud не принимает `excalibur-blog-*` как Task types → fallback `Task(generalPurpose)` + `.cursor/agents/<role>.md` + skill path.
- Parent-agent сам пишет статью вместо `excalibur-blog-writer` → **блокер**, перезапуск writer Task.
- Объединение cover+schema в один Task → запрещено; только параллельные отдельные Task.

## Handoff / fragments

- Параллельные `cover` и `schema` пишут в `.cursor/excalibur-blog-fragments/cover.md` и `schema.md`, директор переносит в handoff.
- Не коммитить `.cursor/excalibur-blog-handoff.md` и fragments.

## Research / дата

- Перед пайплайном: `python3 scripts/excalibur_blog_today.py` и `python3 scripts/excalibur_blog_research_start.py --topic-id …`.
- Если `EXCALIBUR_RUN_DATE` нет в выводе today.py — старая ветка/код, **блокер**.

## Publish

- `EXCALIBUR_BLOG_ALLOW_PUBLISH=yes` только в Cloud Secrets, не в git.
- Publish без обновления `shared/published-articles.md` → следующий прогон может дублировать slug.
- Для publish-preflight используй `python3 scripts/excalibur_blog_wp_publish.py --env-check`, не ad-hoc import без `scripts/` в `sys.path`.
- Beget/artuyut: если SSH_USER/PASS пустые, а FTP_* есть в `teya-memory/teya.env.local`, publish-скрипт сам мапит FTP→SSH и ставит `SSH_ROOT=public_html`. Не ставь `SSH_ROOT=.` вручную: bootstrap уйдёт вне web root и даст HTTP 404.
- `memory/site.env.local` не коммитить. Workspace-копию не создавать, пока файл не в `.gitignore`.

## Writer / outcome markers

- Writer обязан прогнать `excalibur_blog_utility_gate.py` по своему `article.html` до handoff. `outcome_markers < 3` = не сдавать. Стебли: результат / сможете / выберите / поймёте / подготовитесь / запишетесь / проедете / начнёте. Синонимы не считаются.
- Agent writer больше не трактует utility_gate как «чужой QA».

## Writer / Fact Check Box

- Fact Check Box **не копирует** пример из `shared/excalibur-article-writing-contract.md`. Автор — только из `shared/authors-registry.json` по `author_id` в `article.meta.json`.
- Запрещены legacy-имена вне реестра (в т.ч. «Елена Ковалева»). Human voice gate блокирует несовпадение автора и generic-шаблон «все статистические показатели…».

## QA

- Шаг cover||schema **только после** GEO QA PASS.
- MCP URLs в production article.html → fix перед publish.
- `article.html` должен проходить whitelist HTML-линтера: `<pre>`/`<code>` запрещены, пока не добавлены в whitelist; код/шаблоны оформляй через blockquote/table/list.
- Cannibalization guard CLI: `--blog-dir memory/blog/articles -o <article_dir>/cannibalization-report.json`, не `--article-dir`.
- При `EXCALIBUR_PROJECT_ROOT=<site>` human-voice ищет `shared/authors-registry.json` в project `shared/` и при отсутствии падает обратно на plugin `shared/`. Автор этого проекта: `viza-tut` в `shared/authors-registry.json`.

## Cover

- Meme/sticker style можно сохранять, но видимый текст не должен быть токсичным или оскорбительным: `лох`, `лохов`, `для лохов` и похожие ярлыки запрещены.
- `KIE_API_KEY` скрипт подхватывает из `teya-memory/teya.env.local`, если process env пуст. Ключ не печатать.
- Inject пишет `figure.article-figure`. Не оставляй `inline-quad` и не добавляй второй figure к тому же `cover/inline-0N.png`.

## Research / notes gate

- `ai` внутри `pain` / `reader_pain` не technical topic. Gate матчит маркеры как целые слова; Mode B how_to/checklist/comparison пропускает GitHub quota, пока карточка темы сама не про AI/MCP/агентов.
- Wordstat: пустой `{}` или голый `totalCount` = `WORDSTAT API FORMAT WARNING`. Сразу parent-кластер + LSI. Не маппить `totalCount` в показы и не ретраить узкую фразу.

## QA / Windows console

- `utility_gate` печатает ASCII `>=` и переводит stdout в utf-8. Вердикт = JSON `overall`. Не читай cp1251 print crash как BLOCK.

## Scout

- Wordstat проверяй cluster-first: широкий parent-запрос → узкий how-to. `totalCount`-only ответ на узкий запрос = low-result signal, не fatal.

## Indexer

- В Cloud shell используй `python3` для interlinker/llms generator; `python` может отсутствовать.
