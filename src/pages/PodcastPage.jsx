import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const bars = [28,46,68,38,72,52,84,36,58,74,48,88,42,66,54,78,32,62,44,80,50,70,36,60];

const demoScript = `Добро пожаловать в BOOK-CRAFT. Сегодня одна идея превращается в целую контентную историю: письмо, подкаст, видео-аватар, изображения и длинный материал. Вместо пяти разрозненных инструментов — единый narrative workflow и общий контекст проекта.`;

export default function PodcastPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [text, setText] = useState(demoMode ? demoScript : "");
  const [format, setFormat] = useState(demoMode ? "История" : "Монолог");
  const [voice, setVoice] = useState(demoMode ? "Тёплый ведущий" : "Тёплый ведущий");
  const [generated, setGenerated] = useState(demoMode);
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
      status={demoMode ? "DZ PRO · SCREENSHOT DEMO" : "UI DEMO · TTS NEXT"}
    >
      <div className="moduleHero moduleHero--podcast">
        <div><small>SCRIPT</small><b>Текст или тема</b></div>
        <span>→</span>
        <div><small>VOICE</small><b>{voice}</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Audio render</b></div>
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
            <SpectralAction variant="primary" onClick={createDemo}>✦ Подготовить аудио DEMO</SpectralAction>
          </div>

          {demoMode && (
            <div className="demoEvidence">
              <small>SCREENSHOT STATE</small>
              <b>Сценарий → голос → waveform → play-state</b>
              <span>Визуальный TTS-пайплайн готов к подключению реального аудио API.</span>
            </div>
          )}
        </div>

        <div className={`podcastConsole ${generated ? "isReady" : ""}`}>
          <div className="podcastConsole__cover"><span>◉</span><small>{format}</small></div>
          <div className="podcastConsole__meta">
            <small>BOOK-CRAFT PODCAST · 02:18</small>
            <h3>{generated ? "Истории, которые звучат" : "Аудио ещё не подготовлено"}</h3>
            <p>{generated ? `${voice} · TTS-ready pipeline · DEMO` : "Добавьте сценарий и запустите подготовку."}</p>
          </div>
          <div className="waveConsole" aria-hidden="true">
            {bars.map((height, i) => <i key={i} style={{height:`${generated ? height : 18}%`}} />)}
          </div>
          <button className="audioPlayButton" type="button" disabled={!generated} onClick={() => setPlaying((v) => !v)}>
            {playing ? "❚❚ Пауза DEMO" : "▶ Прослушать DEMO"}
          </button>
        </div>
      </div>
    </WorkspacePage>
  );
}
