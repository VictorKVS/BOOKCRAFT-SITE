import { Link } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";

const features = [
  {n:"01", title:"Рассылки", text:"Генерация структуры письма, темы, preheader и основного текста.", to:"/mailing", tag:"CORE"},
  {n:"02", title:"Подкасты", text:"Сценарий, голос, TTS-пайплайн и контроль аудио-выхода.", to:"/podcast", tag:"CORE"},
  {n:"03", title:"Видео-аватары", text:"Каталог голосов и аватаров внешнего сервиса, подготовка video job.", to:"/video-avatar", tag:"CORE"},
  {n:"04", title:"Изображения", text:"Локальная генерация через image engine / ComfyUI и выбор варианта.", to:"/images", tag:"BONUS"},
  {n:"05", title:"Книги", text:"Длинный контент: идея, структура, главы, редактура и публикация.", to:"/books", tag:"EXPANSION"},
  {n:"06", title:"Сценарии", text:"Разложение истории на сцены, кадры, реплики и storyboard.", to:"/scripts", tag:"EXPANSION"},
  {n:"07", title:"Аналитика", text:"Отдельный слой метрик, рекомендаций и обратной связи.", to:"/analytics", tag:"DEMO"},
  {n:"08", title:"Общий контекст", text:"Единая логика продукта: один замысел может проходить через несколько форматов.", to:"/create", tag:"PLATFORM"},
];

export default function FeaturesPage() {
  return (
    <WorkspacePage
      eyebrow="✦ PRODUCT"
      title="Возможности"
      description="BOOK-CRAFT собирает текст, аудио, видео и визуальный контент в один связанный производственный поток."
      status="PRODUCT MAP"
    >
      <div className="featureMatrix">
        {features.map((item) => (
          <Link to={item.to} key={item.n} className="featureTile spectralSurface">
            <div className="featureTile__top"><span>{item.n}</span><small>{item.tag}</small></div>
            <h3>{item.title}</h3>
            <p>{item.text}</p>
            <b>Открыть →</b>
          </Link>
        ))}
      </div>
    </WorkspacePage>
  );
}
