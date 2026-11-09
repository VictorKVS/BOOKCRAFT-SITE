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
  const [title,setTitle] = useState("");
  const [titleTouched,setTitleTouched] = useState(false);
  const [intent,setIntent] = useState("Разложить цикл по произведениям, построить базу знаний, восстановить хронологию и мир, найти противоречия.");
  const [description,setDescription] = useState("");
  const [files,setFiles] = useState([]);
  const [savedSources,setSavedSources] = useState([]);
  const [projectState,setProjectState] = useState(null);
  const [projectEvents,setProjectEvents] = useState([]);
  const [areas,setAreas] = useState(new Set(["Хронология","Персонажи","События","Локации","Технологии","Отношения"]));
  const [phase,setPhase] = useState("setup");
  const [externalResearch,setExternalResearch] = useState(false);
  const [kbTab,setKbTab] = useState("summary");
  const [kbQuery,setKbQuery] = useState("");
  const [workspaceView,setWorkspaceView] = useState("dashboard");
  const [traceLevel,setTraceLevel] = useState("INFO");
  const [sourceQuery,setSourceQuery] = useState("");
  const [runDemo,setRunDemo] = useState(false);
  const [runStage,setRunStage] = useState(0);
  const [projectId,setProjectId] = useState(null);
  const [runId,setRunId] = useState(null);
  const [runState,setRunState] = useState(null);
  const [apiError,setApiError] = useState("");
  const [kbData,setKbData] = useState({});
  const [projects,setProjects] = useState([]);
  const [projectHistory,setProjectHistory] = useState({});
  const [historyOpen,setHistoryOpen] = useState(null);
  const [deleteModal,setDeleteModal] = useState(null);
  const [deleteBusy,setDeleteBusy] = useState(false);
  const [deepModel,setDeepModel] = useState(null);
  const [benchmarkSeed,setBenchmarkSeed] = useState(null);
  const [benchmarkBusy,setBenchmarkBusy] = useState(false);
  const [referenceAnalysis,setReferenceAnalysis] = useState(null);
  const [referenceBusy,setReferenceBusy] = useState(false);
  const [sourceCount,setSourceCount] = useState(0);
  const [sourceBusy,setSourceBusy] = useState(false);
  const [projectBusy,setProjectBusy] = useState(false);
  const [projectMeta,setProjectMeta] = useState(null);
  const [products,setProducts] = useState([]);
  const [creativeType,setCreativeType] = useState("COMIC");
  const [creativeTitle,setCreativeTitle] = useState("");
  const [creativeBusy,setCreativeBusy] = useState(false);
  const [analysisProfile,setAnalysisProfile] = useState("CANON_FULL");
  const [analysisDepth,setAnalysisDepth] = useState("FULL");
  const [uiTrace,setUiTrace] = useState([]);
  const [githubDebugStatus,setGithubDebugStatus] = useState("WAITING");
  const [adminSettings,setAdminSettings] = useState({github_debug_trace:false,local_trace:true});
  const [adminVisible,setAdminVisible] = useState(false);
  const [adminBusy,setAdminBusy] = useState(false);
  const [researchDashboard,setResearchDashboard] = useState(null);
  const [selectedResearchWork,setSelectedResearchWork] = useState(null);
  const [researchBusy,setResearchBusy] = useState(false);
  const [researchAction,setResearchAction] = useState("");
  const [researchGraph,setResearchGraph] = useState(null);
  const [selectedCorpusObject,setSelectedCorpusObject] = useState(null);
  const [sourceIntel,setSourceIntel] = useState(null);
  const [sourceIntelBusy,setSourceIntelBusy] = useState(false);
  const [commandCenter,setCommandCenter] = useState(null);
  const [reportBusy,setReportBusy] = useState(false);

  const activeMode = projectModes.find(x=>x[0]===mode);
  const isStudy = activeMode?.[3] === "STUDY";
  const pipeline = isStudy ? studyPipeline : authorPipeline;
  const size = useMemo(() => files.reduce((s,f)=>s+f.size,0),[files]);
  const savedSize = useMemo(() => savedSources.reduce((s,f)=>s+(f.size_bytes || 0),0),[savedSources]);
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
  const sequenceState = useMemo(()=>{
    const latest={};
    for(const e of uiTrace){
      if(e.event_type==="SEQUENCE" && e.sequence){
        latest[e.sequence]=e;
      }
    }
    return latest;
  },[uiTrace]);

  async function loadAdminSettings(){
    try{
      const r=await window.fetch("http://127.0.0.1:8191/api/admin/settings");
      if(r.ok){
        const data=await r.json();
        setAdminSettings(data);
        if(!data.github_debug_trace) setGithubDebugStatus("DISABLED");
        return data;
      }
    }catch{}
    return null;
  }

  async function updateAdminSetting(key,value){
    setAdminBusy(true);
    try{
      const form=new FormData();
      form.append(key,String(value));
      const r=await window.fetch("http://127.0.0.1:8191/api/admin/settings",{method:"PATCH",body:form});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setAdminSettings(data);
      if(!data.github_debug_trace) setGithubDebugStatus("DISABLED");
      else setGithubDebugStatus("WAITING");
      setUiTrace(prev=>[...prev.slice(-299),{
        timestamp:new Date().toISOString(),
        event_type:"ADMIN_SETTINGS",
        status:"PASS",
        action_id:key,
        result:value ? "ON":"OFF"
      }]);
    }catch(err){
      setApiError("Не удалось изменить настройку администрирования: "+err.message);
    }finally{
      setAdminBusy(false);
    }
  }

  function safeEndpoint(url){
    try{
      const u=new URL(url,window.location.origin);
      return u.pathname;
    }catch{
      return String(url).split("?")[0].slice(0,160);
    }
  }

  async function traceEvent(eventType,payload={},publish=true){
    const event={
      event_type:eventType,
      action_id:payload.action_id || null,
      button:payload.button || null,
      project_id:projectId || payload.project_id || null,
      project_code:projectMeta?.short_code || payload.project_code || null,
      run_id:runId || payload.run_id || null,
      workspace_view:workspaceView,
      phase,
      ...payload,
      timestamp:new Date().toISOString()
    };
    setUiTrace(prev=>[...prev.slice(-299),event]);
    try{
      const form=new FormData();
      form.append("event",eventType);
      form.append("payload",JSON.stringify(event));
      const r=await window.fetch("http://127.0.0.1:8191/api/debug/trace",{method:"POST",body:form});
      if(r.ok){
        const data=await r.json();
        if(data.admin_settings) setAdminSettings(data.admin_settings);
        if(data.github?.status) setGithubDebugStatus(data.github.status);
      }else if(adminSettings.github_debug_trace){
        setGithubDebugStatus("WARN");
      }
    }catch{
      if(adminSettings.github_debug_trace) setGithubDebugStatus("WARN");
    }
  }

  async function tracedFetch(url,options={}){
    const method=(options.method || "GET").toUpperCase();
    const endpoint=safeEndpoint(url);
    const isPoll=endpoint.startsWith("/api/runs/");
    const isDebug=endpoint.startsWith("/api/debug/trace");
    const started=performance.now();
    if(!isPoll && !isDebug){
      traceEvent("API_START",{
        action_id:`${method} ${endpoint}`,
        method,endpoint,status:"START"
      },false);
    }
    try{
      const response=await window.fetch(url,options);
      if(!isPoll && !isDebug){
        traceEvent("API_END",{
          action_id:`${method} ${endpoint}`,
          method,endpoint,http_status:response.status,
          status:response.ok?"PASS":"ERROR",
          duration_ms:Math.round(performance.now()-started)
        },method!=="GET");
      }
      return response;
    }catch(err){
      if(!isPoll && !isDebug){
        traceEvent("API_END",{
          action_id:`${method} ${endpoint}`,
          method,endpoint,status:"ERROR",
          result:String(err?.message || err),
          duration_ms:Math.round(performance.now()-started)
        },method!=="GET");
      }
      throw err;
    }
  }

  function handleButtonTrace(e){
    const button=e.target.closest?.("button");
    if(!button || button.disabled) return;
    const label=(button.getAttribute("data-trace") || button.textContent || "BUTTON")
      .replace(/\s+/g," ").trim().slice(0,100);
    traceEvent("BUTTON",{
      action_id:`BUTTON:${label}`,
      button:label,
      status:"CLICK"
    },true);
  }

  function inferClientTitle(list){
    if(!list.length) return "";
    const clean = name => name
      .replace(/\.[^.]+$/,"")
      .replace(/[_-]+/g," ")
      .replace(/\b(original|litmir|club|edition|fb2|pdf|docx|epub)\b/gi," ")
      .replace(/\s+/g," ")
      .trim();
    if(list.length===1) return clean(list[0].name).slice(0,100);
    return `Цикл из ${list.length} книг`;
  }

  async function importAliceReferenceAnalysis(){
    if(!projectId) return;
    setReferenceBusy(true);
    setApiError("");
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/import-alice-reference-analysis`,{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setReferenceAnalysis(data);
      setProjectMeta(prev=>prev ? {...prev,reference_analysis:{
        id:data.reference_id,scope:data.scope,status:data.status,chunk_count:data.chunk_count,maturity:data.maturity
      }} : prev);
      await loadResearchDashboard(projectId);
      setSelectedResearchWork("ALICE-005");
      traceEvent("SEQUENCE",{sequence:"ANALYSIS_FLOW",step:"REFERENCE_ANALYSIS_IMPORTED",status:"PASS",result:data.reference_id},true);
    }catch(err){
      setApiError("Не удалось подключить старый анализ Алисы: "+err.message);
    }finally{
      setReferenceBusy(false);
    }
  }

  async function importAliceBenchmark(){
    if(!projectId) return;
    setBenchmarkBusy(true);
    setApiError("");
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/import-alice-benchmark`,{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setBenchmarkSeed(data);
      setKbData(prev=>({...prev,benchmark_seed:data,works:{...(prev.works||{}),benchmark:{
        seed_id:data.seed_id,
        expected:data.cycle_expected,
        verified_in_big_fb2:data.source_audit?.matched_works,
        missing_from_big_fb2:data.source_audit?.missing_from_source,
        separate_star_dog_source_present:data.current_project_expected_matches===52,
        expected_current_total:data.current_project_expected_matches,
        status:"MANUAL_VERIFIED_BENCHMARK"
      }}}));
    }catch(err){
      setApiError("Не удалось импортировать эталон Алисы: "+err.message);
    }finally{
      setBenchmarkBusy(false);
    }
  }

  async function checkDeepModel(){
    try{
      const r=await tracedFetch("http://127.0.0.1:8191/api/deep/model-status");
      if(r.ok){
        const data=await r.json();
        setDeepModel(data);
        return data;
      }
    }catch{}
    const fallback={available:false,provider:"NONE"};
    setDeepModel(fallback);
    return fallback;
  }

  async function selectLocalGguf(){
    setApiError("");
    try{
      const r=await tracedFetch("http://127.0.0.1:8191/api/deep/select-gguf",{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setDeepModel(data);
      if(data.status==="CANCELLED") return;
      if(data.needs_package){
        setApiError("Модель выбрана, но ALINA backend не видит llama-cpp-python. Установите его в .venv-alina или используйте Ollama.");
      }
    }catch(err){
      setApiError("Не удалось выбрать GGUF-модель: "+err.message);
    }
  }

  async function clearLocalModel(){
    try{
      const r=await tracedFetch("http://127.0.0.1:8191/api/deep/clear-model",{method:"POST"});
      if(r.ok) setDeepModel(await r.json());
    }catch{}
  }

  async function startDeepAnalysis(){
    if(!projectId) return;
    setApiError("");
    const model=await checkDeepModel();
    if(!model?.available){
      setApiError("Глубокий анализ не запущен: локальная LLM не обнаружена.");
      return;
    }
    try{
      const form=new FormData();
      form.append("profile",analysisProfile);
      form.append("config",JSON.stringify({
        depth:analysisDepth,
        full_components:true,
        evidence_required:true,
        chronology:true,
        contradictions:true,
        forecast_inputs:true
      }));
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/deep-analysis`,{method:"POST",body:form});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();

      if(data.status==="NEEDS_MODEL"){
        setApiError("Глубокий анализ не запущен: backend не нашёл локальную модель.");
        return;
      }
      if(data.status==="REUSED"){
        setRunId(null);
        setRunDemo(false);
        setPhase("ready");
        setRunState({
          run_type:"DEEP_ANALYSIS",
          status:"REUSED",
          progress:100,
          detail:"Источники и параметры анализа не изменились — использована существующая семантическая БЗ.",
          metrics:{analysis_profile:data.analysis_profile,analysis_fingerprint:data.analysis_fingerprint}
        });
        const pr=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}`);
        if(pr.ok) setProjectMeta(await pr.json());
        traceEvent("SEQUENCE",{sequence:"ANALYSIS_FLOW",step:"DEEP_REUSED",status:"REUSED",analysis_profile:data.analysis_profile,kb_version:data.kb_version},true);
        return;
      }

      traceEvent("SEQUENCE",{sequence:"ANALYSIS_FLOW",step:"DEEP_STARTED",status:"QUEUED",analysis_profile:data.analysis_profile,run_id:data.run_id},true);
      setRunId(data.run_id);
      setRunState({...data,run_type:"DEEP_ANALYSIS"});
      setRunDemo(true);
      setPhase("running");
    }catch(err){
      setApiError("Не удалось запустить глубокий анализ: "+err.message);
    }
  }

  async function loadResearchDashboard(projectIdValue){
    if(!projectIdValue){
      setResearchDashboard(null);
      setSelectedResearchWork(null);
      return null;
    }
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectIdValue}/research`);
      if(r.ok){
        const data=await r.json();
        setResearchDashboard(data);
        if(!selectedResearchWork && data.programs?.length){
          setSelectedResearchWork(data.programs[0].work_id);
          loadResearchGraph(data.programs[0].work_id);
        } else if(selectedResearchWork){
          loadResearchGraph(selectedResearchWork);
        }
        return data;
      }
    }catch{}
    setResearchDashboard(null);
    return null;
  }

  async function simulateSourceIntelligence(objectId){
    if(!projectId || !objectId) return;
    setSourceIntelBusy(true);
    setApiError("");
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/source-intelligence/${objectId}/simulate`,{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setSourceIntel(data);
      await loadProjectState(projectId);
      traceEvent("SEQUENCE",{
        sequence:"SOURCE_INTELLIGENCE",
        step:objectId,
        status:"PASS",
        result:"SIMULATED_OSINT"
      },true);
    }catch(err){
      setApiError("Source Intelligence: "+err.message);
    }finally{
      setSourceIntelBusy(false);
    }
  }

  async function loadResearchGraph(workId){
    if(!projectId || !workId){
      setResearchGraph(null);
      return null;
    }
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/research/${workId}/graph`);
      if(r.ok){
        const data=await r.json();
        setResearchGraph(data);
        return data;
      }
    }catch{}
    setResearchGraph(null);
    return null;
  }

  async function runResearchTask(workId,taskId){
    if(!projectId || !workId || !taskId) return;
    setResearchBusy(true);
    setResearchAction(taskId);
    setApiError("");
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/research/${workId}/tasks/${taskId}/run`,{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      await loadResearchDashboard(projectId);
      await loadResearchGraph(workId);
      traceEvent("SEQUENCE",{
        sequence:"RESEARCH_FLOW",
        step:`${workId}:${taskId}`,
        status:data.status || "PASS",
        result:data.task?.quality_gate || data.status
      },true);
    }catch(err){
      setApiError(`Research ${workId}/${taskId}: ${err.message}`);
    }finally{
      setResearchBusy(false);
      setResearchAction("");
    }
  }

  async function runNextResearchTask(workId){
    if(!projectId || !workId) return;
    setResearchBusy(true);
    setResearchAction("NEXT");
    setApiError("");
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/research/${workId}/next`,{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      await loadResearchDashboard(projectId);
      await loadResearchGraph(workId);
      traceEvent("SEQUENCE",{
        sequence:"RESEARCH_FLOW",
        step:`${workId}:NEXT`,
        status:data.status || "PASS",
        result:data.task?.task_id || "NO_READY_TASKS"
      },true);
    }catch(err){
      setApiError(`Research ${workId}: ${err.message}`);
    }finally{
      setResearchBusy(false);
      setResearchAction("");
    }
  }

  async function runResearchAuto(workId){
    if(!projectId || !workId) return;
    setResearchBusy(true);
    setResearchAction("AUTO");
    setApiError("");
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/research/${workId}/auto`,{method:"POST"});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      await loadResearchDashboard(projectId);
      await loadResearchGraph(workId);
      traceEvent("SEQUENCE",{
        sequence:"RESEARCH_FLOW",
        step:`${workId}:AUTO`,
        status:data.status || "PASS",
        result:(data.executed || []).map(x=>`${x.task_id}:${x.status}`).join(",").slice(0,220)
      },true);
    }catch(err){
      setApiError(`Research AUTO ${workId}: ${err.message}`);
    }finally{
      setResearchBusy(false);
      setResearchAction("");
    }
  }

  async function loadProjects(){
    try{
      const r=await tracedFetch("http://127.0.0.1:8191/api/projects");
      if(r.ok) setProjects(await r.json());
    }catch{
      // Backend may be offline while the page is opened.
    }
  }

  async function toggleHistory(projectId){
    if(historyOpen===projectId){ setHistoryOpen(null); return; }
    setHistoryOpen(projectId);
    if(projectHistory[projectId]) return;
    const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/runs`);
    if(r.ok){
      const data=await r.json();
      setProjectHistory(prev=>({...prev,[projectId]:data}));
    }
  }

  async function openProjectFolder(project, folder){
    const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${project.project_id}/open-folder/${folder}`,{method:"POST"});
    if(!r.ok) alert("Не удалось открыть папку: "+await r.text());
  }

  async function renameLocalProject(project){
    const next=window.prompt("Новое название проекта", project.title || "");
    if(next===null || !next.trim()) return;
    const form=new FormData();
    form.append("title",next.trim());
    const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${project.project_id}/title`,{method:"PATCH",body:form});
    if(!r.ok){
      alert("Не удалось переименовать проект: "+await r.text());
      return;
    }
    if(projectId===project.project_id){
      setTitle(next.trim());
      setTitleTouched(true);
      setProjectMeta(prev=>prev ? {...prev,title:next.trim()} : prev);
    }
    await loadProjects();
  }

  async function performDeleteRun(projectIdValue, runIdValue){
    setDeleteBusy(true);
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectIdValue}/runs/${runIdValue}`,{method:"DELETE"});
      if(!r.ok) throw new Error(await r.text());
      setProjectHistory(prev=>({
        ...prev,
        [projectIdValue]:(prev[projectIdValue] || []).filter(x=>x.run_id!==runIdValue)
      }));
      await loadProjects();
      setDeleteModal(null);
    }catch(err){
      alert("Не удалось удалить run: "+err.message);
    }finally{
      setDeleteBusy(false);
    }
  }

  async function performDeleteProject(project){
    setDeleteBusy(true);
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${project.project_id}`,{method:"DELETE"});
      if(!r.ok) throw new Error(await r.text());
      if(projectId===project.project_id){
        setPhase("setup");
        setProjectId(null);
        setRunId(null);
        setRunState(null);
        setKbData({});
        setProjectMeta(null);
        setProducts([]);
        setResearchDashboard(null);
        setSelectedResearchWork(null);
        setProjectState(null);
        setProjectEvents([]);
        setSavedSources([]);
        setFiles([]);
      }
      setProjectHistory(prev=>{const n={...prev}; delete n[project.project_id]; return n;});
      setHistoryOpen(null);
      await loadProjects();
      setDeleteModal(null);
    }catch(err){
      alert("Не удалось удалить проект: "+err.message);
    }finally{
      setDeleteBusy(false);
    }
  }

  async function loadCommandCenter(projectIdValue){
    if(!projectIdValue) return null;
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectIdValue}/command-center`);
      if(!r.ok) return null;
      const data=await r.json();
      setCommandCenter(data);
      return data;
    }catch{
      return null;
    }
  }

  async function exportProjectReport(){
    if(!projectId) return;
    setReportBusy(true);
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/report`);
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json;charset=utf-8"});
      const url=URL.createObjectURL(blob);
      const a=document.createElement("a");
      a.href=url;
      a.download=`${projectMeta?.short_code || "ALINA"}_project_report.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      await loadCommandCenter(projectId);
    }catch(err){
      setApiError("Экспорт отчёта: "+err.message);
    }finally{
      setReportBusy(false);
    }
  }

  function openCommandTarget(target){
    if(!target) return;
    setWorkspaceView(target);
  }

  async function loadProjectState(projectIdValue){
    try{
      const [sr,er]=await Promise.all([
        tracedFetch(`http://127.0.0.1:8191/api/projects/${projectIdValue}/state`),
        tracedFetch(`http://127.0.0.1:8191/api/projects/${projectIdValue}/events?limit=100`)
      ]);
      const state=sr.ok?await sr.json():null;
      const events=er.ok?await er.json():[];
      if(state){
        setProjectState(state);
        setSavedSources(state.source_set?.sources || []);
        setSourceCount(state.source_set?.count || 0);
      }
      setProjectEvents(events || []);
      await loadCommandCenter(projectIdValue);
      return state;
    }catch{
      return null;
    }
  }

  async function ensureAliceVerifiedCorpus(projectIdValue, projectLike){
    const probe=((projectLike?.title || "")+" "+(projectLike?.description || "")).toLowerCase();
    if(!probe.includes("алиса")) return null;
    try{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectIdValue}/source-intelligence/import-alice-verified-corpus`,{method:"POST"});
      if(!r.ok) return null;
      return await r.json();
    }catch{
      return null;
    }
  }

  async function openLocalProject(project){
    setProjectId(project.project_id);
    setFiles([]);
    setWorkspaceView("dashboard");
    const detailResponse=await tracedFetch(`http://127.0.0.1:8191/api/projects/${project.project_id}`);
    const detail=detailResponse.ok ? await detailResponse.json() : project;
    setProjectMeta(detail);
    await ensureAliceVerifiedCorpus(project.project_id, detail);
    setProjectState(detail.project_state || null);
    setSelectedCorpusObject(null);
    setSavedSources(detail.saved_sources || detail.project_state?.source_set?.sources || []);
    setReferenceAnalysis(detail.reference_analysis || null);
    setSourceCount(detail.project_state?.source_set?.count ?? detail.source_count ?? 0);
    setTitle(detail.title || "");
    setDescription(detail.description || detail.intent || "");
    setTitleTouched(true);
    const rr=await tracedFetch(`http://127.0.0.1:8191/api/projects/${project.project_id}/runs`);
    const runs=rr.ok?await rr.json():[];
    const latest=runs[0] || project.latest_run;
    if(latest){
      setRunId(null);
      setRunState(latest);
    }
    const names=["sources","structure","works","claims","entities","events","world","graph","conflicts","review_queue","characters","relations","locations","technologies","organizations","time_anchors","deep_claims","open_threads","deep_graph","benchmark_seed"];
    const pairs=await Promise.all(names.map(async name=>{
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${project.project_id}/kb/${name}`);
      return [name,r.ok?await r.json():null];
    }));
    const loaded=Object.fromEntries(pairs);
    setKbData(loaded);
    setBenchmarkSeed(loaded.benchmark_seed || null);
    await loadProducts(project.project_id);
    await loadResearchDashboard(project.project_id);
    await loadProjectState(project.project_id);
    setPhase("ready");
    setRunDemo(false);
    window.scrollTo({top:document.body.scrollHeight,behavior:"smooth"});
  }

  useEffect(()=>{ loadProjects(); checkDeepModel(); loadAdminSettings(); },[]);

  useEffect(()=>{
    let cancelled=false;
    const pollGit=async()=>{
      try{
        const r=await window.fetch("http://127.0.0.1:8191/api/debug/github-status");
        if(r.ok){
          const data=await r.json();
          if(!cancelled){
            setGithubDebugStatus(data.enabled ? (data.status || "WAITING") : "DISABLED");
          }
        }
      }catch{}
      if(!cancelled) setTimeout(pollGit,1500);
    };
    pollGit();
    return()=>{cancelled=true};
  },[]);

  useEffect(()=>{
    if(!projectId || !researchDashboard?.programs?.some(p=>p.program_status==="RUNNING")) return;
    let cancelled=false;
    const pollResearch=async()=>{
      if(cancelled) return;
      await loadResearchDashboard(projectId);
      if(!cancelled) setTimeout(pollResearch,1200);
    };
    const timer=setTimeout(pollResearch,1200);
    return()=>{cancelled=true; clearTimeout(timer);};
  },[projectId,researchDashboard?.programs?.map(p=>p.program_status).join("|")]);

  useEffect(()=>{
    if(!runId) return;
    let cancelled=false;
    const poll=async()=>{
      try{
        const res=await tracedFetch(`http://127.0.0.1:8191/api/runs/${runId}`);
        if(!res.ok) throw new Error(`Backend status ${res.status}`);
        const data=await res.json();
        if(cancelled) return;
        setRunState(data);
        if(data.project_title && !titleTouched) setTitle(data.project_title);
        if(data.stage_index>=0) setRunStage(data.stage_index);
        if(data.status==="PASS"){
          traceEvent("SEQUENCE",{sequence:data.run_type==="DEEP_ANALYSIS"?"ANALYSIS_FLOW":"PROJECT_FLOW",step:data.run_type==="DEEP_ANALYSIS"?"DEEP_COMPLETED":"FOUNDATION_COMPLETED",status:"PASS",run_id:data.run_id},true);
          setPhase("ready");
          setRunDemo(false);
          const names=["sources","structure","works","claims","entities","events","world","graph","conflicts","review_queue","characters","relations","locations","technologies","organizations","time_anchors","deep_claims","open_threads","deep_graph","benchmark_seed"];
          const pairs=await Promise.all(names.map(async name=>{
            const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${data.project_id}/kb/${name}`);
            return [name,r.ok?await r.json():null];
          }));
          if(!cancelled) {
            const loaded=Object.fromEntries(pairs);
            setKbData(loaded);
            setBenchmarkSeed(loaded.benchmark_seed || null);
            const pr=await tracedFetch(`http://127.0.0.1:8191/api/projects/${data.project_id}`);
            if(pr.ok){
              const meta=await pr.json();
              setTitle(meta.title || title);
              setProjectMeta(meta);
              setSourceCount(meta.source_count || sourceCount);
            }
            await loadProducts(data.project_id);
            await loadResearchDashboard(data.project_id);
            await loadProjectState(data.project_id);
            if(data.run_type!=="DEEP_ANALYSIS") setWorkspaceView("research");
            loadProjects();
          }
          return;
        }
        if(data.status==="NEEDS_MODEL"){
          setPhase("ready");
          setRunDemo(false);
          setApiError(data.detail || "Локальная модель не найдена");
          checkDeepModel();
          return;
        }
        if(data.status==="FAIL"){
          setRunDemo(false);
          if(data.run_type==="DEEP_ANALYSIS"){
            setPhase("ready");
            setApiError((data.error || "Глубокий анализ прерван") + " · Сохранён checkpoint. Повторный запуск продолжит с последнего успешно обработанного chunk.");
            setWorkspaceView("process");
          }else{
            setPhase("error");
            setApiError(data.error || "Анализ завершился с ошибкой");
          }
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

  async function createProjectContract(){
    const clean=title.trim();
    if(!clean){
      setApiError("Сначала задайте название проекта.");
      return;
    }
    setProjectBusy(true);
    setApiError("");
    try{
      const form=new FormData();
      form.append("title",clean);
      form.append("mode",mode);
      form.append("intent",intent);
      form.append("description",description.trim() || intent);
      const r=await tracedFetch("http://127.0.0.1:8191/api/projects",{method:"POST",body:form});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setProjectId(data.project_id);
      setProjectMeta(data);
      setProjectState(data.project_state || null);
      setSavedSources([]);
      setProjectEvents([]);
      setProducts([]);
      setTitle(data.title);
      setDescription(data.description || "");
      setTitleTouched(true);
      setSourceCount(data.source_count || 0);
      setPhase("setup");
      traceEvent("SEQUENCE",{sequence:"PROJECT_FLOW",step:"PROJECT_CREATED",status:"PASS",project_id:data.project_id,project_code:data.short_code},true);
      await loadProjects();
    }catch(err){
      setApiError("Не удалось создать проект: "+err.message);
    }finally{
      setProjectBusy(false);
    }
  }

  async function attachSourcesToProject(){
    if(!projectId){
      setApiError("Сначала создайте проект.");
      return;
    }
    if(!files.length){
      setApiError("Выберите хотя бы одну книгу.");
      return;
    }
    setSourceBusy(true);
    setApiError("");
    try{
      const form=new FormData();
      files.forEach(file=>form.append("files",file,file.name));
      const r=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/sources`,{method:"POST",body:form});
      if(!r.ok) throw new Error(await r.text());
      const data=await r.json();
      setSourceCount(data.project_state?.source_set?.count ?? data.project?.source_count ?? files.length);
      setProjectMeta(data.project || null);
      setProjectState(data.project_state || null);
      setSavedSources(data.project_state?.source_set?.sources || []);
      setFiles([]);
      await loadProjectState(projectId);
      traceEvent("SEQUENCE",{sequence:"PROJECT_FLOW",step:"SOURCES_ATTACHED",status:"PASS",source_count:data.project_state?.source_set?.count ?? data.project?.source_count ?? files.length,result:data.source_changed ? "SOURCE_SET_CHANGED" : "SOURCE_SET_REUSED"},true);
      await loadProjects();
    }catch(err){
      setApiError("Не удалось добавить книги в проект: "+err.message);
    }finally{
      setSourceBusy(false);
    }
  }

  async function startAnalysis(){
    if(!projectId){
      setApiError("Сначала создайте проект.");
      return;
    }
    if(sourceCount < 1){
      setApiError("Сначала сохраните книги в проект.");
      return;
    }
    setApiError("");
    setKbData({});
    setRunState(null);
    setRunDemo(true);
    setRunStage(0);
    setPhase("running");
    try{
      const res=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}/foundation-analysis`,{method:"POST"});
      if(!res.ok) throw new Error(await res.text());
      const data=await res.json();
      if(data.status==="REUSED"){
        const pr=await tracedFetch(`http://127.0.0.1:8191/api/projects/${projectId}`);
        if(pr.ok){
          const meta=await pr.json();
          setProjectMeta(meta);
        }
        setRunState({
          run_type:"FOUNDATION_REUSE",
          status:"REUSED",
          progress:100,
          metrics:runState?.metrics || {},
          detail:"Источники не изменились — первичный разбор повторно не выполнялся."
        });
        setRunDemo(false);
        setPhase("ready");
        setApiError("");
        await loadResearchDashboard(projectId);
        setWorkspaceView("research");
        traceEvent("SEQUENCE",{sequence:"PROJECT_FLOW",step:"FOUNDATION_REUSED",status:"REUSED",kb_version:data.kb_version},true);
        return;
      }
      traceEvent("SEQUENCE",{sequence:"PROJECT_FLOW",step:"FOUNDATION_STARTED",status:"QUEUED",run_id:data.run_id},true);
      setRunId(data.run_id);
    }catch(err){
      setPhase("error");
      setRunDemo(false);
      setApiError("Не удалось запустить построение БЗ: "+err.message);
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

  function requestRemoveFile(file){
    setDeleteModal({type:"file",file,key:file.name+"-"+file.size});
  }

  function performRemoveFile(key){
    setFiles(prev=>{
      const next=prev.filter(f=>f.name+"-"+f.size!==key);
      if(!titleTouched) setTitle(inferClientTitle(next));
      return next;
    });
    setDeleteModal(null);
  }

  function toggleArea(a){
    setAreas(prev=>{
      const n=new Set(prev);
      n.has(a)?n.delete(a):n.add(a);
      return n;
    });
  }

  return (
    <div className="asPage" onClickCapture={handleButtonTrace}>
      <section className="asPrivacy">
        <div className="asPrivacyIcon">⌂</div>
        <div>
          <b>PRIVATE LOCAL MODE</b>
          <span>Учебный проект. Файлы остаются в текущей локальной сессии браузера. Публикация и внешний поиск выключены.</span>
        </div>
        <div className="asPrivacyState">LOCAL ONLY</div>
      </section>

      <section className="asProjectManager">
        <div className="asManagerHead">
          <div><small>LOCAL PROJECT MANAGER</small><h2>Мои проекты</h2><p>Проекты, базы знаний и история запусков хранятся только локально.</p></div>
          <div className="asManagerTools">
            <button onClick={()=>setAdminVisible(v=>!v)}>⚙ Администрирование</button>
            <button onClick={loadProjects}>↻ Обновить</button>
          </div>
        </div>
        {projects.length===0 ? <div className="asNoProjects">Пока нет сохранённых проектов. Создайте первый ниже.</div> :
        <div className="asProjectList">
          {projects.map(p=><article key={p.project_id}>
            <div className="asProjectMain">
              <small>{p.short_code || "—"} · {p.project_id}</small>
              <b>{p.short_code ? `${p.short_code} — ${p.title}` : p.title}</b>
              <p className="asProjectDescription">{p.description || p.intent || "Описание проекта пока не задано."}</p>
              <span>Sources: {p.source_count || 0} · Source Set v{p.source_set_version || 0} · KB v{p.kb_version || 0} · Products: {p.product_count || 0}</span>
              <span>{p.latest_run ? `${p.latest_run.status} · runs: ${p.run_count} · works: ${p.latest_run.metrics?.works ?? "—"}` : "Ещё не анализировался"}</span>
              <div className="asProjectFolders">
                <button onClick={()=>openProjectFolder(p,"sources")}>📁 Тексты</button>
                <button onClick={()=>openProjectFolder(p,"kb")}>📁 База знаний</button>
                <button onClick={()=>openProjectFolder(p,"runs")}>📁 История</button>
                <button onClick={()=>openProjectFolder(p,"products")}>📁 Products</button>
                <em>{p.analysis_level==="FOUNDATION_ONLY"?"ПЕРВИЧНЫЙ РАЗБОР":"ГЛУБОКИЙ АНАЛИЗ"}</em>
              </div>
            </div>
            <div className="asProjectActions">
              <button onClick={()=>openLocalProject(p)}>Открыть</button>
              <button onClick={()=>renameLocalProject(p)}>Переименовать</button>
              <button onClick={()=>toggleHistory(p.project_id)}>История</button>
              <button className="danger" onClick={()=>setDeleteModal({type:"project",project:p})}>Удалить проект</button>
            </div>
            {historyOpen===p.project_id && <div className="asHistory">
              {(projectHistory[p.project_id] || []).length===0 ? <span>История пока пуста.</span> :
                (projectHistory[p.project_id] || []).map(r=><div key={r.run_id}>
                  <b>{r.run_id}</b>
                  <span>{r.status} · {r.progress ?? 0}%</span>
                  <span>works {r.metrics?.works ?? "—"} / {r.metrics?.works_expected ?? "—"}</span>
                  <small>{r.updated_at || r.created_at}</small>
                  <button className="danger" onClick={()=>setDeleteModal({type:"run",project:p,run:r})}>Удалить run</button>
                </div>)}
            </div>}
          </article>)}
        </div>}
      </section>

      {adminVisible && <section className="asAdminPanel">
        <div className="asAdminHead">
          <div>
            <small>SYSTEM ADMINISTRATION</small>
            <h2>Администрирование</h2>
            <p>Управление наблюдаемостью и отладочными интеграциями ALINA.</p>
          </div>
          <button onClick={()=>setAdminVisible(false)}>Закрыть</button>
        </div>

        <div className="asAdminGrid">
          <article>
            <div>
              <small>LOCAL TRACE</small>
              <b>Локальная трассировка</b>
              <span>Кнопки, API и последовательности сохраняются локально для диагностики.</span>
            </div>
            <button
              className={adminSettings.local_trace ? "toggle on":"toggle"}
              disabled={adminBusy}
              onClick={()=>updateAdminSetting("local_trace",!adminSettings.local_trace)}
            ><i></i><em>{adminSettings.local_trace ? "ON":"OFF"}</em></button>
          </article>

          <article className={adminSettings.github_debug_trace ? "github-on":""}>
            <div>
              <small>GITHUB DEBUG TRACE</small>
              <b>Публикация трассировки в GitHub</b>
              <span>Нужна только при совместной отладке. Можно отключить одной кнопкой.</span>
            </div>
            <button
              className={adminSettings.github_debug_trace ? "toggle on":"toggle"}
              disabled={adminBusy}
              onClick={()=>updateAdminSetting("github_debug_trace",!adminSettings.github_debug_trace)}
            ><i></i><em>{adminSettings.github_debug_trace ? "ON":"OFF"}</em></button>
          </article>
        </div>

        <div className="asAdminStatus">
          <div><small>GITHUB STATUS</small><b>{adminSettings.github_debug_trace ? githubDebugStatus : "DISABLED"}</b></div>
          <div><small>TRACE FILE</small><b>projects/.../debug/alina_ui_trace.jsonl</b></div>
          <div><small>PRIVACY</small><b>SAFE DEBUG ONLY</b></div>
        </div>

        <div className="asAdminPolicy">
          <b>Что разрешено отправлять:</b>
          <span>кнопка · API endpoint · статус · длительность · project/run ID · этап последовательности.</span>
          <b>Что запрещено:</b>
          <span>тексты книг · фрагменты · содержимое БЗ · имена исходных файлов · приватные prompts.</span>
        </div>
      </section>}

      <section className="asHero asSimpleHero">
        <div>
          <span className="asEyebrow">FATHER · ALINA KNOWLEDGE FACTORY</span>
          <h1>Новый проект</h1>
          <p>Назовите проект, загрузите книгу или цикл книг — ALINA сама разберёт корпус и откроет рабочую базу знаний.</p>
        </div>
        <div className="asStatus">
          <b>{phase === "setup" ? "PRIVATE" : phase === "running" ? "RUNNING" : "READY"}</b>
          <span>LOCAL KNOWLEDGE PROJECT</span>
        </div>
      </section>

      <div className="asSimpleSteps">
        <div className={projectId ? "active done" : "active"}><i>1</i><span>Название и проект</span></div>
        <div className={sourceCount>0 ? "active done" : projectId ? "active" : ""}><i>2</i><span>Книги проекта</span></div>
        <div className={phase==="ready" ? "active done" : sourceCount>0 ? "active" : ""}><i>3</i><span>Исследовательский комплекс</span></div>
      </div>

      <section className="asPanel asSimpleProject">
        <div className="asPanelTitle">
          <div><small>ШАГ 1</small><h2>Название проекта</h2></div>
          <span>Проект остаётся локальным</span>
        </div>
        <label className="asProjectName">
          <span>{projectId ? `PROJECT CONTRACT · ${projectId}` : "Название обязательно. Сначала создаём проект, потом добавляем книги."}</span>
          <input disabled={Boolean(projectId)} value={title} onChange={e=>{setTitle(e.target.value);setTitleTouched(true)}} placeholder="Например: Алиса Селезнёва — цикл"/>
        </label>
        <label className="asProjectDescriptionField">
          <span>Краткое описание проекта</span>
          <textarea
            disabled={Boolean(projectId)}
            value={description}
            onChange={e=>setDescription(e.target.value)}
            maxLength={500}
            placeholder="Например: Исследование цикла об Алисе Селезнёвой: произведения, персонажи, хронология, технологии, противоречия и восстановление единой модели мира."
          />
          <small>{description.length}/500</small>
        </label>
        <div className="asContractActions">
          {!projectId ? <button className="primary" disabled={!title.trim() || projectBusy} onClick={createProjectContract}>
            {projectBusy ? "Создаю проект…" : "Создать проект →"}
          </button> : <div className="asContractReady">
            <b>✓ Проект создан</b>
            <span>{projectMeta?.short_code || "—"} · {projectId} · sources / kb / runs / deep / products готовы</span>
          </div>}
        </div>
        {apiError && !projectId && <div className="asSetupError">{apiError}</div>}
      </section>

      <section className="asPanel">
        <div className="asPanelTitle">
          <div><small>ШАГ 2</small><h2>Загрузить книги</h2></div>
          <span>FB2 · PDF · EPUB · DOCX · TXT</span>
        </div>

        <input ref={inputRef} className="asHidden" type="file" multiple accept=".fb2,.pdf,.epub,.docx,.txt" onChange={addFiles}/>
        <button className="asDrop" disabled={!projectId} onClick={()=>projectId && inputRef.current?.click()}>
          <b>＋ Добавить книгу или цикл книг</b>
          <span>Можно выбрать один файл, несколько книг или большой сборник.</span>
        </button>

        <div className="asFileSummary">
          <article><small>СОХРАНЕНО</small><b>{savedSources.length}</b></article>
          <article><small>В ПРОЕКТЕ</small><b>{savedSize ? (savedSize/1024/1024).toFixed(1)+" MB" : "0 MB"}</b></article>
          <article><small>ДОБАВИТЬ</small><b>{files.length}</b></article>
          <article><small>ХРАНЕНИЕ</small><b>LOCAL ONLY</b></article>
        </div>

        {savedSources.length > 0 && <div className="asSavedSources">
          <div className="asSavedSourcesHead">
            <b>Сохранённые материалы проекта</b>
            <span>Источник: project_state.json</span>
          </div>
          {savedSources.map((f,i)=><div key={(f.sha256 || f.filename)+"-"+i}>
            <span><b>{String(i+1).padStart(2,"0")}</b>{f.filename}</span>
            <span className="asFileRight">
              <small>{((f.size_bytes || 0)/1024/1024).toFixed(2)} MB · {String(f.extension || "").replace(".","").toUpperCase()}</small>
              <em>СОХРАНЁН</em>
            </span>
          </div>)}
        </div>}

        {files.length > 0 && <div className="asFiles">
          {files.map((f,i)=>{
            const key=f.name+"-"+f.size;
            return <div key={key}>
              <span><b>{String(i+1).padStart(2,"0")}</b>{f.name}</span>
              <span className="asFileRight"><small>{(f.size/1024/1024).toFixed(2)} MB</small><button className="asTrashBtn" title="Удалить файл" onClick={()=>requestRemoveFile(f)}>⌫</button></span>
            </div>;
          })}
        </div>}

        <div className="asSourceCommit">
          <div>
            <small>ИСТОЧНИКИ ПРОЕКТА</small>
            <b>{sourceCount} файл(а/ов) зарегистрировано в project_state.json</b>
          </div>
          <button disabled={!projectId || !files.length || sourceBusy} onClick={attachSourcesToProject}>
            {sourceBusy ? "Сохраняю…" : "Сохранить книги в проект →"}
          </button>
        </div>
      </section>

      <section className="asLaunch asSimpleLaunch">
        <div>
          <small>ШАГ 3</small>
          <h2>Подготовить корпус и запустить исследование</h2>
          <p>{!projectId
            ? "Сначала создайте проект."
            : sourceCount<1
              ? "Проект создан. Теперь добавьте и сохраните книги."
              : `В проекте сохранено ${sourceCount} источник(а/ов). Сначала ALINA подготовит структуру корпуса, затем автоматически запустит Research Complex по произведениям.`}</p>
        </div>
        <button disabled={!projectId || sourceCount<1 || phase==="running"} onClick={startAnalysis}>
          {phase==="running" ? "ALINA готовит корпус…" : "Запустить исследовательский комплекс →"}
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
            <span>{runState?.run_type==="DEEP_ANALYSIS" ? "DEEP SEMANTIC RUN" : `STAGE ${Math.max(effectiveStage,0)+1}/${liveStages.length}`}</span>
            <span>ACTIVE: {runState?.stage || ["SOURCE","SPLIT","EVIDENCE","ENTITIES","WORLD","CONFLICTS","FINALIZE"][effectiveStage]}</span>
            <span>PRIVATE LOCAL</span>
            {runState?.current_total > 0 && <span>TEXT: {runState.current_item}/{runState.current_total}</span>}
          </div>
          {runState?.current_name && <div className="asCurrentText">
            <small>СЕЙЧАС ОБРАБАТЫВАЕТСЯ</small>
            <b>{runState.current_name}</b>
          </div>}
          {runState?.run_type==="DEEP_ANALYSIS" ? <div className="asDeepLive">
            <article><small>MODEL</small><b>{runState?.model_name || runState?.model?.model || "—"}</b></article>
            <article><small>CHUNK</small><b>{runState?.current_total ? `${runState.current_item} / ${runState.current_total}` : "—"}</b></article>
            <article><small>CHARS</small><b>{(runState?.chars_processed || 0).toLocaleString("ru-RU")}</b></article>
            <article><small>SECTION</small><b>{runState?.current_name || "—"}</b></article>
          </div> : <div className="asLiveSteps">
            {liveStages.map((x,i)=><button key={x[0]} className={i<effectiveStage?"done":i===effectiveStage?"active":""} disabled={Boolean(runId)} onClick={()=>setRunStage(i)}>
              <b>{i<runStage?"✓":String(i+1).padStart(2,"0")}</b><span>{x[0]}</span>
            </button>)}
          </div>}
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
            <b>Foundation завершён — Research Complex запущен</b>
            <p>Структура корпуса готова. Теперь ALINA последовательно исследует произведения по R01–R30, проверяет evidence и строит взвешенные графы узлов и связей.</p>
          </div>
        </section>}

        {phase==="ready" && researchDashboard && <section className="asResearchNow">
          {(()=>{
            const programs=researchDashboard.programs || [];
            const running=programs.find(p=>p.program_status==="RUNNING");
            const active=running || programs.find(p=>["ACTIVE","REVIEW"].includes(p.program_status)) || programs[0];
            const task=active?.tasks?.find(t=>t.status==="RUNNING") || active?.tasks?.find(t=>t.status==="READY");
            return <>
              <div>
                <small>RESEARCH STATUS</small>
                <b>{running ? "ИССЛЕДОВАНИЕ ВЫПОЛНЯЕТСЯ" : active ? active.program_status : "ОЖИДАНИЕ"}</b>
                <span>{active ? `${active.work_id} · ${active.work_title}` : "Исследовательские программы ещё не сформированы"}</span>
              </div>
              <div>
                <small>ТЕКУЩАЯ ЗАДАЧА</small>
                <b>{task ? `${task.task_id} · ${task.name}` : "—"}</b>
                <span>{task ? `${task.progress || 0}% · ${task.quality_gate || "NOT_CHECKED"}` : ""}</span>
              </div>
              <div>
                <small>ПО ЦИКЛУ</small>
                <b>{researchDashboard.totals?.research_ready || 0} / {researchDashboard.totals?.works || 0}</b>
                <span>произведений RESEARCH_READY</span>
              </div>
              <button onClick={()=>setWorkspaceView("research")}>Открыть Research Complex →</button>
            </>;
          })()}
        </section>}

        {phase==="ready" && apiError && <section className="asRecoverableError">
          <div>
            <small>RECOVERABLE ANALYSIS ERROR</small>
            <b>Глубокий анализ прерван, данные не потеряны</b>
            <span>{apiError}</span>
          </div>
          <button onClick={startDeepAnalysis}>Продолжить глубокий анализ →</button>
        </section>}

        {phase==="ready" && <section className="asWorkspace">
          <div className="asWorkspaceHead">
            <div>
              <small>ALINA KNOWLEDGE WORKSPACE</small>
              <h2>{projectMeta?.short_code ? `${projectMeta.short_code} — ${title}` : (title || "Новый проект")}</h2>
              <p>{runState?.run_type==="DEEP_ANALYSIS" && runState?.status==="PASS" ? "Глубокий семантический анализ завершён." : "Корпус подготовлен. Research Complex выполняет исследовательские задачи по произведениям и строит evidence-weighted граф."}</p>
            </div>
            <div className="asWorkspaceActions">
              <button onClick={exportProjectReport} disabled={reportBusy}>{reportBusy ? "Формирую отчёт…" : "Экспорт отчёта"}</button>
              <button className="primary" onClick={startDeepAnalysis} disabled={!projectId || phase==="running"}>
                {runState?.run_type==="DEEP_ANALYSIS" && phase==="running" ? "Глубокий анализ идёт…" : "Запустить глубокий анализ →"}
              </button>
            </div>
          </div>

          <div className="asWorkspaceNav">
            <button className={workspaceView==="dashboard"?"active":""} onClick={()=>setWorkspaceView("dashboard")}>Dashboard</button>
            <button className={workspaceView==="knowledge"?"active":""} onClick={()=>setWorkspaceView("knowledge")}>База знаний</button>
            <button className={workspaceView==="research"?"active":""} onClick={()=>setWorkspaceView("research")}>Research Complex</button>
            <button className={workspaceView==="process"?"active":""} onClick={()=>setWorkspaceView("process")}>Процесс / Trace</button>
            <button className={workspaceView==="graph"?"active":""} onClick={()=>setWorkspaceView("graph")}>Graph Lab</button>
            <button className={workspaceView==="sources"?"active":""} onClick={()=>setWorkspaceView("sources")}>Source Center</button>
            <button className={workspaceView==="forecast"?"active":""} onClick={()=>setWorkspaceView("forecast")}>Прогноз</button>
            <button className={workspaceView==="creative"?"active":""} onClick={()=>setWorkspaceView("creative")}>Creative Studio</button>
            <button onClick={()=>setAdminVisible(true)}>Администрирование</button>
          </div>

          {projectState && <div className="asProjectStateStrip">
            <div><small>PROJECT STATE</small><b>v{projectState.schema_version || "1.0"}</b><span>{projectState.status || "—"}</span></div>
            <div><small>SOURCES</small><b>{projectState.source_set?.count || 0}</b><span>Source Set v{projectState.source_set?.version || 0}</span></div>
            <div><small>WORKS</small><b>{projectState.knowledge_base?.works_matched || 0}</b><span>из {projectState.knowledge_base?.works_expected ?? "—"}</span></div>
            <div><small>RESEARCH</small><b>{projectState.research?.totals?.pass_tasks || 0} PASS</b><span>{projectState.research?.totals?.running || 0} running</span></div>
            <div><small>CORPUS VERIFY</small><b>{projectState.corpus_verification?.status || "PENDING"}</b><span>{projectState.corpus_verification?.summary?.publication_year_matches ?? 0}/{projectState.corpus_verification?.summary?.works_expected ?? 0} years matched</span></div>
            <div><small>EVENTS</small><b>{projectEvents.length}</b><span>{projectState.last_event?.event_type || "—"}</span></div>
          </div>}

          <div className="asProjectArchitecture">
            <article><small>PROJECT</small><b>{projectMeta?.short_code || "—"}</b><span>{title}</span></article>
            <article><small>SOURCE SET</small><b>v{projectMeta?.source_set_version || 0}</b><span>{projectMeta?.source_count ?? sourceCount} source(s)</span></article>
            <article><small>FINGERPRINT</small><b>{projectMeta?.source_fingerprint ? projectMeta.source_fingerprint.slice(0,10)+"…" : "—"}</b><span>{projectMeta?.foundation_stale ? "KB stale" : "reusable"}</span></article>
            <article><small>KNOWLEDGE BASE</small><b>v{projectMeta?.kb_version || 0}</b><span>{projectMeta?.active_analysis_profile || projectMeta?.analysis_level || "NONE"}</span></article>
            <article><small>PRODUCTS</small><b>{products.length}</b><span>creative outputs</span></article>
          </div>

          <div className="asBenchmarkPanel">
            <div className="asBenchmarkHead">
              <div>
                <small>ALICE BENCHMARK SEED</small>
                <b>{benchmarkSeed ? "MANUAL VERIFIED BENCHMARK · IMPORTED" : "Ранее выполненный разбор Алисы"}</b>
                <span>{benchmarkSeed
                  ? "Эталон подключён к текущей БЗ отдельно от автоматического run."
                  : "Наш ранее проверенный разбор можно подмешать как seed/benchmark, не выдавая его за текущий Deep Run."}</span>
              </div>
              <button disabled={!projectId || benchmarkBusy} onClick={importAliceBenchmark}>
                {benchmarkBusy ? "Импорт…" : benchmarkSeed ? "Обновить эталон" : "Вставить эталон Алисы"}
              </button>
            </div>
            <div className="asReferenceAnalysis">
              <div>
                <small>REFERENCE ANALYSIS · COMMIT 359c692</small>
                <b>{referenceAnalysis ? "Сто лет тому вперёд · подключено" : "Готовый глубокий разбор «Сто лет тому вперёд»"}</b>
                <span>{referenceAnalysis
                  ? `${referenceAnalysis.chunk_count || 61} chunks · ${referenceAnalysis.maturity || "TRUSTED_ANALYTICAL_FOUNDATION_READY"}`
                  : "Canon, entities, events, relations, temporal/state/causal stores, graph и evidence chunks."}</span>
              </div>
              <button disabled={!projectId || referenceBusy} onClick={importAliceReferenceAnalysis}>
                {referenceBusy ? "Подключаю…" : referenceAnalysis ? "Обновить reference" : "Подключить готовый анализ"}
              </button>
            </div>

            <div className="asBenchmarkMetrics">
              <article><small>КАТАЛОГ</small><b>{benchmarkSeed?.cycle_expected ?? 52}</b><span>произведения</span></article>
              <article><small>БОЛЬШОЙ FB2</small><b>{benchmarkSeed?.source_audit?.matched_works ?? 51}/52</b><span>ручной аудит</span></article>
              <article><small>ОТДЕЛЬНЫЙ PDF</small><b>{benchmarkSeed?.current_project_expected_matches===52 ? "ЕСТЬ" : "ЗВЁЗДНЫЙ ПЁС"}</b><span>ALICE-029</span></article>
              <article><small>DEEP BENCHMARK</small><b>{benchmarkSeed?.historical_deep_benchmark?.clean_chunks ?? 61}</b><span>chunks «Сто лет тому вперёд»</span></article>
            </div>
            {benchmarkSeed && <div className="asBenchmarkNote">
              <span>FOUNDATION:</span>
              <b>{benchmarkSeed.historical_deep_benchmark?.pipeline_metrics?.claims_total ?? 565} claims · {benchmarkSeed.historical_deep_benchmark?.pipeline_metrics?.entities ?? 46} entities · {benchmarkSeed.historical_deep_benchmark?.pipeline_metrics?.events ?? 19} events · {benchmarkSeed.historical_deep_benchmark?.pipeline_metrics?.graph_edges ?? 80} graph edges</b>
            </div>}
          </div>

          <div className="asDeepStatus">
            <div>
              <small>DEEP ANALYSIS ENGINE</small>
              <b>{deepModel?.available ? `LOCAL MODEL READY · ${deepModel.model}` : deepModel?.configured ? `GGUF CONFIGURED · ${deepModel.model}` : "LOCAL MODEL NOT FOUND"}</b>
              <span>{deepModel?.available
                ? `${deepModel.provider} · ${deepModel.detection || "AUTO"} · полный текст будет анализироваться локально chunk за chunk.`
                : deepModel?.needs_package
                  ? "GGUF выбран, но в .venv-alina не найден llama-cpp-python."
                  : "Ollama/GGUF пока не определены backend-ом."}</span>
              {!deepModel?.available && deepModel?.error && <em>DIAGNOSTIC: {deepModel.error}</em>}
              {deepModel?.available && deepModel?.models?.length > 0 && <em>MODELS: {deepModel.models.join(" · ")}</em>}
              {deepModel?.model_path && <em>{deepModel.model_path}</em>}
            </div>
            <div className="asDeepControlBox">
              <label>
                <span>ПРОФИЛЬ АНАЛИЗА</span>
                <select value={analysisProfile} onChange={e=>setAnalysisProfile(e.target.value)}>
                  <option value="CANON_FULL">CANON_FULL — полный канон</option>
                  <option value="CHARACTER_DEEP">CHARACTER_DEEP — персонажи</option>
                  <option value="WORLD_TECH">WORLD_TECH — мир и технологии</option>
                  <option value="COMIC_PREP">COMIC_PREP — подготовка комикса</option>
                  <option value="FILM_PREP">FILM_PREP — подготовка фильма</option>
                </select>
              </label>
              <label>
                <span>ГЛУБИНА</span>
                <select value={analysisDepth} onChange={e=>setAnalysisDepth(e.target.value)}>
                  <option value="FULL">FULL</option>
                  <option value="FOCUSED">FOCUSED</option>
                </select>
              </label>
              <div className="asDeepActions">
                <button onClick={checkDeepModel}>Проверить</button>
                <button onClick={selectLocalGguf}>Выбрать GGUF</button>
                {deepModel?.configured && <button onClick={clearLocalModel}>Сбросить</button>}
              </div>
            </div>
          </div>
          {apiError && <div className="asDeepError">{apiError}</div>}

          <div className="asRunReport">
            <article><small>ИСТОЧНИКИ</small><b>{projectState?.source_set?.count ?? savedSources.length}</b><span>в Source Set проекта</span></article>
            <article><small>ПРОИЗВЕДЕНИЯ</small><b>{benchmarkSeed ? `${benchmarkSeed.current_project_expected_matches} / ${benchmarkSeed.cycle_expected}` : (runState?.metrics?.works ?? "—")}{!benchmarkSeed && runState?.metrics?.works_expected ? ` / ${runState.metrics.works_expected}` : ""}</b><span>{benchmarkSeed ? "BENCHMARK VERIFIED" : (runState?.metrics?.works_review != null ? `review: ${runState.metrics.works_review} · missing: ${runState.metrics.works_missing ?? 0}` : "по каталогу")}</span></article>
            <article><small>СТРУКТУРНЫЕ ОБЪЕКТЫ</small><b>{runState?.metrics?.entities ?? "—"}</b><span>первичный реестр заголовков</span></article>
            <article><small>СОБЫТИЯ</small><b>{runState?.metrics?.events ?? "—"}</b><span>извлечено</span></article>
            <article><small>ПРОТИВОРЕЧИЯ</small><b>{runState?.metrics?.conflicts ?? "—"}</b><span>структурный cross-check</span></article>
            <article><small>REVIEW</small><b>{runState?.metrics?.review ?? "—"}</b><span>на проверку</span></article>
          </div>


          {workspaceView==="dashboard" && <section className="asCommandCenter">
            <div className="asCommandHero">
              <div>
                <small>PROJECT COMMAND CENTER</small>
                <h3>{commandCenter?.project?.code || projectMeta?.short_code || "—"} · {commandCenter?.project?.title || title}</h3>
                <p>Единая оперативная картина проекта: доверие к корпусу, производственный поток, проблемы и следующий шаг.</p>
              </div>
              <div className={`asHealth ${(commandCenter?.health || "REVIEW").toLowerCase()}`}>
                <small>PROJECT HEALTH</small>
                <b>{commandCenter?.health || "REVIEW"}</b>
              </div>
            </div>

            <div className="asCommandNext">
              <div>
                <small>РЕКОМЕНДОВАННОЕ ДЕЙСТВИЕ</small>
                <b>{commandCenter?.next_action?.label || "Обновить состояние проекта"}</b>
              </div>
              <button onClick={()=>openCommandTarget(commandCenter?.next_action?.target || "research")}>Перейти →</button>
            </div>

            <div className="asCommandKpis">
              <article><small>SOURCES</small><b>{commandCenter?.kpis?.sources ?? 0}</b><span>в проекте</span></article>
              <article><small>CORPUS</small><b>{commandCenter?.kpis?.works_matched ?? 0}/{commandCenter?.kpis?.works_expected ?? "—"}</b><span>идентифицировано</span></article>
              <article><small>VERIFIED</small><b>{commandCenter?.kpis?.corpus_verified ?? 0}</b><span>metadata verified</span></article>
              <article><small>RESEARCH READY</small><b>{commandCenter?.kpis?.research_ready ?? 0}/{commandCenter?.kpis?.research_works ?? 0}</b><span>произведений</span></article>
              <article><small>PASS</small><b>{commandCenter?.kpis?.pass_tasks ?? 0}</b><span>research tasks</span></article>
              <article><small>REVIEW / FAIL</small><b>{commandCenter?.kpis?.review_tasks ?? 0} / {commandCenter?.kpis?.failed_tasks ?? 0}</b><span>требуют внимания</span></article>
            </div>

            <div className="asPipelineBoard">
              <div className="asCommandSectionHead"><b>ПРОИЗВОДСТВЕННЫЙ КОНВЕЙЕР</b><span>overview → drill-down</span></div>
              <div className="asPipelineStages">
                {(commandCenter?.pipeline || []).map((p,i)=><button key={p.id} className={(p.status || "").toLowerCase()} onClick={()=>openCommandTarget(p.target)}>
                  <small>{String(i+1).padStart(2,"0")} · {p.id}</small>
                  <b>{p.label}</b>
                  <span>{p.status} · {p.progress ?? 0}%</span>
                  <i><em style={{width:`${Math.max(0,Math.min(100,p.progress || 0))}%`}}/></i>
                </button>)}
              </div>
            </div>

            <div className="asCommandGrid">
              <section className="asAttentionPanel">
                <div className="asCommandSectionHead"><b>ТРЕБУЕТ ВНИМАНИЯ</b><span>{commandCenter?.attention?.length || 0}</span></div>
                {(commandCenter?.attention || []).length===0 ? <div className="asCommandEmpty">Критических блокеров нет.</div> :
                  (commandCenter.attention || []).map((a,i)=><button key={i} className={(a.severity || "MEDIUM").toLowerCase()} onClick={()=>openCommandTarget(a.target)}>
                    <span>{a.severity}</span>
                    <div><b>{a.title}</b><small>{a.reason}</small></div>
                    <em>Открыть →</em>
                  </button>)}
              </section>

              <section className="asCurrentOperation">
                <div className="asCommandSectionHead"><b>ТЕКУЩАЯ ОПЕРАЦИЯ</b><span>{commandCenter?.current_operation?.program_status || "IDLE"}</span></div>
                <div><small>ОБЪЕКТ</small><b>{commandCenter?.current_operation?.work_id || "—"} · {commandCenter?.current_operation?.work_title || "нет активного"}</b></div>
                <div><small>ЗАДАЧА</small><b>{commandCenter?.current_operation?.task_id || "—"} · {commandCenter?.current_operation?.task_name || "—"}</b></div>
                <div><small>СТАТУС</small><b>{commandCenter?.current_operation?.task_status || commandCenter?.current_operation?.run?.status || "—"}</b></div>
                <div><small>RUN</small><b>{commandCenter?.current_operation?.run?.stage || "—"} · {commandCenter?.current_operation?.run?.progress ?? 0}%</b></div>
                {commandCenter?.current_operation?.run?.error && <p>{commandCenter.current_operation.run.error}</p>}
                <button onClick={()=>setWorkspaceView("process")}>Открыть процесс / trace →</button>
              </section>
            </div>

            <div className="asTrustPanel">
              <div className="asCommandSectionHead"><b>TRUST & EVIDENCE</b><span>{commandCenter?.trust?.corpus_verification_status || "PENDING"}</span></div>
              <div>
                <article><small>YEARS VERIFIED</small><b>{commandCenter?.trust?.publication_year_matches ?? 0}/{commandCenter?.trust?.works_expected ?? 0}</b></article>
                <article><small>OFFICIAL FULL TEXT</small><b>{commandCenter?.trust?.official_full_text_verified ?? 0}</b></article>
                <article><small>PUBLISHER EDITIONS</small><b>{commandCenter?.trust?.publisher_editions_verified ?? 0}</b></article>
                <article><small>REPORT</small><b>ALINA_PROJECT_REPORT_V1</b></article>
              </div>
            </div>
          </section>}

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
                          {kbTab==="summary" && kbData.works ? <div className="asKbOverview">
                            <div className="asOverviewHero">
                              <div><small>ИТОГ РАЗБОРА</small><h3>{kbData.works.cycle || title}</h3><p>ALINA завершила первый слой ingest и сохранила структуру корпуса, evidence, первичный graph/world foundation и очередь проверки.</p></div>
                              <strong>{runState?.status || "PASS"}</strong>
                            </div>
                            <div className="asOverviewGrid">
                              <article><small>ИСТОЧНИКИ</small><b>{runState?.metrics?.sources ?? files.length}</b></article>
                              <article><small>ПРОИЗВЕДЕНИЯ</small><b>{kbData.works.matched_count ?? 0}/{kbData.works.expected ?? "—"}</b></article>
                              <article><small>REVIEW WORKS</small><b>{kbData.works.review_count ?? 0}</b></article>
                              <article><small>MISSING</small><b>{kbData.works.missing_count ?? 0}</b></article>
                              <article><small>CLAIMS</small><b>{runState?.metrics?.claims ?? 0}</b></article>
                              <article><small>STRUCTURAL OBJECTS</small><b>{runState?.metrics?.entities ?? 0}</b></article>
                            </div>
                            <div className="asOverviewNext">
                              <b>Следующий слой ALINA</b>
                              <span>ГЛУБОКИЙ АНАЛИЗ: полный текст → персонажи → события → отношения → хронология → технологии → причинность → противоречия → прогноз. Это уже не секундный этап.</span>
                            </div>
                          </div> : kbTab==="works" && kbData.works ? <div className="asWorksResult">
                            <div className="asWorksSummary">
                              <b>{kbData.works.cycle || "Каталог произведений"}</b>
                              <span>Найдено {kbData.works.matched_count ?? 0} из {kbData.works.expected ?? "—"} · review {kbData.works.review_count ?? 0} · не найдено {kbData.works.missing_count ?? 0}</span>
                            </div>
                            <div className="asWorksList">
                              {(kbData.works.matched || []).map(w=><article
                                key={w.work_id}
                                role="button"
                                tabIndex={0}
                                className={selectedCorpusObject?.work_id===w.work_id ? "selected" : ""}
                                onClick={()=>{setSelectedCorpusObject({...w,cycle:kbData.works.cycle,catalog_author:kbData.works.author});setSourceIntel(null)}}
                                onKeyDown={e=>{if(e.key==="Enter"){setSelectedCorpusObject({...w,cycle:kbData.works.cycle,catalog_author:kbData.works.author});setSourceIntel(null)}}}
                              >
                                <span>{w.work_id}</span><b>{w.title}</b><small>{w.publication_year || "—"} · {w.form || "—"}</small><em>MATCHED</em>
                              </article>)}
                              {(kbData.works.review || []).map(w=><article
                                key={w.work_id}
                                role="button"
                                tabIndex={0}
                                className={`review ${selectedCorpusObject?.work_id===w.work_id ? "selected" : ""}`}
                                onClick={()=>{setSelectedCorpusObject({...w,cycle:kbData.works.cycle,catalog_author:kbData.works.author});setSourceIntel(null)}}
                              >
                                <span>{w.work_id}</span><b>{w.title}</b><small>Похоже на: {w.candidate_heading} · {Math.round((w.confidence || 0)*100)}%</small><em>REVIEW</em>
                              </article>)}
                              {(kbData.works.missing || []).map(w=><article
                                key={w.work_id}
                                role="button"
                                tabIndex={0}
                                className={`missing ${selectedCorpusObject?.work_id===w.work_id ? "selected" : ""}`}
                                onClick={()=>{setSelectedCorpusObject({...w,cycle:kbData.works.cycle,catalog_author:kbData.works.author});setSourceIntel(null)}}
                              >
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
                          <small>INSPECTOR · CORPUS OBJECT</small>
                          <h3>{selectedCorpusObject?.title || "Карточка объекта"}</h3>
                          {!selectedCorpusObject ? <p>Выберите произведение или документ в списке.</p> : <>
                            <p>{selectedCorpusObject.object_type || "CORPUS_OBJECT"} · {selectedCorpusObject.work_id || selectedCorpusObject.object_id}</p>
                            <div><span>Дата / год</span><b>{selectedCorpusObject.date || selectedCorpusObject.publication_year || "НЕ УСТАНОВЛЕНО"}</b></div>
                            <div><span>Автор / орган</span><b>{selectedCorpusObject.author || selectedCorpusObject.catalog_author || selectedCorpusObject.issuing_authority || "НЕ УСТАНОВЛЕНО"}</b></div>
                            <div><span>Тип</span><b>{selectedCorpusObject.form || selectedCorpusObject.document_type || selectedCorpusObject.object_type || "—"}</b></div>
                            <div><span>Цикл / набор</span><b>{selectedCorpusObject.cycle || "—"}</b></div>
                            <div><span>Порядок</span><b>{selectedCorpusObject.semantic_order ?? "—"}</b></div>
                            <div><span>Идентификация</span><b>{selectedCorpusObject.status || "—"} · {selectedCorpusObject.confidence!=null ? Math.round(selectedCorpusObject.confidence*100)+"%" : "—"}</b></div>
                            <div><span>Полнота</span><b>{selectedCorpusObject.completeness_status || "COMPLETENESS_NOT_VERIFIED"}</b></div>
                            <div><span>Версия / редакция</span><b>{selectedCorpusObject.version_status || "VERSION_NOT_VERIFIED"}</b></div>
                            <div><span>Авторитетность</span><b>{selectedCorpusObject.authority_status || "AUTHORITY_SOURCE_PENDING"}</b></div>
                            <div><span>Источник корпуса</span><b>{selectedCorpusObject.source_id || selectedCorpusObject.reference_source_file || "—"}</b></div>
                            <div><span>Заголовок в источнике</span><b>{selectedCorpusObject.matched_heading || selectedCorpusObject.candidate_heading || "—"}</b></div>
                            <div><span>Основа каталога</span><b>{selectedCorpusObject.catalog_basis || kbData.works?.catalog_basis || "—"}</b></div>
                            {(selectedCorpusObject.aliases || []).length>0 && <div className="asInspectorWide">
                              <span>Алиасы / варианты названия</span>
                              <b>{selectedCorpusObject.aliases.join(" · ")}</b>
                            </div>}
                            {(selectedCorpusObject.notes || []).length>0 && <div className="asInspectorWide">
                              <span>Примечания</span>
                              <b>{selectedCorpusObject.notes.join(" · ")}</b>
                            </div>}
                            <hr/>
                            <button onClick={()=>simulateSourceIntelligence(selectedCorpusObject.object_id || selectedCorpusObject.work_id)} disabled={sourceIntelBusy}>
                              {sourceIntelBusy ? "OSINT работает…" : "Отправить в OSINT · имитация"}
                            </button>
                            <button onClick={()=>{setWorkspaceView("research");setSelectedResearchWork(selectedCorpusObject.work_id)}}>Открыть исследование</button>
                            <button disabled>Сравнить версии — Corpus Lab</button>
                            <button disabled>OFFICIAL DIRECT — по необходимости</button>
                            {sourceIntel && <div className="asSourceIntelResult">
                              <small>SIMULATED OSINT RESULT</small>
                              <b>{sourceIntel.identification?.title}</b>
                              <span>{sourceIntel.warning}</span>
                              <div className="asSourceIntelKpis">
                                <em>IDENTITY {sourceIntel.identification?.confidence!=null ? Math.round(sourceIntel.identification.confidence*100)+"%" : "—"}</em>
                                <em>{sourceIntel.completeness?.status || "—"}</em>
                                <em>{sourceIntel.version_status || "—"}</em>
                                <em>{sourceIntel.authority_status || "—"}</em>
                              </div>
                              <div className="asSourceIntelQuestions">
                                {(sourceIntel.questions || []).map(q=><div key={q.id}>
                                  <span>{q.id}</span>
                                  <b>{q.question}</b>
                                  <em>{Array.isArray(q.answer) ? (q.answer.join(" · ") || "—") : String(q.answer ?? "—")}</em>
                                  <small>{q.status}</small>
                                </div>)}
                              </div>
                            </div>}
                          </>}
                        </aside>
                      </div>
          </>}

          {workspaceView==="research" && <section className="asResearchComplex">
            <div className="asResearchHead">
              <div>
                <small>WORK-LEVEL RESEARCH FACTORY</small>
                <h3>Исследовательский комплекс произведений</h3>
                <p>Каждое произведение получает до 30 контролируемых задач. Межкнижный Continuity Engine остаётся заблокированным до прохождения R30.</p>
              </div>
              <button onClick={()=>loadResearchDashboard(projectId)}>↻ Обновить</button>
            </div>

            <div className="asResearchKpis">
              <article><small>ПРОИЗВЕДЕНИЙ</small><b>{researchDashboard?.totals?.works ?? 0}</b></article>
              <article><small>RESEARCH READY</small><b>{researchDashboard?.totals?.research_ready ?? 0}</b></article>
              <article><small>BLOCKED</small><b>{researchDashboard?.totals?.blocked ?? 0}</b></article>
              <article><small>PASS TASKS</small><b>{researchDashboard?.totals?.pass_tasks ?? 0}</b></article>
              <article><small>REVIEW</small><b>{researchDashboard?.totals?.review_tasks ?? 0}</b></article>
              <article><small>FAILED</small><b>{researchDashboard?.totals?.failed_tasks ?? 0}</b></article>
            </div>

            <div className="asResearchLayout">
              <aside className="asResearchWorks">
                <div className="asResearchPaneTitle"><b>ПРОИЗВЕДЕНИЯ</b><span>{researchDashboard?.programs?.length || 0}</span></div>
                <div className="asResearchWorkList">
                  {(researchDashboard?.programs || []).map(p=><button
                    key={p.work_id}
                    className={selectedResearchWork===p.work_id?"active":""}
                    onClick={()=>{setSelectedResearchWork(p.work_id);loadResearchGraph(p.work_id)}}
                  >
                    <small>{p.work_id}</small>
                    <b>{p.work_title}</b>
                    <span>{p.program_status} · {p.summary?.completion_pct || 0}%</span>
                  </button>)}
                </div>
              </aside>

              <div className="asResearchTasks">
                {(()=>{
                  const p=(researchDashboard?.programs || []).find(x=>x.work_id===selectedResearchWork);
                  if(!p) return <div className="asResearchEmpty">Research Program ещё не сформирован. Он создаётся автоматически после Foundation.</div>;
                  return <>
                    <div className="asResearchProgramHead">
                      <div><small>{p.work_id}</small><h4>{p.work_title}</h4><span>{p.research_profile} · Source Set v{p.source_set_version}</span></div>
                      <div className="asResearchProgramActions">
                        <em>{p.program_status}</em>
                        <button disabled={researchBusy || p.program_status==="RUNNING"} onClick={()=>runResearchAuto(p.work_id)}>
                          {researchBusy && researchAction==="AUTO" ? "Автомат выполняет…" : "Автозапуск доступного"}
                        </button>
                        <button disabled={researchBusy || p.program_status==="RUNNING"} onClick={()=>runNextResearchTask(p.work_id)}>
                          {researchBusy && researchAction==="NEXT" ? "Выполняю…" : "Следующая задача →"}
                        </button>
                      </div>
                    </div>
                    <div className="asResearchProgress">
                      <div><i style={{width:`${p.summary?.completion_pct || 0}%`}}></i></div>
                      <span>{p.summary?.completion_pct || 0}%</span>
                    </div>
                    <div className="asResearchRunSummary">
                      <span>RUN HISTORY: {(p.execution_history || []).length}</span>
                      <span>PASS: {p.summary?.pass || 0}</span>
                      <span>REVIEW: {p.summary?.review || 0}</span>
                      <span>BLOCKED: {p.summary?.blocked || 0}</span>
                      <span>FAILED: {p.summary?.failed || 0}</span>
                    </div>
                    <div className="asTaskGrid">
                      {(p.tasks || []).map(t=><article key={t.task_id} className={String(t.status || "").toLowerCase()}>
                        <div className="asTaskTop"><small>{t.task_id}</small><em>{t.status}</em></div>
                        <b>{t.name}</b>
                        {t.research_question && <p className="asTaskQuestion">{t.research_question}</p>}
                        <div className="asTaskBar"><i style={{width:`${t.progress || 0}%`}}></i></div>
                        <span>{t.quality_gate || "NOT_CHECKED"}</span>
                        {(t.depends_on || []).length>0 && <small className="asTaskDeps">depends: {t.depends_on.join(" · ")}</small>}
                        {(t.blockers || []).length>0 && <strong>{t.blockers.join(" · ")}</strong>}
                        <button
                          disabled={researchBusy || ["PASS","REUSED","RUNNING","BLOCKED"].includes(t.status)}
                          onClick={()=>runResearchTask(p.work_id,t.task_id)}
                        >
                          {researchBusy && researchAction===t.task_id ? "Выполняю…" : t.status==="RUNNING" ? "Выполняется…" : ["PASS","REUSED"].includes(t.status) ? "Готово" : t.status==="BLOCKED" ? "Заблокировано" : "Запустить"}
                        </button>
                      </article>)}
                    </div>
                  </>;
                })()}
              </div>
            </div>

            {researchGraph && <div className="asResearchGraphSummary">
              <div className="asResearchGraphHead">
                <div>
                  <small>EVIDENCE-WEIGHTED GRAPH</small>
                  <b>{selectedResearchWork}</b>
                  <span>Узлы и связи формируются из work-scoped анализа с весами evidence/confidence.</span>
                </div>
                <div className="asResearchGraphKpis">
                  <article><small>NODES</small><b>{researchGraph.node_count || 0}</b></article>
                  <article><small>EDGES</small><b>{researchGraph.edge_count || 0}</b></article>
                </div>
              </div>
              <div className="asResearchTopNodes">
                {(researchGraph.nodes || []).slice().sort((a,b)=>(b.weight||0)-(a.weight||0)).slice(0,12).map(n=>
                  <span key={n.id}><b>{n.label}</b><em>{n.type} · w={Number(n.weight||0).toFixed(2)}</em></span>
                )}
              </div>
            </div>}

            <div className="asContinuityGate">
              <div>
                <small>CYCLE CONTINUITY ENGINE</small>
                <b>{researchDashboard?.continuity?.program_status || "BLOCKED"}</b>
                <span>{researchDashboard?.continuity?.reason || "Ожидает готовности исследовательских программ произведений."}</span>
              </div>
              <div>
                <small>WORKS READY</small>
                <b>{researchDashboard?.continuity?.work_programs_ready || 0} / {researchDashboard?.continuity?.work_programs_total || 0}</b>
              </div>
              <div>
                <small>CYCLE TASKS</small>
                <b>{researchDashboard?.continuity?.summary?.total || 30}</b>
              </div>
            </div>
          </section>}

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
              <article><small>TEXT ITEM</small><b>{runState?.current_total ? `${runState.current_item}/${runState.current_total}` : "—"}</b></article>
            </div>
            <div className="asSequenceTrace">
              {[
                ["PROJECT_FLOW","PROJECT → SOURCES → FOUNDATION"],
                ["ANALYSIS_FLOW","FOUNDATION → DEEP → KB"],
                ["CREATIVE_FLOW","KB → PRODUCT → PROMPT/RAG"],
                ["GITHUB_FLOW","UI/API → SAFE TRACE → GITHUB"]
              ].map(([id,label])=>{
                const e=sequenceState[id];
                const status=id==="GITHUB_FLOW" ? githubDebugStatus : (e?.status || "WAITING");
                const step=id==="GITHUB_FLOW" ? (githubDebugStatus==="PUSHED"?"SAFE TRACE PUSHED":githubDebugStatus==="PUBLISHING"?"PUBLISHING IN BACKGROUND":githubDebugStatus==="WARN"?"GITHUB WARNING":"WAITING FOR TRACE") : (e?.step || "WAITING");
                return <article key={id} className={String(status).toLowerCase()}>
                  <small>{id}</small>
                  <b>{label}</b>
                  <span>{step}</span>
                  <em>{status}</em>
                </article>;
              })}
            </div>

            <div className="asProcessLayout">
              <div className="asStageBoard">
                {studyPipeline.map(([n,name,desc],i)=><article key={name} className={i===0?"ready":""}>
                  <i>{i===0?"●":"○"}</i><div><small>{n}</small><b>{name}</b><span>{desc}</span></div><em>{i===0?"READY":"WAIT"}</em>
                </article>)}
              </div>
              <div className="asTraceLog">
                <div className="asTraceHead"><b>TRACE LOG</b><span>{traceLevel}</span></div>
                <pre>{[
                  ...(runState?.trace || []).map(e=>({timestamp:e.timestamp,kind:e.stage,status:e.status,text:`${e.current && e.total ? `[${e.current}/${e.total}] ` : ""}${e.action}`})),
                  ...uiTrace.map(e=>({timestamp:e.timestamp,kind:e.event_type,status:e.status || "INFO",text:e.button || e.action_id || e.step || e.endpoint || ""}))
                ].sort((a,b)=>String(a.timestamp).localeCompare(String(b.timestamp))).slice(-300)
                  .map(e=>`[${e.timestamp}] [${e.kind}] [${e.status}] ${e.text}`).join("\n") || `[SYSTEM] Project opened in PRIVATE LOCAL MODE
[TRACE] UI/API tracing enabled
[GITHUB] Safe debug publishing enabled`}</pre>
              </div>
            </div>
            <div className="asGithubTrace">
              <div>
                <small>GITHUB SAFE EXPORT</small>
                <b>{!adminSettings.github_debug_trace ? "DISABLED" : githubDebugStatus==="PUSHED" ? "PUSHED" : githubDebugStatus==="PUBLISHING" ? "PUBLISHING" : githubDebugStatus==="WARN" ? "WARNING" : githubDebugStatus==="NO_CHANGES" ? "SYNCED" : "WAITING"}</b>
              </div>
              <span>{adminSettings.github_debug_trace ? "DEBUG MODE: safe trace публикуется в GitHub." : "GitHub trace отключён в Администрировании. Локальная трассировка работает отдельно."} Текст книг, содержимое файлов и имена источников не публикуются.</span>
            </div>
            <div className="asTraceSchema">
              <b>Каждая запись трассы:</b>
              <code>timestamp · event_type · project_code · run_id · button/API · sequence.step · status · duration_ms · github</code>
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

          {workspaceView==="creative" && <section className="asCreativeStudio">
            <div className="asCreativeHead">
              <div>
                <small>CREATIVE STUDIO</small>
                <h3>Продукты поверх одной базы знаний</h3>
                <p>Источники и канон не перечитываются заново. Меняется только творческий профиль и зависимые слои.</p>
              </div>
              <span>KB v{projectMeta?.kb_version || 0}</span>
            </div>

            <div className="asCreativeModes">
              {[
                ["BOOK","Книга / продолжение"],
                ["COMIC","Комикс"],
                ["VISUAL_NOVEL","Visual Novel"],
                ["SHORT_VIDEO","Короткое видео"],
                ["FILM","Фильм / серия"],
                ["GAME_SCENARIO","Игровой сценарий"]
              ].map(([id,label])=><button key={id} className={creativeType===id?"active":""} onClick={()=>setCreativeType(id)}>{label}</button>)}
            </div>

            <div className="asCreativeCreate">
              <div>
                <small>НОВЫЙ ПРОДУКТ</small>
                <input value={creativeTitle} onChange={e=>setCreativeTitle(e.target.value)} placeholder={creativeType==="COMIC"?"Например: Комикс — Сто лет тому вперёд":"Название продукта"}/>
              </div>
              <button disabled={!creativeTitle.trim() || creativeBusy} onClick={createCreativeProduct}>
                {creativeBusy ? "Создаю…" : "Создать продукт →"}
              </button>
            </div>

            <div className="asCreativePipeline">
              <span>CANON KB</span><i>→</i><span>AUTHOR INTENT</span><i>→</i><span>STORY</span><i>→</i><span>SCENES</span><i>→</i>
              <span>VISUAL BIBLE</span><i>→</i><span>PROMPT PACK</span><i>→</i><span>RAG</span><i>→</i><span>GENERATION</span>
            </div>

            <div className="asProductList">
              {products.length===0 ? <div className="asNoProducts">Творческих продуктов пока нет.</div> :
                products.map(p=><article key={p.product_id}>
                  <div><small>{p.product_id} · {p.type}</small><b>{p.title}</b><span>{p.profile} · source KB v{p.source_kb_version}</span></div>
                  <em>{p.status}</em>
                </article>)}
            </div>

            {creativeType==="COMIC" && <div className="asComicFactory">
              <small>COMIC FACTORY</small>
              <b>SCENE → PANELS → CAMERA → CHARACTER STATE → CONTINUITY → PROMPT → RAG → IMAGE</b>
              <p>Для каждого кадра будут храниться поза, взгляд, эмоция, действие, взаимодействие, костюм, props, локация, камера, свет, continuity, prompt и ссылки на RAG-контекст.</p>
            </div>}
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

      {deleteModal && <div className="asModalBackdrop" onMouseDown={e=>{if(e.target===e.currentTarget && !deleteBusy)setDeleteModal(null)}}>
        <section className="asDeleteModal" role="dialog" aria-modal="true" aria-label="Подтверждение удаления">
          <div className="asDeleteIcon">⌫</div>
          <small>ALINA · DELETE CONFIRMATION</small>

          {deleteModal.type==="file" && <>
            <h3>Удалить файл из нового проекта?</h3>
            <p>Файл будет убран только из текущего списка загрузки. Исходный файл на компьютере не удаляется.</p>
            <div className="asDeleteTarget">
              <b>{deleteModal.file.name}</b>
              <span>{(deleteModal.file.size/1024/1024).toFixed(2)} MB · локальный файл</span>
            </div>
          </>}

          {deleteModal.type==="run" && <>
            <h3>Удалить эту запись истории?</h3>
            <p>Будет удалён только выбранный run. База знаний и остальные запуски проекта останутся.</p>
            <div className="asDeleteTarget">
              <b>{deleteModal.run.run_id}</b>
              <span>{deleteModal.run.status} · {deleteModal.run.progress ?? 0}% · works {deleteModal.run.metrics?.works ?? "—"}/{deleteModal.run.metrics?.works_expected ?? "—"}</span>
            </div>
          </>}

          {deleteModal.type==="project" && <>
            <h3>Удалить проект целиком?</h3>
            <p>Это удалит локальный проект, его загруженные копии книг, базу знаний, граф, review queue и историю запусков.</p>
            <div className="asDeleteTarget danger">
              <b>{deleteModal.project.title}</b>
              <span>{deleteModal.project.run_count || 0} запуск(ов) · {deleteModal.project.project_id}</span>
            </div>
            <div className="asDeleteWarning">Исходные книги вне папки ALINA на вашем компьютере не удаляются.</div>
          </>}

          <div className="asModalActions">
            <button className="secondary" disabled={deleteBusy} onClick={()=>setDeleteModal(null)}>Отмена</button>
            <button className="danger" disabled={deleteBusy} onClick={()=>{
              if(deleteModal.type==="file") performRemoveFile(deleteModal.key);
              if(deleteModal.type==="run") performDeleteRun(deleteModal.project.project_id,deleteModal.run.run_id);
              if(deleteModal.type==="project") performDeleteProject(deleteModal.project);
            }}>{deleteBusy ? "Удаление…" : deleteModal.type==="project" ? "Удалить проект" : "Удалить"}</button>
          </div>
        </section>
      </div>}
    </div>
  );
}
