import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const bars = [28,46,68,38,72,52,84,36,58,74,48,88,42,66,54,78,32,62,44,80,50,70,36,60];
const demoScript = "Добро пожаловать в BOOK-CRAFT. Сегодня одна идея превращается в целую контентную историю: письмо, подкаст, видео-аватар, изображения и длинный материал. Вместо пяти разрозненных инструментов — единый narrative workflow и общий контекст проекта.";

export default function PodcastPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [text, setText] = useState(demoMode ? demoScript : "");
  const [format, setFormat] = useState(demoMode ? "История" : "Монолог");
  const [voice, setVoice] = useState("Тёплый ведущий");
  const [generated, setGenerated] = useState(demoMode);
  const [phase, setPhase] = useState(demoMode ? "ready" : "idle");
  const [playing, setPlaying] = useState(false);
  const [playProgress, setPlayProgress] = useState(0);

  useEffect(() => {
    if (!playing) return undefined;

    const timer = window.setInterval(() => {
      setPlayProgress((value) => {
        if (value >= 100) {
          setPlaying(false);
          return 0;
        }
        return value + 1.5;
      });
    }, 180);

    return () => window.clearInterval(timer);
  }, [playing]);

  function createDemo() {
    if (phase === "processing") return;

    setPlaying(false);
    setPlayProgress(0);
    setGenerated(false);
    setPhase("processing");

    window.setTimeout(() => {
      setGenerated(true);
      setPhase("ready");
    }, 1500);
  }

  return (
    <WorkspacePage
      eyebrow="✦ PODCAST"
      title="Подкаст"
      description="Сценарий превращается в аудио-пайплайн: формат, голос, подготовка текста и будущий TTS-рендер."
      status={demoMode ? "DZ PRO · INTERACTIVE DEMO" : "UI DEMO · TTS NEXT"}
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
            <SpectralAction variant="primary" onClick={createDemo}>
              {phase === "processing" ? "✦ Готовлю аудио…" : generated ? "✦ Пересобрать аудио" : "✦ Подготовить аудио DEMO"}
            </SpectralAction>
          </div>

          <div className={`demoRunStatus demoRunStatus--${phase}`}>
            <div className="demoRunStatus__line">
              <span>{phase === "processing" ? "TTS DEMO PROCESS" : phase === "ready" ? "AUDIO READY" : "WAITING SCRIPT"}</span>
              <b>{phase === "processing" ? "script → chunks → voice render" : phase === "ready" ? `${voice} · 02:18 ✓` : "добавьте сценарий"}</b>
            </div>
            <i className="demoRunStatus__progress" />
          </div>
        </div>

        <div className={`podcastConsole ${generated ? "isReady" : ""} ${playing ? "isPlaying" : ""} ${phase === "processing" ? "isProcessing" : ""}`}>
          <div className="podcastConsole__cover"><span>◉</span><small>{format}</small></div>
          <div className="podcastConsole__meta">
            <small>BOOK-CRAFT PODCAST · 02:18</small>
            <h3>{phase === "processing" ? "Собираю аудиодорожку…" : generated ? "Истории, которые звучат" : "Аудио ещё не подготовлено"}</h3>
            <p>{generated ? `${voice} · TTS-ready pipeline · DEMO` : "Добавьте сценарий и запустите подготовку."}</p>
          </div>

          <div className="waveConsole" aria-hidden="true">
            {bars.map((height, i) => <i key={i} style={{height:`${generated ? height : 18}%`, animationDelay:`${i * 34}ms`}} />)}
          </div>

          <div className="audioProgressTrack"><i style={{width:`${playProgress}%`}} /></div>
          <small className="audioProgressLabel">{playing ? `DEMO PLAY · ${Math.round(playProgress)}%` : generated ? "READY TO PLAY" : "WAITING"}</small>

          <button className="audioPlayButton" type="button" disabled={!generated} onClick={() => setPlaying((value) => !value)}>
            {playing ? "❚❚ Пауза DEMO" : "▶ Прослушать DEMO"}
          </button>
        </div>
      </div>
    </WorkspacePage>
  );
}
