import { useEffect, useMemo, useRef, useState } from "react";
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
  const [workspaceView,setWorkspaceView] = useState("knowledge");
  const [traceLevel,setTraceLevel] = useState("INFO");
  const [sourceQuery,setSourceQuery] = useState("");
  const [runDemo,setRunDemo] = useState(false);
  const [runStage,setRunStage] = useState(0);
  const [projectId,setProjectId] = useState(null);
  const [runId,setRunId] = useState(null);
  const [runState,setRunState] = useState(null);
  const [apiError,setApiError] = useState("");
  const [kbData,setKbData] = useState({});

  const activeMode = projectModes.find(x=>x[0]===mode);
  const isStudy = activeMode?.[3] === "STUDY";
  const pipeline = isStudy ? studyPipeline : authorPipeline;
  const size = useMemo(() => files.reduce((s,f)=>s+f.size,0),[files]);
  const liveStages = [
    ["Подготовка источников","Проверяю файлы, форматы и контрольные суммы",8],
    ["Разделение корпуса","Ищу произведения, сборники, главы и секции",23],
    ["Извлечение evidence","Читаю фрагменты и создаю доказуемые утверждения",47],
    ["Сущности и события","Собираю персонажей, места, события и отношения",66],
    ["Хронология и мир","Строю временные якоря, технологии и состояние мира",82],
    ["Поиск противоречий","Сверяю книги между собой и формирую review queue",94],
    ["Финализация БЗ","Сохраняю граф, индексы и отчёт анализа",100]
  ];
  const effectiveStage = runState?.stage_index >= 0 ? runState.stage_index : runStage;
  const currentLive = liveStages[Math.min(Math.max(effectiveStage,0), liveStages.length-1)];
  const effectiveProgress = runState?.progress ?? currentLive[2];
  const effectiveLabel = runState?.stage_label || currentLive[0];
  const effectiveDetail = runState?.detail || currentLive[1];

  useEffect(()=>{
    if(!runId) return;
    let cancelled=false;
    const poll=async()=>{
      try{
        const res=await fetch(`http://127.0.0.1:8191/api/runs/${runId}`);
        if(!res.ok) throw new Error(`Backend status ${res.status}`);
        const data=await res.json();
        if(cancelled) return;
        setRunState(data);
        if(data.stage_index>=0) setRunStage(data.stage_index);
        if(data.status==="PASS"){
          setPhase("ready");
          setRunDemo(false);
          const names=["sources","structure","works","claims","entities","events","world","graph","conflicts","review_queue"];
          const pairs=await Promise.all(names.map(async name=>{
            const r=await fetch(`http://127.0.0.1:8191/api/projects/${data.project_id}/kb/${name}`);
            return [name,r.ok?await r.json():null];
          }));
          if(!cancelled) setKbData(Object.fromEntries(pairs));
          return;
        }
        if(data.status==="FAIL"){
          setPhase("error");
          setApiError(data.error || "Анализ завершился с ошибкой");
          return;
        }
      }catch(err){
        if(!cancelled) setApiError(`Нет связи с ALINA backend: ${err.message}`);
      }
      if(!cancelled) setTimeout(poll,700);
    };
    poll();
    return()=>{cancelled=true};
  },[runId]);

  async function startAnalysis(){
    setApiError("");
    setKbData({});
    setRunState(null);
    setRunDemo(true);
    setRunStage(0);
    setPhase("running");
    try{
      const form=new FormData();
      form.append("title",title || "Новый проект");
      form.append("mode",mode);
      form.append("intent",intent);
      form.append("areas",JSON.stringify(Array.from(areas)));
      form.append("external_research",String(externalResearch));
      files.forEach(file=>form.append("files",file,file.name));
      const res=await fetch("http://127.0.0.1:8191/api/projects/ingest",{method:"POST",body:form});
      if(!res.ok) throw new Error(await res.text());
      const data=await res.json();
      setProjectId(data.project_id);
      setRunId(data.run_id);
    }catch(err){
      setPhase("error");
      setRunDemo(false);
      setApiError(`Не удалось запустить анализ: ${err.message}. Запустите .\\START_ALINA.ps1`);
    }
  }

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
        <button disabled={!files.length || phase==="running"} onClick={startAnalysis}>
          {files.length ? (isStudy ? "Разобрать и построить базу знаний →" : "Подготовить мир проекта →") : "Сначала загрузите корпус"}
        </button>
      </section>

      {phase!=="setup" && <>
        {runDemo && <section className="asLiveRun">
          <div className="asLiveRunHead">
            <div>
              <small>ALINA LIVE RUN</small>
              <h3>{effectiveLabel}</h3>
              <p>{effectiveDetail}</p>
            </div>
            <strong>{effectiveProgress}%</strong>
          </div>
          <div className="asLiveProgress"><i style={{width:`${effectiveProgress}%`}}/></div>
          <div className="asLiveMeta">
            <span>STAGE {Math.max(effectiveStage,0)+1}/{liveStages.length}</span>
            <span>ACTIVE: {runState?.stage || ["SOURCE","SPLIT","EVIDENCE","ENTITIES","WORLD","CONFLICTS","FINALIZE"][effectiveStage]}</span>
            <span>PRIVATE LOCAL</span>
          </div>
          <div className="asLiveSteps">
            {liveStages.map((x,i)=><button key={x[0]} className={i<effectiveStage?"done":i===effectiveStage?"active":""} disabled={Boolean(runId)} onClick={()=>setRunStage(i)}>
              <b>{i<runStage?"✓":String(i+1).padStart(2,"0")}</b><span>{x[0]}</span>
            </button>)}
          </div>
          <div className="asLiveControls">
            <span>{runId ? `RUN: ${runId}` : "Подключение к backend..."}</span>
            <span>{runState?.status || "STARTING"}</span>
          </div>
        </section>}

        {phase==="error" && <section className="asReady" style={{borderColor:"#7f1d1d"}}>
          <span>!</span><div><b>ALINA остановлена</b><p>{apiError}</p></div>
        </section>}

        {phase==="ready" && <section className="asReady">
          <span>✓</span>
          <div>
            <b>Рабочее место базы знаний открыто</b>
            <p>Локальный backend завершил анализ. Ниже показаны реальные метрики run, структура корпуса и созданные артефакты БЗ.</p>
          </div>
        </section>}

        {phase==="ready" && <section className="asWorkspace">
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

          <div className="asWorkspaceNav">
            <button className={workspaceView==="knowledge"?"active":""} onClick={()=>setWorkspaceView("knowledge")}>База знаний</button>
            <button className={workspaceView==="process"?"active":""} onClick={()=>setWorkspaceView("process")}>Процесс / Trace</button>
            <button className={workspaceView==="graph"?"active":""} onClick={()=>setWorkspaceView("graph")}>Graph Lab</button>
            <button className={workspaceView==="sources"?"active":""} onClick={()=>setWorkspaceView("sources")}>Source Center</button>
            <button className={workspaceView==="forecast"?"active":""} onClick={()=>setWorkspaceView("forecast")}>Прогноз</button>
          </div>

          <div className="asRunReport">
            <article><small>ИСТОЧНИКИ</small><b>{files.length}</b><span>локальных файлов</span></article>
            <article><small>ПРОИЗВЕДЕНИЯ</small><b>{runState?.metrics?.works ?? "—"}{runState?.metrics?.works_expected ? ` / ${runState.metrics.works_expected}` : ""}</b><span>{runState?.metrics?.works_missing != null ? `не найдено: ${runState.metrics.works_missing}` : "по каталогу"}</span></article>
            <article><small>СТРУКТУРНЫЕ ОБЪЕКТЫ</small><b>{runState?.metrics?.entities ?? "—"}</b><span>первичный реестр заголовков</span></article>
            <article><small>СОБЫТИЯ</small><b>{runState?.metrics?.events ?? "—"}</b><span>извлечено</span></article>
            <article><small>ПРОТИВОРЕЧИЯ</small><b>{runState?.metrics?.conflicts ?? "—"}</b><span>структурный cross-check</span></article>
            <article><small>REVIEW</small><b>{runState?.metrics?.review ?? "—"}</b><span>на проверку</span></article>
          </div>


          {workspaceView==="knowledge" && <>
                      <div className="asDonePanel">
                        <div>
                          <small>ЧТО СДЕЛАЛА ALINA</small>
                          <h3>Отчёт выполнения</h3>
                        </div>
                        <div className="asDoneGrid">
                          {[
                            ["Источники приняты","SOURCE"],
                            ["Произведения сопоставлены","SPLIT"],
                            ["Структура корпуса разобрана","SPLIT"],
                            ["Evidence первого слоя создан","EVIDENCE"],
                            ["Первичный реестр построен","ENTITIES"],
                            ["World/Graph foundation создан","WORLD"],
                            ["Структурные противоречия проверены","CONFLICTS"],
                            ["Review queue сформирована","FINALIZE"]
                          ].map(([label,stage],i)=>{
                            const order={SOURCE:0,SPLIT:1,EVIDENCE:2,ENTITIES:3,WORLD:4,CONFLICTS:5,FINALIZE:6};
                            const done=runState?.status==="PASS" || (runState?.stage_index ?? -1)>=order[stage];
                            return <span key={label} className={done?"done":""}>{done?"✓":"○"} {label}</span>;
                          })}
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
                          {kbTab==="works" && kbData.works ? <div className="asWorksResult">
                            <div className="asWorksSummary">
                              <b>{kbData.works.cycle || "Каталог произведений"}</b>
                              <span>Найдено {kbData.works.matched_count ?? 0} из {kbData.works.expected ?? "—"} · не найдено {kbData.works.missing_count ?? 0}</span>
                            </div>
                            <div className="asWorksList">
                              {(kbData.works.matched || []).map(w=><article key={w.work_id}>
                                <span>{w.work_id}</span><b>{w.title}</b><small>{w.publication_year || "—"} · {w.form || "—"}</small><em>MATCHED</em>
                              </article>)}
                              {(kbData.works.missing || []).map(w=><article key={w.work_id} className="missing">
                                <span>{w.work_id}</span><b>{w.title}</b><small>Источник не сопоставлен</small><em>REVIEW</em>
                              </article>)}
                            </div>
                          </div> : <div className="asEmptyState">
                            <span>◇</span>
                            <h3>{kbTabs.find(x=>x[0]===kbTab)?.[1]}</h3>
                            <p>Здесь появятся реальные записи после локального анализа. Любую запись можно будет открыть, увидеть источник, связи, уровень уверенности и историю изменений.</p>
                            <div className="asObjectExample">
                              <div><small>OBJECT</small><b>Персонаж / событие / технология</b></div>
                              <div><small>CONFIDENCE</small><b>0.00–1.00</b></div>
                              <div><small>PROVENANCE</small><b>Книга → глава → фрагмент</b></div>
                              <div><small>STATUS</small><b>CANON / REVIEW / CONFLICT</b></div>
                            </div>
                          </div>}
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
          </>}

          {workspaceView==="process" && <section className="asProcessBoard">
            <div className="asProcessTop">
              <div><small>LIVE PROCESS TRACE</small><h3>Состояние анализа</h3><p>Каждый шаг ALINA должен оставлять трассу: вход, модуль, действие, результат, длительность и ошибку.</p></div>
              <div className="asTraceControls">
                <button className="active">LIVE</button>
                {["INFO","DEBUG","WARN","ERROR"].map(x=><button key={x} className={traceLevel===x?"active":""} onClick={()=>setTraceLevel(x)}>{x}</button>)}
              </div>
            </div>
            <div className="asProcessKpis">
              <article><small>RUN</small><b>{runState?.status || "IDLE"}</b></article>
              <article><small>ACTIVE MODULE</small><b>{runState?.stage || "—"}</b></article>
              <article><small>PROGRESS</small><b>{runState?.progress ?? 0}%</b></article>
              <article><small>ERRORS</small><b>{runState?.error ? 1 : 0}</b></article>
              <article><small>ELAPSED</small><b>00:00:00</b></article>
            </div>
            <div className="asProcessLayout">
              <div className="asStageBoard">
                {studyPipeline.map(([n,name,desc],i)=><article key={name} className={i===0?"ready":""}>
                  <i>{i===0?"●":"○"}</i><div><small>{n}</small><b>{name}</b><span>{desc}</span></div><em>{i===0?"READY":"WAIT"}</em>
                </article>)}
              </div>
              <div className="asTraceLog">
                <div className="asTraceHead"><b>TRACE LOG</b><span>{traceLevel}</span></div>
                <pre>{runState?.trace?.length ? runState.trace.map(e=>`[${e.timestamp}] [${e.stage}] [${e.status}] ${e.action}`).join("\n") : `[SYSTEM] Project opened in PRIVATE LOCAL MODE
[INGEST] Waiting for local backend
[POLICY] External research: ${externalResearch ? "ENABLED" : "DISABLED"}
[POLICY] Git/public export: DISABLED`}</pre>
              </div>
            </div>
            <div className="asTraceSchema">
              <b>Каждая запись трассы:</b>
              <code>timestamp · run_id · stage · agent · action · input_ref · output_ref · status · duration_ms · error</code>
            </div>
          </section>}

          {workspaceView==="graph" && <section className="asGraphLab">
            <div className="asProcessTop">
              <div><small>GRAPH LAB</small><h3>Исследование графа знаний</h3><p>Переход от книги к персонажу, событию, технологии, месту и доказательству без потери происхождения факта.</p></div>
              <div className="asGraphActions"><button>Найти путь</button><button>Показать конфликты</button><button>Сбросить вид</button></div>
            </div>
            <div className="asGraphFilters">
              {["WORK","CHARACTER","EVENT","LOCATION","TECHNOLOGY","RELATION","CLAIM","SOURCE"].map(x=><button key={x}>{x}</button>)}
            </div>
            <div className="asGraphCanvas">
              <svg viewBox="0 0 900 430" role="img" aria-label="Макет графа знаний">
                <line x1="450" y1="210" x2="180" y2="100"/><line x1="450" y1="210" x2="720" y2="100"/>
                <line x1="450" y1="210" x2="210" y2="330"/><line x1="450" y1="210" x2="690" y2="330"/>
                <line x1="180" y1="100" x2="720" y2="100"/><line x1="210" y1="330" x2="690" y2="330"/>
                <g className="center"><circle cx="450" cy="210" r="58"/><text x="450" y="205">WORLD</text><text x="450" y="225">GRAPH</text></g>
                <g><circle cx="180" cy="100" r="42"/><text x="180" y="104">WORK</text></g>
                <g><circle cx="720" cy="100" r="42"/><text x="720" y="104">CHARACTER</text></g>
                <g><circle cx="210" cy="330" r="42"/><text x="210" y="334">EVENT</text></g>
                <g><circle cx="690" cy="330" r="42"/><text x="690" y="334">SOURCE</text></g>
              </svg>
              <div className="asGraphEmpty">Реальные узлы появятся после ingest. Клик по узлу → карточка → связи → evidence → исходный фрагмент.</div>
            </div>
            <div className="asGraphBottom">
              <article><small>SELECTED NODE</small><b>—</b><span>Выберите узел</span></article>
              <article><small>NEIGHBORS</small><b>—</b><span>Связанные объекты</span></article>
              <article><small>CONFLICTS</small><b>—</b><span>Противоречивые рёбра</span></article>
              <article><small>PROVENANCE</small><b>—</b><span>Источник доказательства</span></article>
            </div>
          </section>}

          {workspaceView==="forecast" && <section className="asForecastLab">
            <div className="asProcessTop">
              <div>
                <small>FORECAST LAB</small>
                <h3>Прогноз развития мира и сюжета</h3>
                <p>ALINA строит прогноз только из текущего состояния мира, открытых линий, поведения персонажей и причинных связей. Будущий текст не используется до backtest.</p>
              </div>
              <div className="asForecastBadge">FROZEN FORECAST</div>
            </div>

            <div className="asForecastKpis">
              <article><small>КАНДИДАТОВ</small><b>—</b><span>после Prediction Engine</span></article>
              <article><small>ВЫСОКАЯ ВЕРОЯТНОСТЬ</small><b>—</b><span>confidence ≥ 0.75</span></article>
              <article><small>ОТКРЫТЫЕ ЛИНИИ</small><b>—</b><span>поддерживают прогноз</span></article>
              <article><small>РИСК ПРОТИВОРЕЧИЯ</small><b>—</b><span>с каноном / миром</span></article>
            </div>

            <div className="asForecastControls">
              <button>Следующая сцена</button>
              <button>Следующая глава</button>
              <button>Следующая книга</button>
              <button>1 / 5 / 10 сцен</button>
              <button>Только высокая уверенность</button>
            </div>

            <div className="asForecastList">
              {[1,2,3].map((n,i)=><article key={n}>
                <div className="asForecastRank">0{n}</div>
                <div className="asForecastMain">
                  <div className="asForecastTitle">
                    <b>{i===0?"Наиболее вероятное развитие":i===1?"Альтернативная ветвь":"Слабый, но допустимый сценарий"}</b>
                    <span>{i===0?"HIGH":i===1?"MEDIUM":"LOW"}</span>
                  </div>
                  <p>Реальный прогноз появится после построения состояния мира, причинных связей и открытых сюжетных линий.</p>
                  <div className="asForecastWhy">
                    <span>WHY: open_threads</span>
                    <span>character_state</span>
                    <span>causal_links</span>
                    <span>world_pressure</span>
                  </div>
                </div>
                <div className="asForecastScore">
                  <small>PROBABILITY</small>
                  <b>—</b>
                </div>
              </article>)}
            </div>

            <div className="asForecastExplain">
              <div>
                <small>ПОЧЕМУ ALINA ТАК ДУМАЕТ</small>
                <h4>Прогноз должен быть объяснимым</h4>
                <p>Для каждого кандидата показываем цепочку: факты → состояние → открытая линия → причинная связь → прогноз.</p>
              </div>
              <div className="asForecastChain">
                <span>FACTS</span><i>→</i><span>STATE</span><i>→</i><span>THREAD</span><i>→</i><span>CAUSE</span><i>→</i><span>FORECAST</span>
              </div>
            </div>

            <div className="asBacktestBlock">
              <div>
                <small>BACKTEST</small>
                <h4>Проверить прогноз на уже известном будущем</h4>
                <p>Прогноз замораживается до открытия следующей книги/главы. После этого ALINA считает HIT / PARTIAL / MISS и обновляет калибровку.</p>
              </div>
              <button>Заморозить прогноз</button>
            </div>
          </section>}

          {workspaceView==="sources" && <section className="asSourceCenter">
            <div className="asProcessTop">
              <div><small>SOURCE CENTER</small><h3>Источники и автоматическое исследование</h3><p>Канон, библиография и внешнее исследование хранятся раздельно. Внешний сайт никогда сам не становится каноном.</p></div>
              <div className="asSourceMode"><span>EXTERNAL RESEARCH</span><b className={externalResearch?"on":""}>{externalResearch?"ON":"OFF"}</b></div>
            </div>
            <div className="asSourceSearch"><span>⌕</span><input value={sourceQuery} onChange={e=>setSourceQuery(e.target.value)} placeholder="Название книги, автор, тема, URL или вопрос для исследования..."/><button disabled={!externalResearch}>Искать автоматически</button></div>
            <div className="asSourcePolicy">
              <article><b>CANON SOURCE</b><span>Загруженная книга / подтверждённое издание. Может давать канонические факты.</span></article>
              <article><b>REFERENCE</b><span>Энциклопедия, каталог, интервью, научная публикация. Используется для проверки и контекста.</span></article>
              <article><b>WEB RESEARCH</b><span>Сайт/страница, найденные автоматически. Всегда отделены от канона до проверки.</span></article>
              <article><b>DOWNLOAD POLICY</b><span>Скачиваем полный файл только если он пользовательский, public domain или источник явно разрешает загрузку.</span></article>
            </div>
            <div className="asSourceTable">
              <div className="head"><span>Источник</span><span>Класс</span><span>Доверие</span><span>Статус</span><span>Действия</span></div>
              <div><span>Локальные файлы проекта ({files.length})</span><span>CANON SOURCE</span><span>A</span><span>AVAILABLE</span><span><button>Просмотреть</button><button>Читать</button></span></div>
              <div><span>Внешние источники</span><span>WEB RESEARCH</span><span>—</span><span>{externalResearch?"READY":"DISABLED"}</span><span><button disabled={!externalResearch}>Исследовать</button></span></div>
            </div>
            <div className="asSourceFlow">
              <span>SEARCH</span><i>→</i><span>READ</span><i>→</i><span>EXTRACT</span><i>→</i><span>VERIFY</span><i>→</i><span>CLASSIFY</span><i>→</i><span>ADD TO KB</span>
            </div>
          </section>}
        </section>}
      </>}
    </div>
  );
}
