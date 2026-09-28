import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const plans = [
  {name:"START", note:"Для знакомства", accent:"light", items:["Рассылка","Подкаст","Видео-аватар DEMO","Ограниченные image-слоты"]},
  {name:"CREATOR", note:"Основной рабочий набор", accent:"creator", items:["Все CORE-модули","Изображения","Книги и сценарии","История проектов"]},
  {name:"STUDIO", note:"Командный контур", accent:"studio", items:["Командные проекты","Общий контекст","Аналитика","Будущая FATHER-интеграция"]},
];

export default function PricingPage() {
  return (
    <WorkspacePage
      eyebrow="✦ PLANS"
      title="Тарифы"
      description="Структура тарифов готова визуально. Цены и реальные лимиты пока не публикуем — они определяются после подключения API и расчёта себестоимости."
      status="DRAFT · NO PRICES"
    >
      <div className="pricingGrid">
        {plans.map((plan, index) => (
          <article key={plan.name} className={`pricingCard pricingCard--${plan.accent}`}>
            <div className="pricingCard__head"><small>PLAN 0{index + 1}</small><span>DRAFT</span></div>
            <h3>{plan.name}</h3>
            <p>{plan.note}</p>
            <div className="pricingPlaceholder">Цена после расчёта API</div>
            <ul>{plan.items.map((item) => <li key={item}>✓ {item}</li>)}</ul>
            <Link to="/create">Попробовать интерфейс →</Link>
          </article>
        ))}
      </div>
      <div className="pricingNote">
        <b>Почему без выдуманных цен?</b>
        <span>Стоимость зависит от LLM, TTS и внешнего avatar API. До подключения провайдеров показываем только продуктовую структуру тарифов.</span>
      </div>
    </WorkspacePage>
  );
}
