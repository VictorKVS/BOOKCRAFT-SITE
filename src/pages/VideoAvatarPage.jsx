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
  const [voice, setVoice] = useState(demoMode ? "Warm Presenter" : "");
  const [avatar, setAvatar] = useState(demoMode ? "Editorial" : "");
  const [script, setScript] = useState(demoMode ? demoScript : "");
  const [previewReady, setPreviewReady] = useState(demoMode);

  const canPrepare = loaded && voice && avatar && script.trim();

  function reset() {
    setLoaded(false);
    setVoice("");
    setAvatar("");
    setScript("");
    setPreviewReady(false);
  }

  return (
    <WorkspacePage
      eyebrow="✦ EXTERNAL API"
      title="Видео-Аватар"
      description="Интерфейс под внешний avatar API: каталог голосов и персонажей, сценарий и подготовка video job."
      status={demoMode ? "DZ PRO · API SCREENSHOT" : "API DEMO · CONNECTOR NEXT"}
    >
      <div className="moduleHero moduleHero--avatar">
        <div><small>EXTERNAL SERVICE</small><b>HeyGen / compatible API</b></div>
        <span>→</span>
        <div><small>CATALOG</small><b>Voice + Avatar</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Video job contract</b></div>
      </div>

      <div className="formActions formActions--top">
        <SpectralAction variant="primary" onClick={() => setLoaded(true)}>◈ Загрузить каталог</SpectralAction>
        {loaded && <button className="secondaryButton" type="button" onClick={reset}>Сбросить</button>}
      </div>

      {demoMode && (
        <div className="apiProofBanner">
          <span>API CONTRACT</span>
          <b>GET voices + GET avatars</b>
          <small>Screenshot DEMO. Реальный provider key подключается отдельно и не хранится во frontend.</small>
        </div>
      )}

      <div className="avatarStudioGrid">
        <div className="avatarCatalogPanel">
          <div className="panelTitleRow"><h3>Аватары</h3><span className="dataBadge">{demoMode ? "API DEMO" : "DEMO"}</span></div>
          <div className="avatarChoiceGrid avatarChoiceGrid--visual">
            {loaded ? avatars.map((item) => (
              <button key={item.id} type="button" className={avatar === item.name ? "selected" : ""} onClick={() => {setAvatar(item.name);setPreviewReady(false);}}>
                <span className="avatarOrb">◎</span><small>AVATAR {item.id}</small><b>{item.name}</b>
              </button>
            )) : <div className="resultPlaceholder">API AVATARS</div>}
          </div>
        </div>

        <div className="voiceCatalogPanel">
          <div className="panelTitleRow"><h3>Голоса</h3><span className="dataBadge">{demoMode ? "API DEMO" : "DEMO"}</span></div>
          <div className="selectableList selectableList--voices">
            {loaded ? voices.map((item) => (
              <button key={item.id} type="button" className={voice === item.name ? "selected" : ""} onClick={() => {setVoice(item.name);setPreviewReady(false);}}>
                <small>VOICE {item.id}</small><b>{item.name}</b><span>{item.note}</span>
              </button>
            )) : <div className="resultPlaceholder">API VOICES</div>}
          </div>
        </div>
      </div>

      <label className="field avatarScript">
        <span>Сценарий ролика</span>
        <textarea rows="5" value={script} onChange={(e) => {setScript(e.target.value);setPreviewReady(false);}} placeholder="Введите текст, который должен произнести аватар..." />
      </label>

      <div className={`videoJobBar ${canPrepare ? "isReady" : ""}`}>
        <div><small>SELECTION</small><b>{avatar || "Аватар не выбран"} + {voice || "голос не выбран"}</b></div>
        <button type="button" disabled={!canPrepare} onClick={() => setPreviewReady(true)}>
          {previewReady ? "VIDEO JOB READY ✓" : "Подготовить video job →"}
        </button>
      </div>
    </WorkspacePage>
  );
}
