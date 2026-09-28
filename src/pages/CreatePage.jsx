import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const modules = [
  {to:"/mailing", number:"01", title:"Рассылка", text:"Тема → аудитория → письмо", status:"CORE MVP", kind:"mail"},
  {to:"/podcast", number:"02", title:"Подкаст", text:"Сценарий → TTS → аудио", status:"CORE MVP", kind:"podcast"},
  {to:"/video-avatar", number:"03", title:"Видео-Аватар", text:"Голос + аватар → видео", status:"CORE MVP", kind:"avatar"},
  {to:"/images", number:"04", title:"Изображения", text:"Промпт → варианты → выбор", status:"BONUS", kind:"images"},
  {to:"/books", number:"05", title:"Книги", text:"Идея → главы → редактура", status:"EXPANSION", kind:"books"},
  {to:"/scripts", number:"06", title:"Сценарии клипов", text:"Идея → сцены → storyboard", status:"EXPANSION", kind:"scripts"},
];

export default function CreatePage() {
  return (
    <WorkspacePage
      eyebrow="✦ CREATE HUB"
      title="Что создаём?"
      description="Единый производственный хаб BOOK-CRAFT: сначала выбираем формат, затем работаем в специализированном рабочем месте."
      status="UI PASS 01"
    >
      <div className="createIntro">
        <div><small>START</small><b>Одна идея</b><span>может пройти сразу через несколько форматов</span></div>
        <i>→</i>
        <div><small>ORCHESTRATE</small><b>Общий контекст</b><span>между текстом, аудио, видео и изображениями</span></div>
      </div>

      <div className="choiceGrid choiceGrid--studio">
        {modules.map((item) => (
          <Link to={item.to} className={`choiceCard choiceCard--${item.kind} spectralSurface`} key={item.to}>
            <div className="choiceCard__top">
              <small className="choiceNumber">{item.number}</small>
              <small className="moduleState">{item.status}</small>
            </div>
            <b>{item.title}</b>
            <span>{item.text}</span>
            <i>Открыть модуль →</i>
          </Link>
        ))}
      </div>
    </WorkspacePage>
  );
}
