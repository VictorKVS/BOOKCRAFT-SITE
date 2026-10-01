# BOOK-CRAFT Skeleton v1.2

В этой версии:

- отдельная кнопка **◈ Аналитика DEMO** в header;
- отдельная страница `/analytics`;
- реальные маршруты для всей верхней навигации;
- поиск `/search`;
- вход `/login`;
- рабочий mobile menu;
- рабочее demo-video modal;
- маршруты `/create`, `/mailing`, `/podcast`, `/video-avatar`, `/images`;
- общий компонент `SpectralAction`;
- три стадии кнопок: idle → hover → pressed;
- reduced-motion fallback;
- кликабельные сервисные карточки;
- аналитика встроена боковой панелью в рабочие модули.

Проверяем сначала только каркас и переходы. Реальные AI-функции подключаются следующим этапом.

## Visual assets

The current visual library is tracked in GitHub and kept separate from the React UI.

**Current hero candidate**

![BOOK-CRAFT hero candidate](public/assets/bookcraft/hero/candidates/hero-main-v1.png)

- [BOOK-CRAFT asset catalog](public/assets/bookcraft/README.md)
- [Asset inventory](public/assets/bookcraft/INBOX_INVENTORY.md)
- [Full move log](public/assets/ASSET_MOVE_LOG.md)
- [FATHER visual assets](public/assets/father/README.md)

The image library is still in review: candidates are not treated as final runtime assets until selected and wired into the UI.

## DZ PRO AI Content Maker — final demo

Итоговая демонстрация:

- `/demo` — карта всех screenshot-state страниц;
- `/mailing?demo=1` — готовая рассылка;
- `/podcast?demo=1` — готовый podcast/TTS UI;
- `/video-avatar?demo=1` — каталог voices + avatars и video-job contract;
- `/longread?demo=1` — дополнительная вкладка;
- `/images?demo=1` — bonus image workflow.

Полный список имён и URL: `docs/DZ_PRO_SCREENSHOTS.md`.


## DZ PRO evidence

- screenshots: `evidence/screenshots/`
- video: `evidence/video/`
- screenshot map: `docs/DZ_PRO_SCREENSHOTS.md`
- video script: `docs/DZ_PRO_VIDEO_SCRIPT.md`

- final report: `docs/DZ_PRO_REPORT.md`
