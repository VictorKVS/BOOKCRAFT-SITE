import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const voices = [
  {id:"A", name:"Warm Presenter", note:"мягкий / доверительный"},
  {id:"B", name:"Neutral Studio", note:"спокойный / универсальный"},
  {id:"C", name:"Dynamic Host", note:"энергичный / промо"},
];

const avatars = [
  {id:"01", name:"Editorial"},
  {id:"02", name:"Studio One"},
  {id:"03", name:"Tech Host"},
  {id:"04", name:"Creator"},
];

const demoScript = "Одна идея. Пять форматов. BOOK-CRAFT помогает превратить замысел в связанную историю — от текста до видео.";

export default function VideoAvatarPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [loaded, setLoaded] = useState(demoMode);
  const [catalogPhase, setCatalogPhase] = useState(demoMode ? "ready" : "idle");
  const [jobPhase, setJobPhase] = useState(demoMode ? "ready" : "idle");
  const [voice, setVoice] = useState(demoMode ? "Warm Presenter" : "");
  const [avatar, setAvatar] = useState(demoMode ? "Editorial" : "");
  const [script, setScript] = useState(demoMode ? demoScript : "");

  const canPrepare = loaded && voice && avatar && script.trim() && jobPhase !== "processing";

  function loadCatalog() {
    if (catalogPhase === "processing") return;

    setLoaded(false);
    setCatalogPhase("processing");
    setJobPhase("idle");

    window.setTimeout(() => {
      setLoaded(true);
      setCatalogPhase("ready");

      if (!voice) setVoice("Warm Presenter");
      if (!avatar) setAvatar("Editorial");
    }, 1300);
  }

  function prepareJob() {
    if (!canPrepare) return;

    setJobPhase("processing");

    window.setTimeout(() => {
      setJobPhase("ready");
    }, 1800);
  }

  function reset() {
    setLoaded(false);
    setCatalogPhase("idle");
    setJobPhase("idle");
    setVoice("");
    setAvatar("");
    setScript("");
  }

  function chooseAvatar(name) {
    setAvatar(name);
    setJobPhase("idle");
  }

  function chooseVoice(name) {
    setVoice(name);
    setJobPhase("idle");
  }

  return (
    <WorkspacePage
      eyebrow="✦ EXTERNAL API"
      title="Видео-Аватар"
      description="Интерфейс под внешний avatar API: каталог голосов и персонажей, сценарий и подготовка video job."
      status={demoMode ? "DZ PRO · INTERACTIVE API DEMO" : "API DEMO · CONNECTOR NEXT"}
    >
      <div className="moduleHero moduleHero--avatar">
        <div><small>EXTERNAL SERVICE</small><b>HeyGen / compatible API</b></div>
        <span>→</span>
        <div><small>CATALOG</small><b>Voice + Avatar</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Video job contract</b></div>
      </div>

      <div className="formActions formActions--top">
        <SpectralAction variant="primary" onClick={loadCatalog}>
          {catalogPhase === "processing" ? "◈ Загружаю каталог…" : loaded ? "◈ Обновить каталог DEMO" : "◈ Загрузить каталог"}
        </SpectralAction>
        {loaded && <button className="secondaryButton" type="button" onClick={reset}>Сбросить</button>}
      </div>

      <div className={`apiProofBanner ${catalogPhase === "processing" ? "isProcessing" : ""}`}>
        <span>API CONTRACT</span>
        <b>{catalogPhase === "processing" ? "GET voices + GET avatars…" : loaded ? "GET voices + GET avatars ✓" : "WAITING REQUEST"}</b>
        <small>Интерактивное API DEMO. Реальный provider key подключается отдельно и не хранится во frontend.</small>
      </div>

      <div className="avatarStudioGrid">
        <div className="avatarCatalogPanel">
          <div className="panelTitleRow"><h3>Аватары</h3><span className="dataBadge">{catalogPhase === "processing" ? "LOADING" : "API DEMO"}</span></div>
          <div className="avatarChoiceGrid avatarChoiceGrid--visual">
            {loaded ? avatars.map((item) => (
              <button key={item.id} type="button" className={avatar === item.name ? "selected" : ""} onClick={() => chooseAvatar(item.name)}>
                <span className="avatarOrb">◎</span><small>AVATAR {item.id}</small><b>{item.name}</b>
              </button>
            )) : (
              <div className="catalogLoading">
                <i /><i /><i /><i />
                <b>{catalogPhase === "processing" ? "Получаю каталог аватаров…" : "API AVATARS"}</b>
              </div>
            )}
          </div>
        </div>

        <div className="voiceCatalogPanel">
          <div className="panelTitleRow"><h3>Голоса</h3><span className="dataBadge">{catalogPhase === "processing" ? "LOADING" : "API DEMO"}</span></div>
          <div className="selectableList selectableList--voices">
            {loaded ? voices.map((item) => (
              <button key={item.id} type="button" className={voice === item.name ? "selected" : ""} onClick={() => chooseVoice(item.name)}>
                <small>VOICE {item.id}</small><b>{item.name}</b><span>{item.note}</span>
              </button>
            )) : (
              <div className="catalogLoading catalogLoading--voice"><i /><i /><i /><b>{catalogPhase === "processing" ? "Получаю голоса…" : "API VOICES"}</b></div>
            )}
          </div>
        </div>
      </div>

      <label className="field avatarScript">
        <span>Сценарий ролика</span>
        <textarea rows="5" value={script} onChange={(e) => {setScript(e.target.value);setJobPhase("idle");}} placeholder="Введите текст, который должен произнести аватар..." />
      </label>

      <div className={`videoJobBar ${canPrepare ? "isReady" : ""} ${jobPhase === "processing" ? "isProcessing" : ""}`}>
        <div>
          <small>{jobPhase === "processing" ? "VIDEO JOB" : "SELECTION"}</small>
          <b>{jobPhase === "processing" ? "avatar → voice → render request…" : `${avatar || "Аватар не выбран"} + ${voice || "голос не выбран"}`}</b>
        </div>

        <button type="button" disabled={!canPrepare} onClick={prepareJob}>
          {jobPhase === "processing" ? "RENDERING DEMO…" : jobPhase === "ready" ? "VIDEO JOB READY ✓" : "Подготовить video job →"}
        </button>
      </div>
    </WorkspacePage>
  );
}
