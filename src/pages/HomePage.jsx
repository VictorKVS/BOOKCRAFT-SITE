import { Link } from "react-router-dom";
import { useState } from "react";
import SpectralAction from "../components/SpectralAction.jsx";
import ContentPlan from "../components/ContentPlan.jsx";
import VideoAvatarHud from "../components/VideoAvatarHud.jsx";
import PodcastHud from "../components/PodcastHud.jsx";
import AudienceGrowthHud from "../components/AudienceGrowthHud.jsx";
import HeroStage from "../components/HeroStage.jsx";

const services = [
  {to:"/books", title:"Книги", text:"Сюжет, главы, герои и литературный мир", tag:"BOOK", kind:"books", preview:"BOOK WORLD"},
  {to:"/scripts", title:"Сценарии клипов", text:"Сцены, кадры, реплики и визуальная драматургия", tag:"STORY", kind:"scripts", preview:"STORYBOARD"},
  {to:"/video-avatar", title:"Видео-аватар", text:"Реалистичные AI-аватары для роликов и презентаций", tag:"AVATAR", kind:"avatar", preview:"AVATAR PREVIEW"},
  {to:"/images", title:"Генерация изображений", text:"Персонажи, иллюстрации и стабильный визуальный стиль", tag:"IMAGE", kind:"images", preview:"IMAGE WORLD"},
];

export default function HomePage() {
  const [videoOpen, setVideoOpen] = useState(false);

  return (
    <>
      <section className="hero">
        <div className="heroCopy">
          <div className="eyebrow">✦ NARRATIVE KNOWLEDGE STUDIO</div>

          <h1>
            <span>Создание</span>
            <em>сценариев</em>
            <span>и AI-контента</span>
          </h1>

          <p className="lead">
            Превращайте идеи в истории. Создавайте рассылки, подкасты,
            видео-аватары и изображения в одном AI-продукте.
          </p>

          <div className="heroActions">
            <SpectralAction to="/create" variant="primary">✦ Начать создавать →</SpectralAction>
            <SpectralAction variant="ghost" onClick={() => setVideoOpen(true)}>▶ Смотреть видео</SpectralAction>
          </div>

          <div className="metrics">
            <div>
              <span className="metricIcon">▤</span>
              <b>10K+</b>
              <span>DEMO · созданных историй</span>
            </div>
            <div>
              <span className="metricIcon">▦</span>
              <b>4 в 1</b>
              <span>все инструменты в одном месте</span>
            </div>
            <div>
              <span className="metricIcon">∞</span>
              <b>без границ</b>
              <span>масштабирование после MVP</span>
            </div>
          </div>
        </div>

        <div className="heroVisual">
          <HeroStage />

          <div className="heroHudColumn">
            <AudienceGrowthHud />

            <div className="contentPlanSlot">
              <ContentPlan />
            </div>

            <PodcastHud />
            <VideoAvatarHud />
          </div>
        </div>
      </section>

      <section className="serviceGrid" aria-label="Продукты BOOK-CRAFT">
        {services.map((item) => (
          <Link to={item.to} className={`serviceCard spectralSurface serviceCard--${item.kind}`} key={item.to}>
            <div className="serviceTag">{item.tag}</div>
            <h2>{item.title}</h2>
            <p>{item.text}</p>
            <div className="servicePreview">
              <span className="servicePreview__art" aria-hidden="true" />
              <small>{item.preview}</small>
            </div>
            <span className="serviceArrow">→</span>
          </Link>
        ))}
      </section>

      {videoOpen && (
        <div className="modalBackdrop" role="presentation" onMouseDown={() => setVideoOpen(false)}>
          <div className="videoModal" role="dialog" aria-modal="true" aria-label="Видео о BOOK-CRAFT" onMouseDown={(e) => e.stopPropagation()}>
            <button className="modalClose" type="button" onClick={() => setVideoOpen(false)} aria-label="Закрыть">×</button>
            <small>DEMO VIDEO SLOT</small>
            <h2>BOOK-CRAFT за 60–75 секунд</h2>
            <div className="videoPlaceholder">▶</div>
            <p>Сюда подключим финальное демонстрационное видео после сборки рабочих модулей.</p>
          </div>
        </div>
      )}
    </>
  );
}
