import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function MailingPage() {
  const [topic, setTopic] = useState("");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState("Деловой");
  const [result, setResult] = useState("");

  function generateDemo() {
    const safeTopic = topic.trim() || "новый продукт";
    const safeAudience = audience.trim() || "аудитория проекта";
    setResult(
      `DEMO · ${tone} тон\n\nТема: ${safeTopic}\nАудитория: ${safeAudience}\n\nЗдесь появится результат реальной LLM-генерации после подключения backend/API.`
    );
  }

  function reset() {
    setTopic("");
    setAudience("");
    setTone("Деловой");
    setResult("");
  }

  return (
    <WorkspacePage
      eyebrow="✦ MAILING"
      title="Рассылка"
      description="MVP-каркас генерации рассылки. Сейчас проверяем форму, состояния и место результата; LLM ещё не подключена."
      status="UI DEMO"
    >
      <label className="field">
        <span>Тема</span>
        <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Например: запуск нового продукта" />
      </label>

      <label className="field">
        <span>Аудитория</span>
        <input value={audience} onChange={(e) => setAudience(e.target.value)} placeholder="Для кого пишем" />
      </label>

      <label className="field">
        <span>Тон</span>
        <select value={tone} onChange={(e) => setTone(e.target.value)}>
          <option>Деловой</option>
          <option>Дружелюбный</option>
          <option>Премиальный</option>
        </select>
      </label>

      <div className="formActions">
        <SpectralAction variant="primary" onClick={generateDemo}>Сгенерировать DEMO</SpectralAction>
        <button className="secondaryButton" type="button" onClick={reset}>Очистить</button>
      </div>

      <pre className={`resultPlaceholder resultPlaceholder--text ${result ? "isReady" : ""}`}>
        {result || "Результат появится здесь"}
      </pre>
    </WorkspacePage>
  );
}
