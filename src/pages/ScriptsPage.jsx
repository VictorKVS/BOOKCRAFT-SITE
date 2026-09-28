import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function ScriptsPage() {
  const [idea, setIdea] = useState("");
  const [format, setFormat] = useState("Музыкальный клип");
  const [ready, setReady] = useState(false);

  return (
    <WorkspacePage
      eyebrow="✦ STORYBOARD"
      title="Сценарии клипов"
      description="От идеи к монтажной структуре: сцены, действия, реплики, визуальная задача и storyboard."
      status="EXPANSION UI"
    >
      <div className="moduleHero moduleHero--scripts">
        <div><small>IDEA</small><b>Сюжет</b></div><span>→</span>
        <div><small>SCENES</small><b>Сцены + кадры</b></div><span>→</span>
        <div><small>OUTPUT</small><b>Storyboard</b></div>
      </div>

      <div className="fieldPair">
        <label className="field"><span>Формат</span><select value={format} onChange={(e)=>setFormat(e.target.value)}><option>Музыкальный клип</option><option>Shorts / Reels</option><option>Промо</option><option>Сценическая история</option></select></label>
        <label className="field"><span>Темп</span><select defaultValue="Динамичный"><option>Динамичный</option><option>Средний</option><option>Медленный</option></select></label>
      </div>

      <label className="field">
        <span>Идея</span>
        <textarea rows="6" value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Опишите сцену, сюжет, настроение и ключевые визуальные образы..." />
      </label>

      <SpectralAction variant="primary" onClick={() => setReady(true)}>Разложить на DEMO-сцены</SpectralAction>

      <div className={`storyboardStudio ${ready ? "isReady" : ""}`}>
        {[1,2,3,4].map((n) => (
          <article key={n}>
            <div className={`storyboardFrame storyboardFrame--${n}`}><span>SCENE 0{n}</span></div>
            <div><small>{format}</small><b>{ready ? ["Завязка","Развитие","Поворот","Финал"][n-1] : "SCENE SLOT"}</b><p>{ready ? "кадр · действие · реплика · визуальная задача" : "ожидает разложения"}</p></div>
          </article>
        ))}
      </div>
    </WorkspacePage>
  );
}
