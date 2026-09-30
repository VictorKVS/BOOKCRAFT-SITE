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

  return (
    <WorkspacePage
      eyebrow="✦ EXTRA TAB"
      title="Лонгрид"
      description="Дополнительная вкладка ДЗ PRO: из темы и аудитории собираем структуру большого материала и редакционный черновик."
      status="DZ PRO · EXTRA TAB"
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

          <SpectralAction variant="primary" onClick={() => setReady(true)}>✦ Собрать структуру</SpectralAction>

          {demoMode && (
            <div className="demoEvidence">
              <small>REQUIREMENT</small>
              <b>Дополнительная вкладка — выполнено</b>
              <span>Лонгрид использует отдельную логику и собственный визуальный workflow.</span>
            </div>
          )}
        </div>

        <article className={`longreadPreview ${ready ? "isReady" : ""}`}>
          <div className="longreadPreview__head">
            <small>BOOK-CRAFT EDITORIAL</small>
            <span>8–10 MIN READ</span>
          </div>
          <h2>{ready ? topic : "Здесь появится архитектура лонгрида"}</h2>
          <p className="longreadDek">{ready ? `Для: ${audience} · Тон: ${tone}` : "Сначала задайте тему и аудиторию."}</p>

          <div className="longreadSections">
            {(ready ? demoSections : []).map(([n, title, text]) => (
              <section key={n}>
                <small>{n}</small>
                <div><b>{title}</b><p>{text}</p></div>
              </section>
            ))}
          </div>
        </article>
      </div>
    </WorkspacePage>
  );
}
