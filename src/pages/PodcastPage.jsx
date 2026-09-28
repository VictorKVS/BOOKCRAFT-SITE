import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const bars = [28,46,68,38,72,52,84,36,58,74,48,88,42,66,54,78,32,62,44,80,50,70,36,60];

export default function PodcastPage() {
  const [text, setText] = useState("");
  const [format, setFormat] = useState("Монолог");
  const [voice, setVoice] = useState("Тёплый ведущий");
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
      description="Сценарий превращается в аудио-пайплайн: формат, голос, подготовка текста и будущий TTS-рендер."
      status="UI DEMO · TTS NEXT"
    >
      <div className="moduleHero moduleHero--podcast">
        <div><small>SCRIPT</small><b>Текст или тема</b></div>
        <span>→</span>
        <div><small>VOICE</small><b>{voice}</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Аудио</b></div>
      </div>

      <div className="editorGrid">
        <div className="editorColumn">
          <label className="field">
            <span>Тема или сценарий</span>
            <textarea rows="9" value={text} onChange={(e) => setText(e.target.value)} placeholder="Введите тему или текст выпуска..." />
          </label>

          <div className="fieldPair">
            <label className="field">
              <span>Формат</span>
              <select value={format} onChange={(e) => setFormat(e.target.value)}>
                <option>Монолог</option>
                <option>Интервью</option>
                <option>Новости</option>
                <option>История</option>
              </select>
            </label>
            <label className="field">
              <span>Голос</span>
              <select value={voice} onChange={(e) => setVoice(e.target.value)}>
                <option>Тёплый ведущий</option>
                <option>Нейтральный диктор</option>
                <option>Энергичный ведущий</option>
              </select>
            </label>
          </div>

          <div className="formActions">
            <SpectralAction variant="primary" onClick={createDemo}>Подготовить DEMO</SpectralAction>
          </div>
        </div>

        <div className={`podcastConsole ${generated ? "isReady" : ""}`}>
          <div className="podcastConsole__cover"><span>◉</span><small>{format}</small></div>
          <div className="podcastConsole__meta">
            <small>BOOK-CRAFT PODCAST</small>
            <h3>{generated ? "Черновой выпуск готов" : "Аудио ещё не подготовлено"}</h3>
            <p>{generated ? "TTS API ещё не подключён — показано рабочее состояние интерфейса." : "Добавьте сценарий и запустите подготовку."}</p>
          </div>
          <div className="waveConsole" aria-hidden="true">
            {bars.map((height, i) => <i key={i} style={{height:`${generated ? height : 18}%`}} />)}
          </div>
          <button className="audioPlayButton" type="button" disabled={!generated} onClick={() => setPlaying((v) => !v)}>
            {playing ? "❚❚ Пауза DEMO" : "▶ Play-state"}
          </button>
        </div>
      </div>
    </WorkspacePage>
  );
}
