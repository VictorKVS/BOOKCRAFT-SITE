import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const stack = [
  ["BOOK-CRAFT","Пользовательский продукт для производства контента"],
  ["ALINA","AI-оркестрация, аналитика и будущий интеллектуальный слой"],
  ["FATHER","Общая инженерная платформа, агенты, знания, модели и инструменты"],
];

export default function StudioPage() {
  return (
    <WorkspacePage
      eyebrow="✦ ABOUT"
      title="О студии"
      description="BOOK-CRAFT развивается как прикладной продукт внутри более широкой инженерной экосистемы ALINA / FATHER."
      status="PRODUCT STORY"
    >
      <div className="studioManifesto">
        <small>MISSION</small>
        <h2>Не просто генерировать контент, а собирать связанный производственный процесс.</h2>
        <p>Главная идея — пользователь работает с замыслом и результатом, а техническая сложность моделей, API и пайплайнов постепенно уходит внутрь платформы.</p>
      </div>

      <div className="studioStack">
        {stack.map(([name, text], index) => (
          <div key={name} className="studioLayer">
            <span>0{index + 1}</span>
            <div><small>LAYER</small><h3>{name}</h3><p>{text}</p></div>
          </div>
        ))}
      </div>

      <div className="studioActions">
        <Link to="/features">Посмотреть возможности →</Link>
        <Link to="/create">Открыть Create Hub →</Link>
      </div>
    </WorkspacePage>
  );
}
