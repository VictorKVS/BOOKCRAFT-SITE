import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const demoResults = [
  {
    subject: "Истории, которые превращают идеи в контент",
    preheader: "BOOK-CRAFT собирает текст, аудио, видео и визуалы в один narrative workflow",
    body: "Здравствуйте!\n\nПредставляем BOOK-CRAFT — AI-студию для авторов и команд, которым нужно быстро превращать одну идею в связанный набор контента.\n\nИз одной темы можно подготовить рассылку, подкаст, сценарий видео-аватара, изображения и длинную историю — в едином визуальном и смысловом стиле.\n\nГлавное преимущество — общий контекст: материалы не создаются изолированно, а продолжают одну историю.\n\nПопробуйте собрать первую кампанию и сравните, сколько ручных переходов между инструментами удалось убрать.\n\nBOOK-CRAFT · Narrative AI Studio"
  },
  {
    subject: "Одна идея — пять форматов: новый workflow BOOK-CRAFT",
    preheader: "Рассылка, подкаст, видео-аватар, изображения и лонгрид из единого контекста",
    body: "Здравствуйте!\n\nОдна идея редко заканчивается одним текстом. Её приходится переносить между редактором, аудио, видео и визуальными инструментами.\n\nBOOK-CRAFT собирает эти шаги в единый narrative workflow. Вы задаёте тему и аудиторию, а затем развиваете материал в нужных форматах без потери контекста.\n\nДля команды это означает меньше ручного копирования, единый тон и понятную цепочку производства.\n\nОткройте первый проект и соберите свою контентную историю.\n\nBOOK-CRAFT · Narrative AI Studio"
  }
];

export default function MailingPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [topic, setTopic] = useState(demoMode ? "Запуск BOOK-CRAFT Narrative AI Studio" : "");
  const [audience, setAudience] = useState(demoMode ? "Авторы, маркетологи и небольшие креативные команды" : "");
  const [goal, setGoal] = useState("Заинтересовать");
  const [tone, setTone] = useState(demoMode ? "Премиальный" : "Деловой");
  const [result, setResult] = useState(demoMode ? demoResults[0] : null);
  const [phase, setPhase] = useState(demoMode ? "ready" : "idle");
  const [run, setRun] = useState(0);

  function generateDemo() {
    if (phase === "processing") return;

    const safeTopic = topic.trim() || "новый продукт";
    const safeAudience = audience.trim() || "аудитория проекта";

    setPhase("processing");
    setResult(null);

    window.setTimeout(() => {
      if (demoMode) {
        const nextRun = run + 1;
        setRun(nextRun);
        setResult(demoResults[nextRun % demoResults.length]);
      } else {
        setResult({
          subject: `${safeTopic}: коротко о главном`,
          preheader: `${tone} формат для сегмента «${safeAudience}»`,
          body: `Здравствуйте!\n\nПодготовили материал по теме «${safeTopic}». Цель сообщения — ${goal.toLowerCase()}.\n\nDEMO: здесь будет результат реальной LLM после подключения серверного API.`
        });
      }

      setPhase("ready");
    }, 1400);
  }

  function reset() {
    setTopic("");
    setAudience("");
    setGoal("Заинтересовать");
    setTone("Деловой");
    setResult(null);
    setPhase("idle");
  }

  return (
    <WorkspacePage
      eyebrow="✦ MAILING"
      title="Рассылка"
      description="Рабочее место для подготовки письма: задаём тему, аудиторию, цель и тон — затем получаем редактируемый результат."
      status={demoMode ? "DZ PRO · INTERACTIVE DEMO" : "UI DEMO · LLM NEXT"}
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
            <SpectralAction variant="primary" onClick={generateDemo}>
              {phase === "processing" ? "✦ Генерирую…" : result ? "✦ Сгенерировать заново" : "✦ Сгенерировать DEMO"}
            </SpectralAction>
            <button className="secondaryButton" type="button" onClick={reset}>Очистить</button>
          </div>

          <div className={`demoRunStatus demoRunStatus--${phase}`}>
            <div className="demoRunStatus__line">
              <span>{phase === "processing" ? "LLM DEMO PROCESS" : phase === "ready" ? "RESULT READY" : "WAITING INPUT"}</span>
              <b>{phase === "processing" ? "анализ → структура → текст" : phase === "ready" ? "SUBJECT + PREHEADER + BODY ✓" : "заполните brief"}</b>
            </div>
            <i className="demoRunStatus__progress" />
          </div>
        </div>

        <div className={`outputEditor ${result ? "isReady" : ""} ${phase === "processing" ? "isProcessing" : ""}`}>
          <div className="outputEditor__head">
            <span>RESULT</span>
            <small>{phase === "processing" ? "GENERATING…" : result ? "DEMO READY" : "WAITING INPUT"}</small>
          </div>

          {phase === "processing" ? (
            <div className="demoSkeleton">
              <i /><i /><i /><i /><i />
            </div>
          ) : result ? (
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
