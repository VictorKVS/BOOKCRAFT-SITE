import { useMemo, useState } from "react";

const catalog = [
  ["mailing", "Рассылка", "Персонализированные письма, цепочки и предложения", "✉"],
  ["podcast", "Подкаст", "Сценарии, озвучивание и эпизоды", "♫"],
  ["avatar", "Видеоаватар", "Презентации, сценарии и видео", "◉"],
  ["longread", "Лонгрид", "Статьи, исследования и публикации", "▤"],
  ["images", "Изображения", "Иллюстрации, обложки и визуальные концепции", "✦"],
  ["books", "Книги", "Сюжеты, главы и персонажи", "▣"],
  ["scripts", "Сценарии", "Раскадровки, клипы и интерактивные истории", "▷"],
];
const audienceMap = {
  business: { name: "Бизнес и маркетинг", need: "Сокращение времени производства контента", channels: ["Email", "Telegram", "VK", "Сайт"], pitch: "Сократите путь от идеи до готовой кампании" },
  creators: { name: "Авторы и креаторы", need: "Создание историй, видео и визуальных миров", channels: ["Telegram", "VK", "Видео", "Email"], pitch: "Превратите одну идею в целую творческую вселенную" },
  education: { name: "Образование", need: "Разработка учебных материалов и интерактивных занятий", channels: ["Email", "Сайт", "Сообщества"], pitch: "Создавайте учебный контент и практические сценарии быстрее" },
  agencies: { name: "Агентства и студии", need: "Масштабирование клиентского контент-производства", channels: ["Email", "Сайт", "CRM"], pitch: "Объедините производство контента в одном процессе" },
};
const capabilities = [
  "Книги, рассказы, сценарии и интерактивные истории",
  "Email-рассылки, коммерческие предложения и контент-планы",
  "Подкасты, тексты для озвучивания и аудиопроизводство",
  "Видеоаватары, презентации и сценарии видеороликов",
  "Изображения, иллюстрации, обложки и визуальные концепции",
  "Лонгриды, статьи, рекламные и образовательные материалы",
  "AI-ассистенты, рабочие процессы и контроль качества",
  "Сегментация аудитории, аналитика и подготовка публикаций",
];
const sources = [
  { title: "Google Trends", url: "https://trends.google.com/trends/", description: "Поисковый интерес, сравнение запросов и регионов" },
  { title: "Pinterest Trends", url: "https://trends.pinterest.com/", description: "Визуальные направления и сезонные интересы" },
  { title: "TikTok Creative Center", url: "https://ads.tiktok.com/business/creativecenter/", description: "Популярные форматы и темы коротких видео" },
  { title: "Exploding Topics", url: "https://explodingtopics.com/", description: "Поиск растущих тематик и ранних сигналов" },
];
const demoVisuals = [
  { title: "Книжная студия", src: "/assets/bookcraft/hero/foreground/books/books-01.png" },
  { title: "Алина — AI-редактор", src: "/assets/bookcraft/hero/characters/alina/alina-01.png" },
  { title: "Кинематографическая студия", src: "/assets/bookcraft/hero/backgrounds/studio-01.png" },
];
function buildDraft({ topic, audience, mode, tone, duration }) {
  const a = audienceMap[audience];
  const kind = catalog.find((x) => x[0] === mode)?.[1] || "Контент";
  const subject = duration === "trial" ? `BOOKCRAFT: ${a.pitch} — 30 дней демодоступа` : `${topic}: ${kind.toLowerCase()} для вашей аудитории`;
  const text = `Здравствуйте!\n\n${a.pitch}.\n\nПредлагаем познакомиться с BOOKCRAFT — единой AI-студией для создания сценариев и цифрового контента. ${duration === "trial" ? "Приглашаем запросить 30-дневный демонстрационный доступ (условия и доступность подтверждаются отдельно)." : `Тема: ${topic}. Формат: ${kind}.` }\n\nЧто можно попробовать:\n${capabilities.map((x) => `• ${x}`).join("\n")}\n\nДля кого: ${a.name}.\nКаналы: ${a.channels.join(", ")}.\nСтиль: ${tone}.\n\nОтветьте на это письмо, чтобы уточнить условия и получить программу демонстрации.\n\nКоманда BOOKCRAFT`;
  return { subject, preheader: `AI-студия для ${a.name.toLowerCase()}: от идеи до готового контента`, text };
}
function splitEmails(s) { return [...new Set(s.split(/[\s,;]+/).map(x => x.trim()).filter(Boolean))]; }
export default function DemoIntelligencePage() {
  const [mode, setMode] = useState("mailing");
  const [audience, setAudience] = useState("business");
  const [topic, setTopic] = useState("30 дней доступа к BOOKCRAFT");
  const [tone, setTone] = useState("Деловой и вдохновляющий");
  const [duration, setDuration] = useState("trial");
  const [draft, setDraft] = useState(null);
  const [recipients, setRecipients] = useState("");
  const [activeTab, setActiveTab] = useState("audience");
  const [notice, setNotice] = useState("");
  const a = audienceMap[audience];
  const kind = useMemo(() => catalog.find(x => x[0] === mode), [mode]);
  const addresses = splitEmails(recipients);
  const invalid = addresses.filter(x => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x));
  const valid = addresses.length > 0 && invalid.length === 0;
  const generate = () => { setDraft(buildDraft({ topic: topic.trim() || "BOOKCRAFT", audience, mode, tone, duration })); setNotice("Алина подготовила демонстрационный шаблон. Реальная модель не вызывалась."); };
  const copy = async () => { if (!draft) return; try { await navigator.clipboard.writeText(`Тема: ${draft.subject}\nПрехедер: ${draft.preheader}\n\n${draft.text}`); setNotice("Предложение скопировано."); } catch { setNotice("Копирование недоступно: выделите текст письма вручную."); } };
  const prepare = () => { if (!draft || !valid) return; const link = `mailto:${addresses.join(",")}?subject=${encodeURIComponent(draft.subject)}&body=${encodeURIComponent(draft.text)}`; if (link.length > 1800) { setNotice("Письмо слишком длинное для mailto. Скопируйте текст и отправьте через почтовый сервис."); return; } window.location.href = link; setNotice("Открывается почтовое приложение. Никаких писем сайт не отправлял."); };
  return <main className="bcDemo20">
    <div className="bcDemo20__top"><div><div className="bcDemo20__eyebrow">BOOKCRAFT / AI CREATIVE STUDIO / DEMO 2.0</div><h1>Алина создаёт. Аналитика подсказывает.</h1><p>От идеи до предложения, визуальных материалов и подготовки рассылки — в едином рабочем пространстве.</p></div><span className="bcDemo20__status">● ДЕМОНСТРАЦИОННЫЙ РЕЖИМ</span></div>
    <section className="bcDemo20__alinaHero" aria-label="Алина — AI-ассистент BOOKCRAFT"><img src="/assets/bookcraft/hero/characters/alina/alina-01.png" alt="Алина — AI-ассистент"/><div><strong>АЛИНА · AI CREATIVE ASSISTANT</strong><p>Я помогу подготовить предложение, подобрать формат контента и оценить аудиторию. Выберите сценарий и нажмите «Сгенерировать».</p><small>ДЕМОРЕЖИМ · FATHER API НЕ ПОДКЛЮЧЁН</small></div></section>
    <div className="bcDemo20__modes" aria-label="Вид контента">{catalog.map(([id,label,desc,icon])=><button type="button" key={id} className={mode===id?"is-active":""} onClick={()=>{setMode(id);setDraft(null);setNotice("");}} title={desc}><span>{icon}</span> {label}</button>)}</div>
    <div className="bcDemo20__layout"><section className="bcDemo20__main">
      <div className="bcDemo20__pipeline"><span>01 · ВХОДНЫЕ ДАННЫЕ</span><b>→</b><span>02 · АЛИНА / {kind[1].toUpperCase()}</span><b>→</b><span>03 · ПРЕДЛОЖЕНИЕ</span><b>→</b><span>04 · ПОДГОТОВКА ОТПРАВКИ</span></div>
      <div className="bcDemo20__columns"><div className="bcDemo20__form"><h2>Создать {kind[1].toLowerCase()}</h2><label>Тема / продукт<input value={topic} onChange={e=>setTopic(e.target.value)} placeholder="Введите идею" /></label><label>Аудитория<select value={audience} onChange={e=>{setAudience(e.target.value);setDraft(null);}}>{Object.entries(audienceMap).map(([id,v])=><option key={id} value={id}>{v.name}</option>)}</select></label><label>Предложение<select value={duration} onChange={e=>setDuration(e.target.value)}><option value="trial">30 дней демодоступа</option><option value="campaign">Презентация продукта / услуги</option></select></label><label>Тон<select value={tone} onChange={e=>setTone(e.target.value)}><option>Деловой и вдохновляющий</option><option>Дружелюбный</option><option>Премиальный</option><option>Образовательный</option></select></label><button type="button" className="bcDemo20__primary" onClick={generate}>✦ Алина, сгенерируй предложение</button><p className="bcDemo20__hint">Шаблон генерируется локально. Подключение FATHER / LLM — отдельный этап.</p></div>
      <div className="bcDemo20__result"><div className="bcDemo20__sectionhead"><h2>Результат Алины</h2><span>DEMO PREVIEW</span></div>{draft?<><div className="bcDemo20__subject">{draft.subject}</div><p className="bcDemo20__preheader">{draft.preheader}</p><pre>{draft.text}</pre><div className="bcDemo20__actions"><button type="button" onClick={copy}>Копировать текст</button><button type="button" onClick={()=>setDraft(null)}>Очистить</button></div></>:<div className="bcDemo20__empty">Выберите сценарий и нажмите «Сгенерировать». Здесь появится предложение и полный перечень возможностей BOOKCRAFT.</div>}</div></div>
      <section className="bcDemo20__visuals"><div className="bcDemo20__sectionhead"><h2>Визуальные материалы</h2><span>ИЗ БИБЛИОТЕКИ BOOKCRAFT</span></div><div className="bcDemo20__visualgrid">{demoVisuals.map(v=><div className="bcDemo20__visual" key={v.title}><img src={v.src} alt={v.title} loading="lazy"/><span>{v.title}</span></div>)}</div><p className="bcDemo20__hint">Это существующие изображения студии, не результат новой AI-генерации.</p></section>
      <section className="bcDemo20__delivery"><div className="bcDemo20__sectionhead"><h2>Подготовка отправки</h2><span>ТРЕБУЕТ ПОДТВЕРЖДЕНИЯ</span></div><label>Адресаты — один или несколько email<textarea rows="3" value={recipients} onChange={e=>setRecipients(e.target.value)} placeholder="person@example.com, team@example.com" /></label><p className="bcDemo20__hint">Получателей: {addresses.length}. {invalid.length?`Некорректные адреса: ${invalid.join(", ")}`:"Рассылка не выполняется автоматически."}</p><button type="button" className="bcDemo20__primary" disabled={!draft||!valid} onClick={prepare}>✉ Открыть письмо в почтовом приложении</button><p className="bcDemo20__hint">Массовая отправка, списки, согласия и отписка потребуют отдельной интеграции с почтовым сервисом.</p></section>
      {notice&&<div className="bcDemo20__notice" role="status">{notice}</div>}
    </section><aside className="bcDemo20__analytics"><div className="bcDemo20__sectionhead"><h2>Контент-интеллект</h2><span>DEMO / NO LIVE DATA</span></div><div className="bcDemo20__tabs">{[["audience","Аудитория"],["now","Тренды сейчас"],["future","Будущее"],["advice","Советы"]].map(([id,label])=><button type="button" className={activeTab===id?"is-active":""} key={id} onClick={()=>setActiveTab(id)}>{label}</button>)}</div>
      {activeTab==="audience"&&<div className="bcDemo20__analysis"><h3>{a.name}</h3><p><b>Потребность:</b> {a.need}</p><p><b>Сегменты:</b> {audience==="business"?"Малый бизнес · Маркетологи · Владельцы продуктов":audience==="creators"?"Писатели · Блогеры · Продюсеры":audience==="education"?"Преподаватели · Методисты · Онлайн-школы":"Агентства · Продакшн · Фриланс-команды"}</p><p><b>Каналы:</b> {a.channels.join(" · ")}</p><p><b>Гипотеза:</b> аудитории интересен практический результат в короткий срок.</p></div>}
      {activeTab==="now"&&<div className="bcDemo20__analysis"><h3>Текущие направления для проверки</h3><p>AI-автоматизация, короткое видео, персонализация контента, многоканальная публикация.</p><p className="bcDemo20__caution">Это гипотезы для исследования, не измеренные тренды. Для фактического вывода нужны данные, период и регион.</p></div>}
      {activeTab==="future"&&<div className="bcDemo20__analysis"><h3>Гипотезы на 1–3 месяца</h3><p>Агентные процессы, адаптация материалов под сегменты, персонализированные визуальные истории.</p><p className="bcDemo20__caution">Прогноз не подтверждён источниками и не имеет числовой уверенности. До подключения аналитики — только демонстрационный сценарий.</p></div>}
      {activeTab==="advice"&&<div className="bcDemo20__analysis"><h3>Рекомендации Алины</h3><p>Для сегмента «{a.name}» выделить практическую выгоду: {a.need.toLowerCase()}.</p><p>Подготовить 2 версии заголовка, иллюстрацию и короткое письмо с явным призывом к действию.</p><p>Проверить условия 30-дневного доступа до публикации.</p></div>}
      <div className="bcDemo20__sources"><h3>Источники для подключения</h3>{sources.map(s=><a href={s.url} key={s.title} target="_blank" rel="noreferrer"><b>{s.title} ↗</b><small>{s.description}</small></a>)}<p className="bcDemo20__hint">Интеграция API и получение свежих показателей пока не выполнены.</p></div>
      <div className="bcDemo20__alina"><img src="/assets/bookcraft/hero/characters/alina/alina-01.png" alt="Алина"/><div><strong>АЛИНА</strong><small>DEMO READY · FATHER OFFLINE</small></div></div>
    </aside></div>
  </main>;
}