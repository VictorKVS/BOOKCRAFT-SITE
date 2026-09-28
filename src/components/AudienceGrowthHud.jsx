import { Link } from "react-router-dom";

export default function AudienceGrowthHud() {
  return (
    <Link to="/analytics" className="insightHud audienceHud" aria-label="Открыть аналитику роста аудитории">
      <div className="insightHud__head">
        <span>РОСТ АУДИТОРИИ</span>
        <small>DEMO</small>
      </div>

      <div className="audienceHud__body">
        <strong>+287%</strong>

        <div className="audienceChart" aria-hidden="true">
          <i className="bar bar1" />
          <i className="bar bar2" />
          <i className="bar bar3" />
          <i className="bar bar4" />
          <i className="bar bar5" />
          <span className="trendLine">↗</span>
        </div>
      </div>

      <div className="audienceLabels">
        <span>Янв</span><span>Фев</span><span>Мар</span><span>Апр</span>
      </div>
    </Link>
  );
}
