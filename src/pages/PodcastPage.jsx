import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function PodcastPage() {
  const [text, setText] = useState("");
  const [generated, setGenerated] = useState(false);
  const [playing, setPlaying] = useState(false);

  function createDemo() {
    setGenerated(true);
    setPlaying(false);
  }

  return (
    <WorkspacePage
      eyebrow="✦ PODCAST"
      title="Подкаст"
      description="Черновой сценарий потока: текст → подготовка → аудио-слот. Реальный TTS подключим после фиксации каркаса."
      status="UI DEMO"
    >
      <label className="field">
        <span>Тема или сценарий</span>
        <textarea
          rows="7"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Введите тему или текст..."
        />
      </label>

      <div className="formActions">
        <SpectralAction variant="primary" onClick={createDemo}>Подготовить DEMO</SpectralAction>
        {generated && (
          <button className="secondaryButton" type="button" onClick={() => setPlaying((v) => !v)}>
            {playing ? "Пауза DEMO" : "▶ Проверить play-state"}
          </button>
        )}
      </div>

      <div className={`audioSkeleton ${generated ? "isReady" : ""}`}>
        <div className="audioSkeleton__icon">{playing ? "❚❚" : "▶"}</div>
        <div className="audioSkeleton__wave" aria-hidden="true">
          {Array.from({length: 18}).map((_, i) => <i key={i} />)}
        </div>
        <div>
          <b>{generated ? "AUDIO SLOT READY" : "AUDIO SLOT"}</b>
          <span>{generated ? "DEMO state · TTS API not connected" : "Сначала подготовьте сценарий"}</span>
        </div>
      </div>
    </WorkspacePage>
  );
}
