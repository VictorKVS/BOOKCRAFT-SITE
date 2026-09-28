import { Link } from "react-router-dom";

export default function VideoAvatarHud() {
  return (
    <Link to="/video-avatar" className="insightHud avatarHud" aria-label="Открыть Видео-Аватар">
      <div className="insightHud__head">
        <span>ВИДЕО-АВАТАР</span>
        <small>DEMO</small>
      </div>

      <div className="avatarHud__grid">
        <div className="avatarHud__main">
          <span className="avatarSilhouette">◎</span>
          <span className="playMini avatarPlay">▶</span>
        </div>

        <div className="avatarHud__thumbs">
          <span>01</span>
          <span>02</span>
          <span>03</span>
        </div>
      </div>
    </Link>
  );
}
