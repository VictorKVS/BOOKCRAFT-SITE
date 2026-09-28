# BOOK-CRAFT — CARCASS LOCK V1.7

Цель этапа: зафиксировать рабочий черновой интерфейс до финального визуального слоя.

## Что фиксируется

- Header и основные маршруты.
- Desktop / tablet / phone recomposition.
- Hero structure.
- Правая HUD-колонка.
- Четыре продуктовые карточки.
- Create Hub.
- Mailing UI-flow.
- Podcast UI-flow.
- Video Avatar API UI-contract.
- Image Generation UI-contract.
- Books / Scripts skeleton flows.
- Search.
- Demo login state.
- Hover / pressed / focus / reduced motion.

## Что сознательно НЕ считается готовым

- LLM backend.
- TTS/audio generation.
- HeyGen/D-ID/другой внешний API.
- ComfyUI live-call в новом сайте.
- Авторизация.
- Реальная аналитика.
- Финальные изображения и hero-art.
- Финальная световая/анимационная полировка.

## Проверка

```powershell
npm run qa:carcass
npm run build
npm run dev -- --host 127.0.0.1 --port 5180
```

После успешной проверки следующий этап — визуальный слой, без перестройки каркаса.
