import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const examples = [
  {title:"Запуск продукта", flow:"Рассылка → изображение → видео-аватар", to:"/mailing", kind:"launch"},
  {title:"Авторская история", flow:"Книга → сцены → визуальный мир", to:"/books", kind:"book"},
  {title:"Экспертный выпуск", flow:"Сценарий → подкаст → короткое видео", to:"/podcast", kind:"podcast"},
  {title:"Контент-серия", flow:"Идея → контент-план → 4 формата", to:"/create", kind:"series"},
  {title:"Промо-ролик", flow:"Сценарий → аватар → визуальные кадры", to:"/video-avatar", kind:"video"},
  {title:"Визуальная концепция", flow:"Промпт → варианты → выбранный стиль", to:"/images", kind:"visual"},
];

export default function ExamplesPage() {
  return (
    <WorkspacePage
      eyebrow="✦ SHOWCASE"
      title="Примеры"
      description="Демонстрационные сценарии использования. Это продуктовые примеры, а не заявления о реальных клиентских кейсах."
      status="DEMO SHOWCASE"
    >
      <div className="showcaseGrid">
        {examples.map((item, index) => (
          <Link to={item.to} key={item.title} className={`showcaseCard showcaseCard--${item.kind} spectralSurface`}>
            <div className="showcaseVisual"><span>0{index + 1}</span><i>✦</i></div>
            <small>DEMO CASE</small>
            <h3>{item.title}</h3>
            <p>{item.flow}</p>
            <b>Открыть сценарий →</b>
          </Link>
        ))}
      </div>
    </WorkspacePage>
  );
}
