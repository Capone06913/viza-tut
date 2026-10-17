# Очередь правок пайплайна

## INC-20261017-1705-scout-wordstat-empty
status: open
run_date: 2026-10-17
role: excalibur-blog-scout
topic_id: n/a
article_dir: n/a
severity: low
category: api

### What went wrong
- Узкая фраза «чем отличается виза c от визы d» вернула пустой объект без списка фраз и без `totalCount`.
- Фразы «загранпаспорт перед подачей на визу» и «срок действия загранпаспорта для визы» вернули только `totalCount` (2 и 36), без списка.

### How the agent recovered this run
- `totalCount` записан как low-result signal, частотность фразы не выдумана.
- Пустой объект не остановлен как поломка Wordstat: запрос расширен до «шенгенская виза c» и «виза категории d», списки фраз получены.
- Новые темы блога из-за этого не добавлялись.

### Durable fix needed before next run
- В инструкции скаута пустой объект `{}` считать тем же low-result signal, что и ответ только с `totalCount`: расширить фразу до родительского кластера и не останавливать аудит.

### Suggested files to inspect/change
- `skills/scout-excalibur-blog/SKILL.md`

### Secrets
- none recorded

### Fixer resolution
- pending
