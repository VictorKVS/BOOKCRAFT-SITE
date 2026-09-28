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
      description="Только проверка формы и состояний интерфейса. Настоящая авторизация ещё не подключена."
      status="DEMO ONLY"
    >
      <label className="field">
        <span>Email</span>
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="name@example.com" />
      </label>

      <SpectralAction variant="primary" onClick={() => setChecked(true)}>
        Проверить UI-состояние
      </SpectralAction>

      {checked && (
        <div className="noticeBox">
          <b>DEMO</b>
          <span>Форма работает. Реальная сессия пользователя не создавалась.</span>
        </div>
      )}
    </WorkspacePage>
  );
}
