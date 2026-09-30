import { Link } from "react-router-dom";

const shots = [
  ["00", "00_BOOKCRAFT_HOME.png", "/", "Главная BOOK-CRAFT — главный визуальный кадр проекта"],
  ["01", "01_MAILING_GENERATION.png", "/mailing?demo=1", "Нажмите «Сгенерировать заново» — появится LLM-процесс и новый текст"],
  ["02", "02_PODCAST_TTS_PIPELINE.png", "/podcast?demo=1", "Пересоберите аудио, затем запустите DEMO-воспроизведение"],
  ["03", "03_VIDEO_AVATAR_API.png", "/video-avatar?demo=1", "Обновите каталог, выберите avatar/voice и подготовьте video job"],
  ["04", "04_LONGREAD_EXTRA_TAB.png", "/longread?demo=1", "Пересоберите структуру — появится процесс редактора и новый outline"],
  ["05", "05_IMAGE_GENERATION_BONUS.png", "/images?demo=1", "Запустите DEMO-рендер и выберите один из четырёх вариантов"],
  ["06", "06_ANALYTICS_DEMO.png", "/analytics", "Аналитика / DEMO"],
  ["07", "07_CREATE_HUB.png", "/create", "Общий контентный хаб"],
  ["08", "08_BOOKCRAFT_DEMO_INDEX.png", "/demo", "Карта итоговой демонстрации"],
];

export default function DemoShowcasePage() {
  const origin = typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:5180";

  return (
    <section className="demoShowcase">
      <div className="demoShowcase__hero">
        <div>
          <div className="eyebrow">✦ DZ PRO · INTERACTIVE FINAL DEMO</div>
          <h1>BOOK-CRAFT<br/><em>AI Content Maker</em></h1>
          <p>Это не статичные screenshot-state страницы: в основных модулях кнопки запускают видимый DEMO-процесс — генерацию, рендер, загрузку каталога и воспроизведение.</p>
        </div>

        <div className="demoShowcase__score">
          <small>INTERACTIVE</small>
          <b>5 / 5</b>
          <span>core demo flows</span>
        </div>
      </div>

      <div className="demoInteractionHint">
        <span>HOW TO DEMO</span>
        <b>Откройте модуль → нажмите главную кнопку → дождитесь анимации → покажите результат</b>
        <small>Рассылка · Подкаст · Видео-Аватар · Лонгрид · Изображения</small>
      </div>

      <div className="demoShotGrid">
        {shots.map(([n, filename, path, note]) => (
          <Link to={path} className="demoShotCard spectralSurface" key={filename}>
            <div className="demoShotCard__top">
              <span className="demoShotNumber">{n}</span>
              <small>{path.includes("demo=1") ? "INTERACTIVE" : "SCREENSHOT"}</small>
            </div>
            <b>{filename}</b>
            <p>{note}</p>
            <code>{origin}{path}</code>
            <span className="demoShotCard__open">Открыть →</span>
          </Link>
        ))}
      </div>

      <div className="demoShowcase__footer">
        <span>BASE URL</span>
        <code>{origin}/</code>
        <b>BOOK-CRAFT · Narrative AI Studio</b>
      </div>
    </section>
  );
}
