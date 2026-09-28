import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const voices = ["Voice A · neutral", "Voice B · warm", "Voice C · presenter"];
const avatars = ["Avatar 01", "Avatar 02", "Avatar 03", "Avatar 04"];

export default function VideoAvatarPage() {
  const [loaded, setLoaded] = useState(false);
  const [voice, setVoice] = useState("");
  const [avatar, setAvatar] = useState("");

  return (
    <WorkspacePage
      eyebrow="✦ EXTERNAL API"
      title="Видео-Аватар"
      description="Контракт интерфейса для внешнего API: загрузка голосов и аватаров, выбор пары, затем будущая генерация."
      status="API DEMO"
    >
      <div className="formActions">
        <SpectralAction variant="primary" onClick={() => setLoaded(true)}>
          Показать DEMO каталог
        </SpectralAction>
        {loaded && (
          <button className="secondaryButton" type="button" onClick={() => { setLoaded(false); setVoice(""); setAvatar(""); }}>
            Сбросить
          </button>
        )}
      </div>

      <div className="splitList">
        <div>
          <div className="panelTitleRow">
            <h3>Голоса</h3>
            <span className="dataBadge">DEMO</span>
          </div>
          <div className="selectableList">
            {loaded ? voices.map((item) => (
              <button
                key={item}
                type="button"
                className={voice === item ? "selected" : ""}
                onClick={() => setVoice(item)}
              >
                {item}
              </button>
            )) : <div className="resultPlaceholder">API VOICES</div>}
          </div>
        </div>

        <div>
          <div className="panelTitleRow">
            <h3>Аватары</h3>
            <span className="dataBadge">DEMO</span>
          </div>
          <div className="avatarChoiceGrid">
            {loaded ? avatars.map((item) => (
              <button
                key={item}
                type="button"
                className={avatar === item ? "selected" : ""}
                onClick={() => setAvatar(item)}
              >
                <span>◎</span>
                <b>{item}</b>
              </button>
            )) : <div className="resultPlaceholder">API AVATARS</div>}
          </div>
        </div>
      </div>

      <div className={`selectionSummary ${voice && avatar ? "isReady" : ""}`}>
        <small>SELECTION</small>
        <b>{voice && avatar ? `${avatar} + ${voice}` : "Выберите голос и аватар"}</b>
        <span>{voice && avatar ? "UI contract ready · real API not connected" : "После подключения API здесь появится готовая пара."}</span>
      </div>
    </WorkspacePage>
  );
}
