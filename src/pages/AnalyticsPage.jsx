import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const cards = [
  ["Trend Radar","↑ Story Series","Confidence 0.71 · 14d"],
  ["Рассылка","Open / CTR / conversion","ожидает реальные данные"],
  ["Подкаст","Completion / drop-off","ожидает реальные данные"],
  ["Видео-Аватар","Voice / avatar / completion","ожидает реальные данные"],
  ["Изображения","Selected style / reuse","ожидает реальные данные"],
  ["Завод","Latency / rework / cost","ожидает реальные данные"],
];

export default function AnalyticsPage() {
  return (
    <WorkspacePage eyebrow="✦ CONTENT INTELLIGENCE" title="Аналитика" description="Отдельный продуктовый слой. В MVP данные явно помечены DEMO.">
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
        <p>Здесь будет рекомендация с причиной, горизонтом, confidence и кнопкой запуска следующего производственного цикла.</p>
        <SpectralAction to="/create" variant="analytics">Создать варианты →</SpectralAction>
      </div>
    </WorkspacePage>
  );
}
