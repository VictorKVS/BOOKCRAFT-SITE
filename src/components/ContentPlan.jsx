import { Link } from "react-router-dom";

const items = [
  { day: "Пн", label: "Книга — Глава 3", to: "/books" },
  { day: "Вт", label: "Пост + Изображения", to: "/images" },
  { day: "Ср", label: "Видео-аватар", to: "/video-avatar" },
  { day: "Чт", label: "Подкаст (запись)", to: "/podcast" },
  { day: "Пт", label: "Рассылка (Newsletter)", to: "/mailing" },
];

export default function ContentPlan() {
  return (
    <section className="contentPlan" aria-label="Контент-план">
      <div className="contentPlan__title">КОНТЕНТ-ПЛАН</div>

      <div className="contentPlan__list">
        {items.map((item) => (
          <Link className="contentPlan__row" to={item.to} key={`${item.day}-${item.label}`}>
            <span className="contentPlan__check">✓</span>
            <span className="contentPlan__day">{item.day}</span>
            <span className="contentPlan__label">{item.label}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
