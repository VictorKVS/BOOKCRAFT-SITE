import { Link, useLocation } from "react-router-dom";

const studioTools = [
  ["/mailing", "Рассылка"],
  ["/podcast", "Подкаст"],
  ["/video-avatar", "Видео-аватар"],
  ["/images", "Изображения"],
];

export default function WorkspacePage({
  eyebrow,
  title,
  description,
  status = "MVP SKELETON",
  children
}) {
  const location = useLocation();

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

      <div className="workspaceToolRail" aria-label="Быстрый переход между модулями">
        {studioTools.map(([to, label], index) => (
          <Link key={to} to={to} className={location.pathname === to ? "active" : ""}>
            <small>0{index + 1}</small>
            <span>{label}</span>
          </Link>
        ))}
      </div>

      <div className="workspaceGrid">
        <div className="panel panel--main">
          {children}
        </div>

        <aside className="panel panel--side">
          <div className="panelTitleRow">
            <h3>Контент-интеллект</h3>
            <span className="dataBadge">DEMO</span>
          </div>

          <div className="sidePulse">
            <span className="sidePulse__dot" />
            <div><small>PIPELINE</small><b>готов к вводу</b></div>
          </div>

          <div className="demoMetric"><span>Тренд</span><b>—</b></div>
          <div className="demoMetric"><span>Confidence</span><b>—</b></div>
          <div className="demoMetric"><span>Потенциал</span><b>—</b></div>
          <div className="demoMetric"><span>Рекомендация</span><b>ожидает данных</b></div>

          <div className="sideNote">
            Здесь будут реальные метрики после подключения генерации и аналитики. Сейчас блок явно работает как DEMO.
          </div>

          <Link to="/analytics" className="textLink">Открыть полную аналитику →</Link>
        </aside>
      </div>
    </section>
  );
}
