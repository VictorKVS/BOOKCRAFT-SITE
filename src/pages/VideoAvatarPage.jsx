import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const voices = [
  {id:"A", name:"Neutral Studio", note:"спокойный / универсальный"},
  {id:"B", name:"Warm Presenter", note:"мягкий / доверительный"},
  {id:"C", name:"Dynamic Host", note:"энергичный / промо"},
];
const avatars = [
  {id:"01", name:"Studio One"},
  {id:"02", name:"Editorial"},
  {id:"03", name:"Tech Host"},
  {id:"04", name:"Creator"},
];

export default function VideoAvatarPage() {
  const [loaded, setLoaded] = useState(false);
  const [voice, setVoice] = useState("");
  const [avatar, setAvatar] = useState("");
  const [script, setScript] = useState("");
  const [previewReady, setPreviewReady] = useState(false);

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
      description="Интерфейс под внешний avatar API: загружаем каталог, выбираем голос и персонажа, добавляем сценарий и готовим видео-задачу."
      status="API DEMO · CONNECTOR NEXT"
    >
      <div className="moduleHero moduleHero--avatar">
        <div><small>CATALOG</small><b>Voice + Avatar</b></div>
        <span>→</span>
        <div><small>SCRIPT</small><b>Текст ролика</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Video job</b></div>
      </div>

      <div className="formActions formActions--top">
        <SpectralAction variant="primary" onClick={() => setLoaded(true)}>Загрузить DEMO каталог</SpectralAction>
        {loaded && <button className="secondaryButton" type="button" onClick={reset}>Сбросить</button>}
      </div>

      <div className="avatarStudioGrid">
        <div className="avatarCatalogPanel">
          <div className="panelTitleRow"><h3>Аватары</h3><span className="dataBadge">DEMO</span></div>
          <div className="avatarChoiceGrid avatarChoiceGrid--visual">
            {loaded ? avatars.map((item) => (
              <button key={item.id} type="button" className={avatar === item.name ? "selected" : ""} onClick={() => {setAvatar(item.name);setPreviewReady(false);}}>
                <span className="avatarOrb">◎</span><small>AVATAR {item.id}</small><b>{item.name}</b>
              </button>
            )) : <div className="resultPlaceholder">API AVATARS</div>}
          </div>
        </div>

        <div className="voiceCatalogPanel">
          <div className="panelTitleRow"><h3>Голоса</h3><span className="dataBadge">DEMO</span></div>
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
          {previewReady ? "DEMO JOB READY ✓" : "Подготовить DEMO video job →"}
        </button>
      </div>
    </WorkspacePage>
  );
}
