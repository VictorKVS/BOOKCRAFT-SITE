import { useMemo, useRef, useState } from "react";
import "./AlinaStudioPage.css";

const projectModes = [
  ["study-book","Изучить одну книгу","Разобрать произведение в базу знаний: главы, персонажи, события, мир, технологии и противоречия.","STUDY"],
  ["study-cycle","Изучить цикл книг","Разложить весь цикл по произведениям, сшить общий мир, хронологию и связи.","STUDY"],
  ["continue-series","Продолжить серию","Сначала изучить корпус и восстановить мир, затем предложить продолжение.","AUTHOR"],
  ["continue-book","Продолжить книгу","Продолжить с конкретной точки после проверки канона и состояния мира.","AUTHOR"],
  ["existing-world","Новый сюжет в существующем мире","Сохранить правила и канон мира, но открыть новую сюжетную линию.","AUTHOR"],
  ["original","Новый оригинальный мир","Построить новую БЗ мира и начать цикл с нуля.","AUTHOR"],
  ["game","Игровой сценарий","Мир + сюжетный граф + выборы + последствия + квесты + концовки.","GAME"],
  ["alt-history","Альтернативная история","Историческая база + точка расхождения + причинные последствия.","AUTHOR"]
];

const researchAreas = [
  "Хронология","Персонажи","События","Локации","Технологии","Отношения",
  "История","География","Политика и власть","Военное дело","Экономика",
  "Религия и культура","Быт","Медицина","Профессии","Транспорт","Наука"
];

const studyPipeline = [
  ["01","SOURCE","Файл / серия"],
  ["02","SPLIT","Произведения и главы"],
  ["03","EVIDENCE","Факты + источник"],
  ["04","KNOWLEDGE","Сущности и связи"],
  ["05","WORLD","Единая модель мира"],
  ["06","CONFLICTS","Дыры и противоречия"],
  ["07","REVIEW","Проверка человеком"]
];

const authorPipeline = [
  ["01","CORPUS","Изученная база"],
  ["02","CANON","Проверенный канон"],
  ["03","STATE","Текущее состояние мира"],
  ["04","THREADS","Открытые линии"],
  ["05","SIMULATOR","Варианты будущего"],
  ["06","AUTHOR","Выбор автора"],
  ["07","WRITE","План → сцены → текст"]
];

const kbTabs = [
  ["summary","Обзор"],
  ["works","Произведения"],
  ["characters","Персонажи"],
  ["events","События"],
  ["timeline","Хронология"],
  ["world","Мир"],
  ["technology","Технологии"],
  ["relations","Связи"],
  ["conflicts","Противоречия"],
  ["evidence","Доказательства"],
  ["review","На проверку"]
];

export default function AlinaStudioPage() {
  const inputRef = useRef(null);
  const [mode,setMode] = useState("study-cycle");
  const [title,setTitle] = useState("Алиса Селезнёва — цикл");
  const [intent,setIntent] = useState("Разложить цикл по произведениям, построить базу знаний, восстановить хронологию и мир, найти противоречия.");
  const [files,setFiles] = useState([]);
  const [areas,setAreas] = useState(new Set(["Хронология","Персонажи","События","Локации","Технологии","Отношения"]));
  const [phase,setPhase] = useState("setup");
  const [externalResearch,setExternalResearch] = useState(false);
  const [kbTab,setKbTab] = useState("summary");
  const [kbQuery,setKbQuery] = useState("");

  const activeMode = projectModes.find(x=>x[0]===mode);
  const isStudy = activeMode?.[3] === "STUDY";
  const pipeline = isStudy ? studyPipeline : authorPipeline;
  const size = useMemo(() => files.reduce((s,f)=>s+f.size,0),[files]);

  function chooseMode(id){
    setMode(id);
    if(id==="study-book"){
      setIntent("Разобрать одну книгу в базу знаний: структура, персонажи, события, мир, технологии, связи и противоречия.");
    } else if(id==="study-cycle"){
      setIntent("Разложить цикл по произведениям, построить общую базу знаний, восстановить хронологию и мир, найти противоречия.");
    }
  }

  function addFiles(e){
    const next = Array.from(e.target.files || []);
    setFiles(prev => {
      const map = new Map(prev.map(f=>[f.name+"-"+f.size,f]));
      next.forEach(f=>map.set(f.name+"-"+f.size,f));
      return Array.from(map.values());
    });
    e.target.value = "";
  }

  function removeFile(key){
    setFiles(prev=>prev.filter(f=>f.name+"-"+f.size!==key));
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
      <section className="asPrivacy">
        <div className="asPrivacyIcon">⌂</div>
        <div>
          <b>PRIVATE LOCAL MODE</b>
          <span>Учебный проект. Файлы остаются в текущей локальной сессии браузера. Публикация и внешний поиск выключены.</span>
        </div>
        <div className="asPrivacyState">LOCAL ONLY</div>
      </section>

      <section className="asHero">
        <div>
          <span className="asEyebrow">FATHER · ALINA KNOWLEDGE & STORY FACTORY</span>
          <h1>Новый проект</h1>
          <p>Сначала ALINA изучает книгу или цикл и строит доказуемую базу знаний. Продолжение сюжета открывается только после проверки мира, хронологии и канона.</p>
        </div>
        <div className="asStatus">
          <b>{phase === "setup" ? "PRIVATE" : "READY"}</b>
          <span>{isStudy ? "KNOWLEDGE BUILD" : "STORY PROJECT"}</span>
        </div>
      </section>

      <div className="asStepper">
        {["Тип проекта","Корпус","Что извлекать","База знаний","Работа с миром"].map((x,i)=>
          <div key={x} className={i===0 ? "active" : ""}><i>{i+1}</i><span>{x}</span></div>
        )}
      </div>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>STEP 01</small><h2>Что делаем с материалом?</h2></div>
          <span>Изучение и написание разделены</span>
        </div>

        <div className="asModeGrid">
          {projectModes.map(([id,name,desc,type])=>(
            <button key={id} className={mode===id ? "selected" : ""} onClick={()=>chooseMode(id)}>
              <em>{type}</em>
              <strong>{name}</strong>
              <span>{desc}</span>
            </button>
          ))}
        </div>

        <div className="asFields">
          <label><span>Название проекта</span><input value={title} onChange={e=>setTitle(e.target.value)}/></label>
          <label><span>Задача ALINA</span><textarea rows="4" value={intent} onChange={e=>setIntent(e.target.value)}/></label>
        </div>
      </section>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>STEP 02</small><h2>{isStudy ? "Загрузить книгу или цикл" : "Загрузить основу проекта"}</h2></div>
          <span>FB2 · PDF · EPUB · DOCX · TXT</span>
        </div>

        <input ref={inputRef} className="asHidden" type="file" multiple accept=".fb2,.pdf,.epub,.docx,.txt" onChange={addFiles}/>
        <button className="asDrop" onClick={()=>inputRef.current?.click()}>
          <b>＋ Добавить локальные файлы</b>
          <span>Файлы выбираются с вашего компьютера и пока не отправляются ни в GitHub, ни во внешний сервис.</span>
        </button>

        <div className="asFileSummary">
          <article><small>ФАЙЛОВ</small><b>{files.length}</b></article>
          <article><small>ОБЪЁМ</small><b>{size ? (size/1024/1024).toFixed(1)+" MB" : "0 MB"}</b></article>
          <article><small>ПРИВАТНОСТЬ</small><b>LOCAL ONLY</b></article>
        </div>

        {files.length > 0 && <div className="asFiles">
          {files.map((f,i)=>{
            const key=f.name+"-"+f.size;
            return <div key={key}>
              <span><b>{String(i+1).padStart(2,"0")}</b>{f.name}</span>
              <span className="asFileRight"><small>{(f.size/1024/1024).toFixed(2)} MB</small><button onClick={()=>removeFile(key)}>×</button></span>
            </div>;
          })}
        </div>}
      </section>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>STEP 03</small><h2>Что положить в базу знаний?</h2></div>
          <span>Каждый вывод должен хранить связь с исходным фрагментом</span>
        </div>
        <div className="asResearch">
          {researchAreas.map(a=><button key={a} className={areas.has(a)?"active":""} onClick={()=>toggleArea(a)}>{areas.has(a)?"✓ ":"＋ "}{a}</button>)}
        </div>

        <div className="asExternal">
          <div>
            <b>Внешнее исследование</b>
            <span>По умолчанию выключено. Пока учимся — ALINA строит БЗ только из загруженных материалов.</span>
          </div>
          <button className={externalResearch?"on":""} onClick={()=>setExternalResearch(v=>!v)} aria-pressed={externalResearch}>
            {externalResearch ? "РАЗРЕШЕНО" : "ВЫКЛЮЧЕНО"}
          </button>
        </div>
      </section>

      <section className="asPipeline">
        <div className="asPanelTitle">
          <div><small>ALINA PIPELINE</small><h2>{isStudy ? "Как строится база знаний" : "Как строится продолжение"}</h2></div>
          <span>{isStudy ? "Сначала понимание, потом творчество" : "Только поверх проверенной БЗ"}</span>
        </div>
        <div className="asPipeGrid">
          {pipeline.map(([n,name,desc])=><article key={n}><span>{n}</span><strong>{name}</strong><small>{desc}</small></article>)}
        </div>
        <div className="asRules">
          <span>NO SOURCE → NO TRUSTED KNOWLEDGE</span>
          <span>NO PROVENANCE → NO GRAPH EDGE</span>
          <span>PRIVATE BY DEFAULT</span>
        </div>
      </section>

      <section className="asKbPreview">
        <div className="asPanelTitle">
          <div><small>PROJECT OUTPUT</small><h2>Что появится после разбора</h2></div>
          <span>Отдельно для каждой книги + общая модель цикла</span>
        </div>
        <div className="asKbGrid">
          <article><b>Произведения</b><span>WORK-ID, редакции, главы, источники</span></article>
          <article><b>Персонажи</b><span>биография, знания, состояния, отношения</span></article>
          <article><b>События</b><span>кто, где, когда, причины и последствия</span></article>
          <article><b>Мир</b><span>локации, правила, институты, ресурсы</span></article>
          <article><b>Технологии</b><span>что существует, где применяется, ограничения</span></article>
          <article><b>Хронология</b><span>якоря, интервалы, несовместимости</span></article>
          <article><b>Связи</b><span>граф персонажей, событий и объектов</span></article>
          <article><b>Противоречия</b><span>ретконы, дыры, конфликтующие факты</span></article>
        </div>
      </section>

      <section className="asLaunch">
        <div>
          <small>PRIVATE PROJECT</small>
          <h2>{title || "Новый проект"}</h2>
          <p>{files.length ? `Локальных файлов: ${files.length}. Выбрано слоёв БЗ: ${areas.size}. Внешний поиск: ${externalResearch ? "разрешён" : "выключен"}.` : "Добавьте книгу или цикл для запуска локального разбора."}</p>
        </div>
        <button disabled={!files.length} onClick={()=>setPhase("ready")}>
          {files.length ? (isStudy ? "Разобрать и построить базу знаний →" : "Подготовить мир проекта →") : "Сначала загрузите корпус"}
        </button>
      </section>

      {phase==="ready" && <>
        <section className="asReady">
          <span>✓</span>
          <div>
            <b>Рабочее место базы знаний открыто</b>
            <p>Сейчас показан интерфейс результата. Когда подключим локальный backend, сюда будут поступать реальные объекты, метрики и evidence из ALINA AUTO CORPUS INGEST.</p>
          </div>
        </section>

        <section className="asWorkspace">
          <div className="asWorkspaceHead">
            <div>
              <small>ALINA KNOWLEDGE WORKSPACE</small>
              <h2>{title || "Новый проект"}</h2>
              <p>Результат анализа, состояние БЗ и точки, где нужен человек.</p>
            </div>
            <div className="asWorkspaceActions">
              <button>Экспорт отчёта</button>
              <button className="primary">Продолжить работу с миром →</button>
            </div>
          </div>

          <div className="asRunReport">
            <article><small>ИСТОЧНИКИ</small><b>{files.length}</b><span>локальных файлов</span></article>
            <article><small>ПРОИЗВЕДЕНИЯ</small><b>—</b><span>после ingest</span></article>
            <article><small>СУЩНОСТИ</small><b>—</b><span>персонажи / места / объекты</span></article>
            <article><small>СОБЫТИЯ</small><b>—</b><span>после extraction</span></article>
            <article><small>ПРОТИВОРЕЧИЯ</small><b>—</b><span>после cross-check</span></article>
            <article><small>REVIEW</small><b>—</b><span>неуверенные выводы</span></article>
          </div>

          <div className="asDonePanel">
            <div>
              <small>ЧТО СДЕЛАЛА ALINA</small>
              <h3>Отчёт выполнения</h3>
            </div>
            <div className="asDoneGrid">
              <span className="done">✓ Источники приняты</span>
              <span>○ Определить произведения</span>
              <span>○ Разделить на главы</span>
              <span>○ Извлечь evidence</span>
              <span>○ Построить сущности и связи</span>
              <span>○ Собрать хронологию</span>
              <span>○ Найти противоречия</span>
              <span>○ Сформировать review queue</span>
            </div>
          </div>

          <div className="asKbToolbar">
            <div className="asKbTabs">
              {kbTabs.map(([id,label])=><button key={id} className={kbTab===id?"active":""} onClick={()=>setKbTab(id)}>{label}</button>)}
            </div>
            <div className="asKbSearch"><span>⌕</span><input value={kbQuery} onChange={e=>setKbQuery(e.target.value)} placeholder="Поиск по базе знаний..."/></div>
          </div>

          <div className="asKbBody">
            <aside className="asKbSide">
              <b>Фильтры</b>
              <label><input type="checkbox" defaultChecked/> Только подтверждённые</label>
              <label><input type="checkbox"/> Только с конфликтами</label>
              <label><input type="checkbox"/> Требует проверки</label>
              <hr/>
              <small>УВЕРЕННОСТЬ</small>
              <button>Высокая</button>
              <button>Средняя</button>
              <button>Низкая</button>
            </aside>

            <section className="asKbContent">
              <div className="asEmptyState">
                <span>◇</span>
                <h3>{kbTabs.find(x=>x[0]===kbTab)?.[1]}</h3>
                <p>Здесь появятся реальные записи после локального анализа. Любую запись можно будет открыть, увидеть источник, связи, уровень уверенности и историю изменений.</p>
                <div className="asObjectExample">
                  <div><small>OBJECT</small><b>Персонаж / событие / технология</b></div>
                  <div><small>CONFIDENCE</small><b>0.00–1.00</b></div>
                  <div><small>PROVENANCE</small><b>Книга → глава → фрагмент</b></div>
                  <div><small>STATUS</small><b>CANON / REVIEW / CONFLICT</b></div>
                </div>
              </div>
            </section>

            <aside className="asInspector">
              <small>INSPECTOR</small>
              <h3>Карточка объекта</h3>
              <p>Выберите запись в БЗ.</p>
              <div><span>Источник</span><b>—</b></div>
              <div><span>Уверенность</span><b>—</b></div>
              <div><span>Связей</span><b>—</b></div>
              <div><span>Конфликтов</span><b>—</b></div>
              <hr/>
              <button>Подтвердить</button>
              <button>Исправить</button>
              <button>Пометить спорным</button>
            </aside>
          </div>
        </section>
      </>}
    </div>
  );
}
