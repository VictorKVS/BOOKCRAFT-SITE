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

const coreFlows = [
  {to:"/mailing", number:"01", title:"Рассылка", text:"Тема и аудитория → готовый текст письма", meta:"LLM FLOW · DEMO"},
  {to:"/podcast", number:"02", title:"Подкаст", text:"Сценарий → подготовка аудио и TTS-пайплайна", meta:"TTS FLOW · DEMO"},
  {to:"/video-avatar", number:"03", title:"Видео-аватар", text:"Голос + аватар + сценарий → видео-пайплайн", meta:"EXTERNAL API · DEMO"},
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
            Превращайте одну идею в связанный набор контента: рассылку,
            подкаст, видео-аватар, изображения, сценарии и длинные истории.
          </p>

          <div className="heroActions">
            <SpectralAction to="/create" variant="primary">✦ Начать создавать →</SpectralAction>
            <SpectralAction variant="ghost" onClick={() => setVideoOpen(true)}>▶ Смотреть демо</SpectralAction>
          </div>

          <div className="heroProof">
            <span>01 · ИДЕЯ</span>
            <i>→</i>
            <span>02 · ПРОИЗВОДСТВО</span>
            <i>→</i>
            <span>03 · ПУБЛИКАЦИЯ</span>
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
              <span>контентные форматы в одном месте</span>
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
            <div className="contentPlanSlot"><ContentPlan /></div>
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

      <section className="productionSection">
        <div className="productionSection__head">
          <div>
            <small>ДЗ 18 · CORE WORKFLOWS</small>
            <h2>Три рабочих потока в одном продукте</h2>
          </div>
          <p>Главная страница теперь ведёт прямо в обязательные сценарии задания. Реальные API подключаются после визуальной доводки интерфейса.</p>
        </div>

        <div className="productionFlowGrid">
          {coreFlows.map((flow) => (
            <Link to={flow.to} className="productionFlowCard spectralSurface" key={flow.to}>
              <div className="productionFlowCard__top">
                <span>{flow.number}</span>
                <small>{flow.meta}</small>
              </div>
              <h3>{flow.title}</h3>
              <p>{flow.text}</p>
              <b>Открыть рабочее место →</b>
            </Link>
          ))}
        </div>
      </section>

      {videoOpen && (
        <div className="modalBackdrop" role="presentation" onMouseDown={() => setVideoOpen(false)}>
          <div className="videoModal" role="dialog" aria-modal="true" aria-label="Видео о BOOK-CRAFT" onMouseDown={(e) => e.stopPropagation()}>
            <button className="modalClose" type="button" onClick={() => setVideoOpen(false)} aria-label="Закрыть">×</button>
            <small>DEMO VIDEO SLOT</small>
            <h2>BOOK-CRAFT за 60–75 секунд</h2>
            <div className="videoPlaceholder">▶</div>
            <p>Финальный ролик подключим после завершения рабочих модулей и визуального прохода.</p>
          </div>
        </div>
      )}
    </>
  );
}
