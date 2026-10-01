import { Link } from "react-router-dom";
import SpectralAction from "../components/SpectralAction.jsx";
import ContentPlan from "../components/ContentPlan.jsx";
import VideoAvatarHud from "../components/VideoAvatarHud.jsx";
import PodcastHud from "../components/PodcastHud.jsx";
import AudienceGrowthHud from "../components/AudienceGrowthHud.jsx";
import HeroStage from "../components/HeroStage.jsx";

const services = [
  {
    to: "/books",
    title: "Книги",
    text: "Сюжет, главы, герои и литературный мир",
    tag: "BOOK",
    kind: "books",
    preview: "BOOK WORLD",
    icon: "▤",
    image: "/assets/bookcraft/candidates/2026-09-28/bookcraft-20260928-171126-1.png",
  },
  {
    to: "/scripts",
    title: "Сценарии клипов",
    text: "Сцены, кадры, реплики и визуальная драматургия",
    tag: "STORY",
    kind: "scripts",
    preview: "STORYBOARD",
    icon: "▣",
    image: "/assets/bookcraft/candidates/2026-09-28/bookcraft-20260928-171128-2.png",
  },
  {
    to: "/video-avatar",
    title: "Видео-аватар",
    text: "Реалистичные AI-аватары для роликов и презентаций",
    tag: "AVATAR",
    kind: "avatar",
    preview: "AVATAR PREVIEW",
    icon: "◎",
    image: "/assets/bookcraft/candidates/2026-09-28/bookcraft-20260928-171130-3.png",
  },
  {
    to: "/images",
    title: "Генерация изображений",
    text: "Персонажи, иллюстрации и стабильный визуальный стиль",
    tag: "IMAGE",
    kind: "images",
    preview: "IMAGE WORLD",
    icon: "▧",
    image: "/assets/bookcraft/candidates/2026-09-28/bookcraft-20260928-171133-4.png",
  },
];

const coreFlows = [
  {to:"/mailing", number:"01", title:"Рассылка", text:"Тема и аудитория → готовый текст письма", meta:"LLM FLOW · DEMO"},
  {to:"/podcast", number:"02", title:"Подкаст", text:"Сценарий → подготовка аудио и TTS-пайплайна", meta:"TTS FLOW · DEMO"},
  {to:"/video-avatar", number:"03", title:"Видео-аватар", text:"Голос + аватар + сценарий → видео-пайплайн", meta:"EXTERNAL API · DEMO"},
];

const demoMenuItems = [
  {
    to: "/mailing?demo=1",
    icon: "✎",
    type: "ТЕКСТ",
    title: "Рассылка",
    text: "Brief → генерация → SUBJECT / PREHEADER / BODY",
  },
  {
    to: "/podcast?demo=1",
    icon: "◉",
    type: "АУДИО",
    title: "Подкаст",
    text: "Сценарий → голос → waveform → воспроизведение",
  },
  {
    to: "/video-avatar?demo=1",
    icon: "▶",
    type: "ВИДЕО",
    title: "Видео-Аватар",
    text: "Аватар + голос + сценарий → video job",
  },
  {
    to: "/longread?demo=1",
    icon: "▤",
    type: "EXTRA",
    title: "Лонгрид",
    text: "Дополнительная вкладка задания → структура материала",
  },
];

export default function HomePage() {
  return (
    <>
      <section className="hero hero--cinematic">
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
            <SpectralAction to="/create" variant="primary">
              <span className="heroActionIcon">✦</span>
              Начать создавать →
            </SpectralAction>
            <div className="heroDemoMenu">
              <SpectralAction
                to="/demo"
                variant="ghost"
                className="heroDemoMenu__trigger"
                ariaLabel="Открыть меню демонстраций BOOK-CRAFT"
              >
                <span className="heroPlayIcon">▶</span>
                Смотреть демо
                <span className="heroDemoChevron" aria-hidden="true">⌄</span>
              </SpectralAction>

              <div className="heroDemoDropdown" role="menu" aria-label="Демонстрации по заданию">
                <div className="heroDemoDropdown__head">
                  <div>
                    <small>ДЗ PRO · AI CONTENT MAKER</small>
                    <b>Выберите формат</b>
                  </div>
                  <span>DEMO</span>
                </div>

                <div className="heroDemoDropdown__grid">
                  {demoMenuItems.map((item) => (
                    <Link
                      key={item.to}
                      to={item.to}
                      className="heroDemoItem"
                      role="menuitem"
                    >
                      <span className="heroDemoItem__icon" aria-hidden="true">{item.icon}</span>
                      <span className="heroDemoItem__copy">
                        <small>{item.type}</small>
                        <b>{item.title}</b>
                        <em>{item.text}</em>
                      </span>
                      <span className="heroDemoItem__arrow" aria-hidden="true">→</span>
                    </Link>
                  ))}
                </div>

                <Link to="/demo" className="heroDemoDropdown__all">
                  Все демонстрации и карта скриншотов →
                </Link>
              </div>
            </div>
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

      <section className="serviceGrid serviceGrid--cinematic" aria-label="Продукты BOOK-CRAFT">
        {services.map((item) => (
          <Link
            to={item.to}
            className={`serviceCard spectralSurface serviceCard--${item.kind}`}
            key={item.to}
          >
            <div className="serviceCard__topline">
              <span className="serviceIcon" aria-hidden="true">{item.icon}</span>
              <div className="serviceTag">{item.tag}</div>
              <span className="serviceArrow">→</span>
            </div>

            <h2>{item.title}</h2>
            <p>{item.text}</p>

            <div className="servicePreview servicePreview--photo">
              <img src={item.image} alt="" className="servicePreview__image" aria-hidden="true" />
              <span className="servicePreview__veil" aria-hidden="true" />
              <small>{item.preview}</small>
            </div>
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


    </>
  );
}
