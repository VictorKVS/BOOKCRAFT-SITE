import { Link } from "react-router-dom";

export default function PodcastHud() {
  const bars = [18,28,44,32,52,38,58,30,48,60,34,50,26,42,56,36,46,24];

  return (
    <Link to="/podcast" className="insightHud podcastHud" aria-label="Открыть модуль подкаста">
      <div className="insightHud__head">
        <span>ПОДКАСТ</span>
        <small>DEMO</small>
      </div>

      <div className="podcastHud__body">
        <span className="micIcon">◉</span>

        <div className="waveform" aria-hidden="true">
          {bars.map((height, index) => (
            <i key={index} style={{ height: `${height}%` }} />
          ))}
        </div>

        <span className="playMini">▶</span>
      </div>

      <div className="podcastHud__time">
        <span>00:24</span>
        <span>/</span>
        <span>12:38</span>
      </div>
    </Link>
  );
}
