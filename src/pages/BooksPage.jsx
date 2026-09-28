import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function BooksPage() {
  const [idea, setIdea] = useState("");
  const [ready, setReady] = useState(false);

  return (
    <WorkspacePage
      eyebrow="✦ BOOKS"
      title="Книги"
      description="Черновой длинный workflow: идея → структура → главы → редактура."
      status="CARCASS"
    >
      <label className="field">
        <span>Идея книги</span>
        <textarea rows="5" value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Опишите сюжет, тему или мир..." />
      </label>
      <SpectralAction variant="primary" onClick={() => setReady(true)}>Собрать DEMO-структуру</SpectralAction>

      <div className={`pipelineSkeleton ${ready ? "isReady" : ""}`}>
        {["Идея","План","Главы","Редактура","Публикация"].map((x, i) => (
          <div key={x}><small>0{i+1}</small><b>{x}</b></div>
        ))}
      </div>
    </WorkspacePage>
  );
}
