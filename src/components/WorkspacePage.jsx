import { Link } from "react-router-dom";

export default function WorkspacePage({
  eyebrow,
  title,
  description,
  status = "MVP SKELETON",
  children
}) {
  return (
    <section className="workspace">
      <div className="workspaceHead">
        <div>
          <div className="eyebrow">{eyebrow}</div>
          <h1 className="workspaceTitle">{title}</h1>
          <p className="workspaceLead">{description}</p>
        </div>
        <span className="statusBadge">{status}</span>
      </div>

      <div className="workspaceGrid">
        <div className="panel panel--main">
          {children}
        </div>

        <aside className="panel panel--side">
          <div className="panelTitleRow">
            <h3>Аналитика</h3>
            <span className="dataBadge">DEMO</span>
          </div>
          <div className="demoMetric"><span>Тренд</span><b>—</b></div>
          <div className="demoMetric"><span>Confidence</span><b>—</b></div>
          <div className="demoMetric"><span>Потенциал</span><b>—</b></div>
          <div className="demoMetric"><span>Рекомендация</span><b>ожидает данных</b></div>
          <Link to="/analytics" className="textLink">Открыть полную аналитику →</Link>
        </aside>
      </div>
    </section>
  );
}
