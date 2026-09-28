# BOOK-CRAFT — ASSET REGISTRY V1

## Статус
Каркас зафиксирован. Следующий этап — визуальные ассеты без изменения сетки и маршрутов.

## P0 — обязательные ассеты

| Key | Файл | Desktop slot | Требование |
|---|---|---:|---|
| hero.main | `hero/hero-main.webp` | 760×610 | персонаж отдельно, без UI |
| hero.background | `backgrounds/studio-main.webp` | 1200×610 | интерьер/свет, без текста |
| card.books | `cards/books.webp` | 360×86 | книги / литературный мир |
| card.scripts | `cards/scripts.webp` | 360×86 | storyboard / сцены |
| card.avatar | `cards/avatar.webp` | 360×86 | avatar preview art |
| card.images | `cards/images.webp` | 360×86 | image generation art |

## P1 — дополнительные слои
- `props/script.webp`
- `props/storyboard.webp`
- `props/desk.webp`

## Генерация исходников
Для качества исходники лучше генерировать минимум в 2× от runtime slot:
- hero: ~1520×1220;
- background: ~2400×1220;
- card art: ~720×172;
- затем crop / resize / WebP.

## Запреты
В графику не запекаем:
- меню;
- кнопки;
- названия модулей;
- метрики;
- контент-план;
- podcast waveform;
- analytics;
- маршруты;
- финальные тексты интерфейса.

Они уже существуют как живой UI.

## Порядок
1. Hero character.
2. Background.
3. Проверка hero composition.
4. Four card arts.
5. Optional props.
6. Light/color pass.
7. Motion pass.
8. Responsive visual QA.
