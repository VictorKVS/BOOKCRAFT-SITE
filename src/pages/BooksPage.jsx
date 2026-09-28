import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const stages = ["Идея","Мир","Герои","План","Главы","Редактура"];

export default function BooksPage() {
  const [idea, setIdea] = useState("");
  const [genre, setGenre] = useState("Фантастика");
  const [ready, setReady] = useState(false);

  return (
    <WorkspacePage
      eyebrow="✦ BOOKS"
      title="Книги"
      description="Длинный narrative workflow: замысел, мир, герои, структура, главы и редактура."
      status="EXPANSION UI"
    >
      <div className="moduleHero moduleHero--books">
        <div><small>IDEA</small><b>Замысел</b></div><span>→</span>
        <div><small>WORLD</small><b>Мир + герои</b></div><span>→</span>
        <div><small>BOOK</small><b>Главы</b></div>
      </div>

      <div className="fieldPair">
        <label className="field">
          <span>Жанр</span>
          <select value={genre} onChange={(e) => setGenre(e.target.value)}>
            <option>Фантастика</option><option>Детектив</option><option>Драма</option><option>Нон-фикшн</option>
          </select>
        </label>
        <label className="field">
          <span>Рабочий режим</span>
          <select defaultValue="Архитектор истории"><option>Архитектор истории</option><option>Черновик главы</option><option>Редактор</option></select>
        </label>
      </div>

      <label className="field">
        <span>Идея книги</span>
        <textarea rows="6" value={idea} onChange={(e) => setIdea(e.target.value)} placeholder="Опишите сюжет, тему, конфликт или мир..." />
      </label>

      <SpectralAction variant="primary" onClick={() => setReady(true)}>✦ Собрать DEMO-архитектуру</SpectralAction>

      <div className={`bookPipeline ${ready ? "isReady" : ""}`}>
        {stages.map((stage, i) => <div key={stage}><small>0{i+1}</small><b>{stage}</b><span>{ready ? (i < 4 ? "структура готова" : "следующий этап") : "waiting"}</span></div>)}
      </div>
    </WorkspacePage>
  );
}
