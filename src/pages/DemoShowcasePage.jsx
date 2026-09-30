import { Link } from "react-router-dom";

const shots = [
  ["00", "00_BOOKCRAFT_DEMO_INDEX.png", "/demo", "Карта итоговой демонстрации"],
  ["01", "01_BOOKCRAFT_HOME.png", "/", "Главная и индивидуальный дизайн"],
  ["02", "02_MAILING_GENERATION.png", "/mailing?demo=1", "Рассылка: вход → результат"],
  ["03", "03_PODCAST_TTS_PIPELINE.png", "/podcast?demo=1", "Подкаст: сценарий → голос → waveform"],
  ["04", "04_VIDEO_AVATAR_API.png", "/video-avatar?demo=1", "Видео-аватар: каталог голосов и аватаров"],
  ["05", "05_LONGREAD_EXTRA_TAB.png", "/longread?demo=1", "Дополнительная вкладка ДЗ PRO"],
  ["06", "06_IMAGE_GENERATION_BONUS.png", "/images?demo=1", "Бонус: генерация изображений"],
  ["07", "07_ANALYTICS_DEMO.png", "/analytics", "Аналитика / DEMO"],
  ["08", "08_CREATE_HUB.png", "/create", "Общий контентный хаб"],
];

export default function DemoShowcasePage() {
  const origin = typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:5180";

  return (
    <section className="demoShowcase">
      <div className="demoShowcase__hero">
        <div>
          <div className="eyebrow">✦ DZ PRO · FINAL DEMO</div>
          <h1>BOOK-CRAFT<br/><em>AI Content Maker</em></h1>
          <p>Итоговый маршрут для проверки ДЗ и подготовки скриншотов. Все screenshot-state страницы открываются уже заполненными.</p>
        </div>
        <div className="demoShowcase__score">
          <small>COVERAGE</small>
          <b>8 / 8</b>
          <span>screens ready</span>
        </div>
      </div>

      <div className="demoShotGrid">
        {shots.map(([n, filename, path, note]) => (
          <Link to={path} className="demoShotCard spectralSurface" key={filename}>
            <div className="demoShotCard__top">
              <span className="demoShotNumber">{n}</span>
              <small>SCREENSHOT</small>
            </div>
            <b>{filename}</b>
            <p>{note}</p>
            <code>{origin}{path}</code>
            <span className="demoShotCard__open">Открыть готовое состояние →</span>
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
