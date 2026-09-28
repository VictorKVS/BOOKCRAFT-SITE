import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function ScriptsPage() {
  const [idea, setIdea] = useState("");
  const [ready, setReady] = useState(false);

  return (
    <WorkspacePage
      eyebrow="✦ STORYBOARD"
      title="Сценарии клипов"
      description="Черновой workflow сценария: идея → сцены → кадры → storyboard → ролик."
      status="CARCASS"
    >
      <label className="field">
        <span>Идея клипа</span>
        <textarea rows="5" value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Опишите сцену, сюжет или настроение..." />
      </label>
      <SpectralAction variant="primary" onClick={() => setReady(true)}>Разложить на DEMO-сцены</SpectralAction>

      <div className={`storyboardSkeleton ${ready ? "isReady" : ""}`}>
        {[1,2,3,4].map((n) => (
          <div key={n}><small>SCENE {String(n).padStart(2,"0")}</small><span>{ready ? "кадр / реплика / действие" : "SCENE SLOT"}</span></div>
        ))}
      </div>
    </WorkspacePage>
  );
}
