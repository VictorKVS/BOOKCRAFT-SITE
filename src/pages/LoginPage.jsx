import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [checked, setChecked] = useState(false);

  return (
    <WorkspacePage
      eyebrow="✦ ACCOUNT"
      title="Войти"
      description="Демонстрационный экран будущего аккаунта. Настоящая авторизация и пользовательская сессия ещё не подключены."
      status="DEMO ONLY"
    >
      <div className="loginStage">
        <div className="loginStage__brand">
          <span>✦</span>
          <small>BOOK-CRAFT ACCOUNT</small>
          <h2>Ваше творческое пространство</h2>
          <p>Проекты, контент, история генераций и аналитика будут доступны из одного аккаунта.</p>
        </div>

        <div className="loginStage__form">
          <label className="field">
            <span>Email</span>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="name@example.com" />
          </label>
          <SpectralAction variant="primary" onClick={() => setChecked(true)}>Продолжить DEMO</SpectralAction>
          {checked && <div className="noticeBox"><b>DEMO</b><span>UI-состояние проверено. Реальная сессия пользователя не создавалась.</span></div>}
        </div>
      </div>
    </WorkspacePage>
  );
}
