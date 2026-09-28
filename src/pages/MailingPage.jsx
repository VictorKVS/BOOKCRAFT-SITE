import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function MailingPage() {
  const [topic, setTopic] = useState("");
  const [audience, setAudience] = useState("");
  const [goal, setGoal] = useState("Заинтересовать");
  const [tone, setTone] = useState("Деловой");
  const [result, setResult] = useState(null);

  function generateDemo() {
    const safeTopic = topic.trim() || "новый продукт";
    const safeAudience = audience.trim() || "аудитория проекта";
    setResult({
      subject: `${safeTopic}: коротко о главном`,
      preheader: `${tone} формат для сегмента «${safeAudience}»`,
      body: `Здравствуйте!\n\nПодготовили материал по теме «${safeTopic}». Цель сообщения — ${goal.toLowerCase()}. В рабочей версии здесь будет текст, созданный реальной LLM по системному промпту BOOK-CRAFT.\n\nDEMO: структура интерфейса и состояния уже готовы.`
    });
  }

  function reset() {
    setTopic("");
    setAudience("");
    setGoal("Заинтересовать");
    setTone("Деловой");
    setResult(null);
  }

  return (
    <WorkspacePage
      eyebrow="✦ MAILING"
      title="Рассылка"
      description="Рабочее место для подготовки письма: задаём тему, аудиторию, цель и тон — затем получаем редактируемый результат."
      status="UI DEMO · LLM NEXT"
    >
      <div className="moduleHero moduleHero--mail">
        <div><small>INPUT CONTRACT</small><b>Тема + аудитория + цель + тон</b></div>
        <span>→</span>
        <div><small>OUTPUT</small><b>Subject + preheader + письмо</b></div>
      </div>

      <div className="editorGrid">
        <div className="editorColumn">
          <label className="field">
            <span>Тема</span>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Например: запуск нового продукта" />
          </label>

          <label className="field">
            <span>Аудитория</span>
            <input value={audience} onChange={(e) => setAudience(e.target.value)} placeholder="Для кого пишем" />
          </label>

          <div className="fieldPair">
            <label className="field">
              <span>Цель</span>
              <select value={goal} onChange={(e) => setGoal(e.target.value)}>
                <option>Заинтересовать</option>
                <option>Продать</option>
                <option>Проинформировать</option>
                <option>Вернуть аудиторию</option>
              </select>
            </label>

            <label className="field">
              <span>Тон</span>
              <select value={tone} onChange={(e) => setTone(e.target.value)}>
                <option>Деловой</option>
                <option>Дружелюбный</option>
                <option>Премиальный</option>
                <option>Энергичный</option>
              </select>
            </label>
          </div>

          <div className="formActions">
            <SpectralAction variant="primary" onClick={generateDemo}>✦ Сгенерировать DEMO</SpectralAction>
            <button className="secondaryButton" type="button" onClick={reset}>Очистить</button>
          </div>
        </div>

        <div className={`outputEditor ${result ? "isReady" : ""}`}>
          <div className="outputEditor__head">
            <span>RESULT</span>
            <small>{result ? "DEMO READY" : "WAITING INPUT"}</small>
          </div>
          {result ? (
            <>
              <label><small>SUBJECT</small><b>{result.subject}</b></label>
              <label><small>PREHEADER</small><span>{result.preheader}</span></label>
              <pre>{result.body}</pre>
            </>
          ) : (
            <div className="outputEmpty">Здесь появится редактируемая версия рассылки.</div>
          )}
        </div>
      </div>
    </WorkspacePage>
  );
}
