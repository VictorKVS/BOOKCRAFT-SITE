import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const demoResult = {
  subject: "Истории, которые превращают идеи в контент",
  preheader: "BOOK-CRAFT собирает текст, аудио, видео и визуалы в один narrative workflow",
  body: "Здравствуйте!\n\nПредставляем BOOK-CRAFT — AI-студию для авторов и команд, которым нужно быстро превращать одну идею в связанный набор контента.\n\nИз одной темы можно подготовить рассылку, подкаст, сценарий видео-аватара, изображения и длинную историю — в едином визуальном и смысловом стиле.\n\nГлавное преимущество — общий контекст: материалы не создаются изолированно, а продолжают одну историю.\n\nПопробуйте собрать первую кампанию и сравните, сколько ручных переходов между инструментами удалось убрать.\n\nBOOK-CRAFT · Narrative AI Studio"
};

export default function MailingPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [topic, setTopic] = useState(demoMode ? "Запуск BOOK-CRAFT Narrative AI Studio" : "");
  const [audience, setAudience] = useState(demoMode ? "Авторы, маркетологи и небольшие креативные команды" : "");
  const [goal, setGoal] = useState(demoMode ? "Заинтересовать" : "Заинтересовать");
  const [tone, setTone] = useState(demoMode ? "Премиальный" : "Деловой");
  const [result, setResult] = useState(demoMode ? demoResult : null);

  function generateDemo() {
    const safeTopic = topic.trim() || "новый продукт";
    const safeAudience = audience.trim() || "аудитория проекта";

    if (demoMode) {
      setResult(demoResult);
      return;
    }

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
      status={demoMode ? "DZ PRO · SCREENSHOT DEMO" : "UI DEMO · LLM NEXT"}
    >
      <div className="moduleHero moduleHero--mail">
        <div><small>INPUT CONTRACT</small><b>Тема + аудитория + цель + тон</b></div>
        <span>→</span>
        <div><small>SYSTEM PROMPT</small><b>BOOK-CRAFT Mail Editor</b></div>
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

          {demoMode && (
            <div className="demoEvidence">
              <small>SCREENSHOT STATE</small>
              <b>Входные данные заполнены · результат готов</b>
              <span>Этот URL предназначен для итогового тестирования и скриншота.</span>
            </div>
          )}
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
