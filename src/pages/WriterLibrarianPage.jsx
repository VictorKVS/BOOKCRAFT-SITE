import { useMemo, useState } from "react";
import "./WriterLibrarianPage.css";

const patterns = [
  { id:"NP-001", name:"Трёхактная структура", family:"Универсальная", genres:["Фэнтези","Фантастика","Детектив"], verified:"SOURCE_VERIFIED", beats:["Завязка","Противостояние","Разрешение"], score:96 },
  { id:"NP-002", name:"Путешествие героя", family:"Арка героя", genres:["Фэнтези","Попаданцы","Приключения"], verified:"SOURCE_VERIFIED", beats:["Обычный мир","Призыв","Порог","Испытания","Кризис","Возвращение"], score:94 },
  { id:"NP-003", name:"Story Circle", family:"Арка героя", genres:["Фантастика","Драма","Попаданцы"], verified:"SOURCE_VERIFIED", beats:["Комфорт","Желание","Незнакомая ситуация","Адаптация","Получение","Цена","Возврат","Изменение"], score:91 },
  { id:"NP-004", name:"Seven Point Story", family:"Универсальная", genres:["Триллер","Фантастика","Детектив"], verified:"SOURCE_VERIFIED", beats:["Hook","Plot Turn 1","Pinch 1","Midpoint","Pinch 2","Plot Turn 2","Resolution"], score:89 },
  { id:"NP-005", name:"Mystery Investigation", family:"Жанровая", genres:["Детектив","Триллер"], verified:"SOURCE_VERIFIED", beats:["Тайна","Первая улика","Ложный след","Новая гипотеза","Прорыв","Конфронтация","Разгадка"], score:93 },
  { id:"NP-006", name:"Escalation / Failure Loop", family:"Напряжение", genres:["Триллер","Фэнтези","Фантастика"], verified:"UNVERIFIED_HEURISTIC", beats:["Проблема","Меры героя","Провал","Новый план","Ухудшение","Отчаянный шаг","Кризис"], score:84 },
  { id:"NP-007", name:"Goal → Conflict → Disaster", family:"Сцена", genres:["Любой"], verified:"SOURCE_VERIFIED", beats:["Цель","Конфликт","Катастрофа"], score:88 },
  { id:"NP-008", name:"Dramatic Irony", family:"Информация", genres:["Детектив","Триллер","Романтика"], verified:"MULTISOURCE_VERIFIED", beats:["Читатель знает","Герой не знает","Риск растёт","Раскрытие"], score:86 },
];

const sources = [
  ["Story Grid","A","Жанры · сцены · конфликт"],
  ["K.M. Weiland","A","Структура · арки · сцены"],
  ["Novel Factory","A","Outline · персонажи · workflow"],
  ["Save the Cat!","A","15 beats · story types"],
  ["Reedsy","B","Гайды · примеры · структура"],
  ["Plottr","B","Шаблоны · жанровые roadmaps"],
];

const shelves = [
  ["Сюжетные структуры",18,50],
  ["Жанровые паттерны",12,40],
  ["Арки персонажей",9,30],
  ["Сцены и конфликты",14,35],
  ["Напряжение и темп",8,25],
  ["Психология и поведение",3,30],
];

function FlowDiagram({pattern}) {
  const beats = pattern.beats.slice(0, 7);
  const width = 760;
  const gap = width / Math.max(beats.length, 1);
  return (
    <svg className="wlFlow" viewBox={`0 0 ${width} 180`} role="img" aria-label={`Схема: ${pattern.name}`}>
      <defs>
        <linearGradient id={`g-${pattern.id}`} x1="0" x2="1">
          <stop offset="0%" stopColor="#8b5cf6"/>
          <stop offset="100%" stopColor="#22d3ee"/>
        </linearGradient>
        <filter id="shadow"><feDropShadow dx="0" dy="8" stdDeviation="8" floodOpacity=".18"/></filter>
      </defs>
      <path d={`M 42 92 C 160 20, 300 160, 420 82 S 650 40, 720 92`} fill="none" stroke={`url(#g-${pattern.id})`} strokeWidth="5" strokeLinecap="round" opacity=".75"/>
      {beats.map((beat,i) => {
        const x = 42 + i * ((width - 84) / Math.max(beats.length - 1,1));
        const y = 92 + Math.sin(i * 1.35) * 34;
        return (
          <g key={beat} transform={`translate(${x} ${y})`} filter="url(#shadow)">
            <circle r="20" fill="#101827" stroke="#ffffff" strokeWidth="3"/>
            <circle r="7" fill={i === beats.length-1 ? "#22d3ee" : "#a78bfa"}/>
            <text y={i % 2 === 0 ? 44 : -32} textAnchor="middle" className="wlFlowLabel">{beat}</text>
          </g>
        );
      })}
    </svg>
  );
}

export default function WriterLibrarianPage(){
  const [query,setQuery]=useState("");
  const [genre,setGenre]=useState("Все");
  const [selected,setSelected]=useState(patterns[0]);

  const genres=["Все","Попаданцы","Фэнтези","Фантастика","Детектив","Триллер","Романтика"];
  const filtered=useMemo(()=>patterns.filter(p=>{
    const q=query.trim().toLowerCase();
    const text=[p.name,p.family,...p.genres,...p.beats].join(" ").toLowerCase();
    const g=genre==="Все" || p.genres.includes(genre) || p.genres.includes("Любой");
    return g && (!q || text.includes(q));
  }),[query,genre]);

  const verified=patterns.filter(p=>p.verified!=="UNVERIFIED_HEURISTIC").length;

  return (
    <div className="wlPage">
      <section className="wlHero">
        <div>
          <span className="wlEyebrow">FATHER · WRITER LIBRARIAN</span>
          <h1>Библиотека сюжетных систем</h1>
          <p>Поиск, сравнение и визуальное проектирование сюжетов. Источники, схемы, жанровые паттерны и будущий Human Behavior Engine — в одном рабочем месте.</p>
        </div>
        <div className="wlHeroBadge"><b>v1</b><span>KNOWLEDGE WORKSPACE</span></div>
      </section>

      <section className="wlKpis">
        <article><small>ПАТТЕРНЫ</small><strong>{patterns.length}</strong><span>seed library</span></article>
        <article><small>ПРОВЕРЕНО</small><strong>{verified}</strong><span>source-backed</span></article>
        <article><small>ИСТОЧНИКИ</small><strong>{sources.length}</strong><span>priority A/B</span></article>
        <article><small>ПОЛКИ</small><strong>{shelves.length}</strong><span>domain shelves</span></article>
      </section>

      <section className="wlSearchPanel">
        <div className="wlSearchBox">
          <span>⌕</span>
          <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Найти: детектив, ложный след, кризис, попаданец..." />
        </div>
        <div className="wlChips">
          {genres.map(g=><button key={g} className={genre===g?"active":""} onClick={()=>setGenre(g)}>{g}</button>)}
        </div>
      </section>

      <div className="wlLayout">
        <section className="wlCatalog">
          <div className="wlSectionTitle"><div><small>CATALOG</small><h2>Сюжетные схемы</h2></div><span>{filtered.length} найдено</span></div>
          <div className="wlCards">
            {filtered.map(p=>(
              <button key={p.id} className={`wlPatternCard ${selected.id===p.id?"selected":""}`} onClick={()=>setSelected(p)}>
                <div className="wlPatternTop"><span>{p.family}</span><b>{p.score}</b></div>
                <h3>{p.name}</h3>
                <div className="wlMiniFlow">{p.beats.slice(0,5).map((b,i)=><i key={b} title={b}>{i+1}</i>)}</div>
                <p>{p.beats.slice(0,4).join(" → ")}</p>
                <div className="wlTags">{p.genres.map(g=><span key={g}>{g}</span>)}</div>
              </button>
            ))}
          </div>
        </section>

        <aside className="wlSide">
          <div className="wlSideCard">
            <small>KNOWLEDGE HEALTH</small>
            <h3>Наполнение библиотеки</h3>
            {shelves.map(([name,v,max])=>(
              <div className="wlProgress" key={name}>
                <div><span>{name}</span><b>{v}/{max}</b></div>
                <i><em style={{width:`${Math.round(v/max*100)}%`}}/></i>
              </div>
            ))}
          </div>
          <div className="wlSideCard">
            <small>SOURCES</small>
            <h3>Приоритетные базы</h3>
            <div className="wlSources">{sources.map(([name,tier,desc])=><div key={name}><b>{tier}</b><span><strong>{name}</strong><small>{desc}</small></span></div>)}</div>
          </div>
        </aside>
      </div>

      <section className="wlInspector">
        <div className="wlInspectorHead">
          <div><small>{selected.id} · {selected.family}</small><h2>{selected.name}</h2></div>
          <span className={selected.verified==="UNVERIFIED_HEURISTIC"?"warn":"ok"}>{selected.verified}</span>
        </div>
        <FlowDiagram pattern={selected}/>
        <div className="wlBeatGrid">{selected.beats.map((b,i)=><article key={b}><span>{String(i+1).padStart(2,"0")}</span><b>{b}</b><small>{i===0?"Стартовая функция":i===selected.beats.length-1?"Результат / переход":"Драматургический шаг"}</small></article>)}</div>
      </section>
    </div>
  );
}
