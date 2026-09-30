import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const demoSections = [
  ["01", "От одной идеи к контентной системе", "Почему разрозненные генераторы создают много ручной работы и как единый контекст меняет процесс."],
  ["02", "Narrative Core", "Одна тема становится источником для рассылки, подкаста, видео, изображений и длинного материала."],
  ["03", "Контент без потери контекста", "Форматы различаются, но герои, тон, факты и визуальная логика остаются согласованными."],
  ["04", "От прототипа к производству", "Системные промпты, API-контракты, аналитика и публикация собираются вокруг одного workflow."],
];

export default function LongreadPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [topic, setTopic] = useState(demoMode ? "Как одна идея превращается в контентную экосистему" : "");
  const [audience, setAudience] = useState(demoMode ? "Креативные команды и авторы" : "");
  const [tone, setTone] = useState(demoMode ? "Редакционный / премиальный" : "Редакционный");
  const [ready, setReady] = useState(demoMode);
  const [phase, setPhase] = useState(demoMode ? "ready" : "idle");

  function generate() {
    if (phase === "processing") return;

    setReady(false);
    setPhase("processing");

    window.setTimeout(() => {
      setReady(true);
      setPhase("ready");
    }, 1400);
  }

  return (
    <WorkspacePage
      eyebrow="✦ EXTRA TAB"
      title="Лонгрид"
      description="Дополнительная вкладка ДЗ PRO: из темы и аудитории собираем структуру большого материала и редакционный черновик."
      status={demoMode ? "DZ PRO · INTERACTIVE DEMO" : "DZ PRO · EXTRA TAB"}
    >
      <div className="moduleHero moduleHero--longread">
        <div><small>BRIEF</small><b>Тема + аудитория</b></div>
        <span>→</span>
        <div><small>EDITOR</small><b>Структура + narrative arc</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Longread draft</b></div>
      </div>

      <div className="editorGrid">
        <div className="editorColumn">
          <label className="field">
            <span>Тема</span>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Тема большого материала" />
          </label>

          <label className="field">
            <span>Аудитория</span>
            <input value={audience} onChange={(e) => setAudience(e.target.value)} placeholder="Для кого пишем" />
          </label>

          <label className="field">
            <span>Редакционный тон</span>
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              <option>Редакционный</option>
              <option>Редакционный / премиальный</option>
              <option>Объясняющий</option>
              <option>Экспертный</option>
            </select>
          </label>

          <SpectralAction variant="primary" onClick={generate}>
            {phase === "processing" ? "✦ Строю лонгрид…" : ready ? "✦ Пересобрать структуру" : "✦ Собрать структуру"}
          </SpectralAction>

          <div className={`demoRunStatus demoRunStatus--${phase}`}>
            <div className="demoRunStatus__line">
              <span>{phase === "processing" ? "EDITOR DEMO PROCESS" : phase === "ready" ? "LONGREAD READY" : "WAITING BRIEF"}</span>
              <b>{phase === "processing" ? "thesis → outline → narrative arc" : phase === "ready" ? "4 раздела · структура готова ✓" : "задайте тему"}</b>
            </div>
            <i className="demoRunStatus__progress" />
          </div>
        </div>

        <article className={`longreadPreview ${ready ? "isReady" : ""} ${phase === "processing" ? "isProcessing" : ""}`}>
          <div className="longreadPreview__head">
            <small>BOOK-CRAFT EDITORIAL</small>
            <span>{phase === "processing" ? "BUILDING…" : "8–10 MIN READ"}</span>
          </div>

          <h2>{phase === "processing" ? "Собираю архитектуру материала…" : ready ? topic : "Здесь появится архитектура лонгрида"}</h2>
          <p className="longreadDek">{ready ? `Для: ${audience} · Тон: ${tone}` : phase === "processing" ? "Анализ темы и аудитории…" : "Сначала задайте тему и аудиторию."}</p>

          {phase === "processing" ? (
            <div className="demoSkeleton demoSkeleton--longread"><i /><i /><i /><i /><i /><i /></div>
          ) : (
            <div className="longreadSections">
              {(ready ? demoSections : []).map(([n, title, text], index) => (
                <section key={n} style={{animationDelay:`${index * 90}ms`}}>
                  <small>{n}</small>
                  <div><b>{title}</b><p>{text}</p></div>
                </section>
              ))}
            </div>
          )}
        </article>
      </div>
    </WorkspacePage>
  );
}
