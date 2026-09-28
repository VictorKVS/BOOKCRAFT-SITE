import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const modules = [
  ["/mailing","Рассылка","AI-текст рассылки","MVP"],
  ["/podcast","Подкаст","Сценарий и аудио","MVP"],
  ["/video-avatar","Видео-Аватар","Голоса и аватары внешнего сервиса","MVP"],
  ["/images","Изображения","Локальная генерация / ComfyUI","BONUS"],
  ["/books","Книги","Главы, герои и длинный контент","CARCASS"],
  ["/scripts","Сценарии клипов","Сцены, кадры и storyboard","CARCASS"],
];

export default function CreatePage() {
  return (
    <WorkspacePage
      eyebrow="✦ CREATE HUB"
      title="Что создаём?"
      description="Черновой рабочий хаб: все видимые продуктовые направления имеют реальные маршруты и не ведут в тупик."
      status="CARCASS LOCK"
    >
      <div className="choiceGrid">
        {modules.map(([to,title,text,status]) => (
          <Link to={to} className="choiceCard spectralSurface" key={to}>
            <small className="moduleState">{status}</small>
            <b>{title}</b>
            <span>{text}</span>
            <i>Открыть →</i>
          </Link>
        ))}
      </div>
    </WorkspacePage>
  );
}
