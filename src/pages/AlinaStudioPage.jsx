import { useMemo, useRef, useState } from "react";
import "./AlinaStudioPage.css";

const modes = [
  ["continue-series","Продолжить серию","Загрузить цикл, восстановить мир и продолжить его."],
  ["continue-book","Продолжить книгу","Продолжить с конкретной точки одного произведения."],
  ["existing-world","Новый сюжет в существующем мире","Сохранить канон мира, но создать новую линию."],
  ["original","Новый оригинальный мир","Построить мир с нуля и начать новый цикл."],
  ["game","Игровой сценарий","Ветки, выборы, квесты, состояния мира и концовки."],
  ["alt-history","Альтернативная история","Историческая база + точка расхождения + последствия."]
];

const researchAreas = [
  "История","География","Политика и власть","Военное дело","Экономика",
  "Технологии","Религия и культура","Быт","Медицина","Профессии",
  "Транспорт","Хронология","Наука","Социальные отношения"
];

const pipeline = [
  ["01","CORPUS","Файлы и произведения"],
  ["02","EVIDENCE","Факты с привязкой к источнику"],
  ["03","CANON","Надёжный канон"],
  ["04","WORLD","Мир, правила, ресурсы"],
  ["05","CHARACTERS","Персонажи и мышление"],
  ["06","THREADS","Открытые линии"],
  ["07","SIMULATOR","Варианты продолжения"]
];

export default function AlinaStudioPage() {
  const inputRef = useRef(null);
  const [mode,setMode] = useState("continue-series");
  const [title,setTitle] = useState("Алиса Селезнёва — реконструкция цикла");
  const [intent,setIntent] = useState("Собрать цикл по произведениям, восстановить хронологию и мир, найти противоречия и подготовить продолжение.");
  const [files,setFiles] = useState([]);
  const [areas,setAreas] = useState(new Set(["Хронология","Технологии","География","Социальные отношения"]));
  const [phase,setPhase] = useState("setup");

  const size = useMemo(() => files.reduce((s,f)=>s+f.size,0),[files]);

  function addFiles(e){
    const next = Array.from(e.target.files || []);
    setFiles(prev => {
      const map = new Map(prev.map(f=>[f.name+"-"+f.size,f]));
      next.forEach(f=>map.set(f.name+"-"+f.size,f));
      return Array.from(map.values());
    });
    e.target.value = "";
  }

  function toggleArea(a){
    setAreas(prev=>{
      const n=new Set(prev);
      n.has(a)?n.delete(a):n.add(a);
      return n;
    });
  }

  return (
    <div className="asPage">
      <section className="asHero">
        <div>
          <span className="asEyebrow">FATHER · ALINA STORY FACTORY</span>
          <h1>От источников к живому миру</h1>
          <p>Загрузите книги, задайте цель и область исследования. ALINA собирает корпус, отделяет канон от предположений, строит мир и только после этого открывает продолжение сюжета.</p>
        </div>
        <div className="asStatus">
          <b>{phase === "setup" ? "SETUP" : "READY"}</b>
          <span>PROJECT ENTRY</span>
        </div>
      </section>

      <div className="asStepper">
        {["Что пишем","Корпус","Исследование","Построить мир","Продолжить"].map((x,i)=>
          <div key={x} className={i===0 ? "active" : ""}><i>{i+1}</i><span>{x}</span></div>
        )}
      </div>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>STEP 01</small><h2>Что будем писать?</h2></div>
          <span>Выберите режим проекта</span>
        </div>

        <div className="asModeGrid">
          {modes.map(([id,name,desc])=>(
            <button key={id} className={mode===id ? "selected" : ""} onClick={()=>setMode(id)}>
              <strong>{name}</strong><span>{desc}</span>
            </button>
          ))}
        </div>

        <div className="asFields">
          <label><span>Название проекта</span><input value={title} onChange={e=>setTitle(e.target.value)}/></label>
          <label><span>Что вы хотите получить</span><textarea rows="4" value={intent} onChange={e=>setIntent(e.target.value)}/></label>
        </div>
      </section>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>STEP 02</small><h2>Загрузить основу</h2></div>
          <span>FB2 · PDF · EPUB · DOCX · TXT</span>
        </div>

        <input ref={inputRef} className="asHidden" type="file" multiple accept=".fb2,.pdf,.epub,.docx,.txt" onChange={addFiles}/>
        <button className="asDrop" onClick={()=>inputRef.current?.click()}>
          <b>＋ Добавить книги и материалы</b>
          <span>Серия, отдельные книги, заметки автора, исторические источники</span>
        </button>

        <div className="asFileSummary">
          <article><small>ФАЙЛОВ</small><b>{files.length}</b></article>
          <article><small>ОБЪЁМ</small><b>{size ? (size/1024/1024).toFixed(1)+" MB" : "0 MB"}</b></article>
          <article><small>СТАТУС</small><b>{files.length ? "ГОТОВО К INGEST" : "ОЖИДАНИЕ"}</b></article>
        </div>

        {files.length > 0 && <div className="asFiles">
          {files.map((f,i)=><div key={f.name+"-"+f.size}><span><b>{String(i+1).padStart(2,"0")}</b>{f.name}</span><small>{(f.size/1024/1024).toFixed(2)} MB</small></div>)}
        </div>}
      </section>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>STEP 03</small><h2>Что исследовать?</h2></div>
          <span>Writer Librarian будет собирать внешнюю базу отдельно от канона</span>
        </div>
        <div className="asResearch">
          {researchAreas.map(a=><button key={a} className={areas.has(a)?"active":""} onClick={()=>toggleArea(a)}>{areas.has(a)?"✓ ":"＋ "}{a}</button>)}
        </div>
      </section>

      <section className="asPipeline">
        <div className="asPanelTitle">
          <div><small>ALINA PIPELINE</small><h2>Что произойдёт после запуска</h2></div>
          <span>Никакой генерации «с потолка»</span>
        </div>
        <div className="asPipeGrid">
          {pipeline.map(([n,name,desc])=><article key={n}><span>{n}</span><strong>{name}</strong><small>{desc}</small></article>)}
        </div>
        <div className="asRules">
          <span>NO SOURCE → NO CANON</span>
          <span>NO WORLD REVIEW → NO CONTINUATION</span>
          <span>NO STATE UPDATE → NO NEXT CHAPTER</span>
        </div>
      </section>

      <section className="asLaunch">
        <div>
          <small>PROJECT READY</small>
          <h2>{title || "Новый проект"}</h2>
          <p>{files.length ? `Загружено файлов: ${files.length}. Выбрано областей исследования: ${areas.size}.` : "Добавьте корпус, чтобы ALINA могла начать автоматический разбор."}</p>
        </div>
        <button disabled={!files.length} onClick={()=>setPhase("ready")}>
          {files.length ? "Исследовать и построить мир →" : "Сначала загрузите корпус"}
        </button>
      </section>

      {phase==="ready" && <section className="asReady">
        <span>✓</span>
        <div><b>Фронтенд проекта готов к запуску ingest</b><p>Следующий технический слой подключит эту кнопку к ALINA AUTO CORPUS INGEST и будет показывать реальный прогресс по произведениям.</p></div>
      </section>}
    </div>
  );
}
