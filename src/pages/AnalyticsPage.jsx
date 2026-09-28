import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const cards = [
  ["Trend Radar","↑ Story Series","Confidence 0.71 · DEMO"],
  ["Рассылка","Open / CTR / conversion","ожидает реальные данные"],
  ["Подкаст","Completion / drop-off","ожидает реальные данные"],
  ["Видео-Аватар","Voice / avatar / completion","ожидает реальные данные"],
  ["Изображения","Selected style / reuse","ожидает реальные данные"],
  ["Завод","Latency / rework / cost","ожидает реальные данные"],
];

export default function AnalyticsPage() {
  return (
    <WorkspacePage
      eyebrow="✦ CONTENT INTELLIGENCE"
      title="Аналитика"
      description="Будущий слой обратной связи BOOK-CRAFT. Сейчас все числа и графики явно обозначены как DEMO."
      status="DEMO DATA ONLY"
    >
      <div className="analyticsHero">
        <div><small>DEMO INDEX</small><strong>71</strong><span>content signal</span></div>
        <div className="analyticsHero__chart" aria-hidden="true">{[22,40,34,58,49,72,66,82,74,88].map((h,i)=><i key={i} style={{height:`${h}%`}} />)}</div>
        <div><small>NEXT SIGNAL</small><b>Story Series</b><span>пример рекомендации</span></div>
      </div>

      <div className="analyticsGrid">
        {cards.map(([title,value,note]) => (
          <div className="analyticCard" key={title}>
            <small>DEMO</small>
            <h3>{title}</h3>
            <b>{value}</b>
            <span>{note}</span>
          </div>
        ))}
      </div>

      <div className="recommendation">
        <small>DEMO · ALINA RECOMMENDS</small>
        <h3>Следующий эксперимент</h3>
        <p>После подключения реальных данных здесь появятся причина рекомендации, горизонт, confidence и измеримый результат.</p>
        <SpectralAction to="/create" variant="analytics">Создать варианты →</SpectralAction>
      </div>
    </WorkspacePage>
  );
}
