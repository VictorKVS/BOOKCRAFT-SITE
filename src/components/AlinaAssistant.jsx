import {
  useEffect,
  useState,
} from "react";

import {
  fatherAnalyzeImage,
  fatherChat,
  getFatherHealth,
  getFatherRuntimeInfo,
} from "../services/fatherClient.js";

import {
  assetRegistry,
} from "../config/assetRegistry.js";

export default function AlinaAssistant() {
  const [open, setOpen] = useState(false);

  const [online, setOnline] =
    useState(false);

  const [runtimeInfo, setRuntimeInfo] =
    useState(null);

  const [message, setMessage] =
    useState("");

  const [answer, setAnswer] =
    useState(
      "Я Алина. FATHER подключается как мой локальный AI-контур.",
    );

  const [busy, setBusy] =
    useState(false);

  const [error, setError] =
    useState("");

  const [visionFile, setVisionFile] =
    useState(null);

  const [visionPrompt, setVisionPrompt] =
    useState(
      "Опиши изображение, видимый текст и важные детали. Не додумывай то, чего не видно.",
    );

  const alinaImage =
    assetRegistry.hero.characters[0];

  async function refreshHealth() {
    try {
      const [health, runtime] =
        await Promise.all([
          getFatherHealth(),
          getFatherRuntimeInfo(),
        ]);

      setOnline(
        health?.father === "ready"
      );

      setRuntimeInfo(runtime);
    } catch {
      setOnline(false);
      setRuntimeInfo(null);
    }
  }

  useEffect(() => {
    void refreshHealth();

    const timer = window.setInterval(
      refreshHealth,
      10000,
    );

    return () =>
      window.clearInterval(timer);
  }, []);

  async function sendMessage() {
    const value = message.trim();

    if (!value || busy) {
      return;
    }

    setBusy(true);
    setError("");

    try {
      const result =
        await fatherChat(value);

      setAnswer(
        result.answer ||
        "Ответ от FATHER пуст.",
      );

      setMessage("");
      setOnline(true);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Не удалось связаться с FATHER.",
      );

      setOnline(false);
    } finally {
      setBusy(false);
    }
  }

  async function analyzeImage() {
    if (!visionFile || busy) {
      return;
    }

    setBusy(true);
    setError("");

    try {
      const result =
        await fatherAnalyzeImage(
          visionFile,
          visionPrompt,
        );

      setAnswer(
        result.answer ||
        "Анализ завершён без текста.",
      );

      setOnline(true);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Vision-анализ не выполнен.",
      );

      setOnline(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className={`alinaDockButton ${
          online
            ? "is-online"
            : "is-offline"
        }`}
        onClick={() =>
          setOpen((value) => !value)
        }
        aria-expanded={open}
        aria-label="Открыть Алину"
      >
        <span className="alinaDockAvatar">
          <img
            src={alinaImage}
            alt=""
          />
        </span>

        <span className="alinaDockButtonText">
          <strong>АЛИНА</strong>
          <small>
            {online
              ? "FATHER ONLINE"
              : "FATHER OFFLINE"}
          </small>
        </span>

        <span
          className="alinaDockStatus"
          aria-hidden="true"
        />
      </button>

      {open && (
        <aside
          className="alinaDock"
          aria-label="ALINA AI Assistant"
        >
          <header className="alinaDockHeader">
            <div className="alinaDockIdentity">
              <img
                src={alinaImage}
                alt="Алина"
              />

              <div>
                <strong>
                  Алина
                </strong>

                <span>
                  BOOKCRAFT · FATHER AI
                </span>
              </div>
            </div>

            <button
              type="button"
              className="alinaDockClose"
              onClick={() =>
                setOpen(false)
              }
              aria-label="Закрыть"
            >
              ×
            </button>
          </header>

          <div className="alinaDockRuntime">
            <span
              className={
                online
                  ? "runtimeDot online"
                  : "runtimeDot offline"
              }
            />

            <strong>
              {online
                ? "FATHER CORE ONLINE"
                : "FATHER CORE OFFLINE"}
            </strong>

            <button
              type="button"
              onClick={() =>
                void refreshHealth()
              }
            >
              проверить
            </button>
          </div>

          {runtimeInfo && (
            <div className="alinaRuntimeMeta">
              <span>
                <small>MODEL</small>
                <strong>{runtimeInfo.model}</strong>
              </span>

              <span>
                <small>ENGINE</small>
                <strong>{runtimeInfo.provider}</strong>
              </span>

              <span>
                <small>MODE</small>
                <strong>{runtimeInfo.mode}</strong>
              </span>
            </div>
          )}

          <div className="alinaDockAnswer">
            {answer}
          </div>

          {error && (
            <div className="alinaDockError">
              {error}
            </div>
          )}

          <div className="alinaDockChat">
            <textarea
              rows={4}
              value={message}
              placeholder="Напиши Алине..."
              onChange={(event) =>
                setMessage(
                  event.target.value,
                )
              }
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();
                  void sendMessage();
                }
              }}
            />

            <button
              type="button"
              disabled={
                busy ||
                !message.trim()
              }
              onClick={() =>
                void sendMessage()
              }
            >
              {busy
                ? "Думаю..."
                : "Отправить →"}
            </button>
          </div>

          <details className="alinaDockVision">
            <summary>
              Vision · анализ изображения
            </summary>

            <input
              type="file"
              accept="image/*"
              onChange={(event) =>
                setVisionFile(
                  event.target.files?.[0] ??
                    null,
                )
              }
            />

            <textarea
              rows={3}
              value={visionPrompt}
              onChange={(event) =>
                setVisionPrompt(
                  event.target.value,
                )
              }
            />

            <button
              type="button"
              disabled={
                busy ||
                !visionFile
              }
              onClick={() =>
                void analyzeImage()
              }
            >
              Анализировать
            </button>
          </details>
        </aside>
      )}
    </>
  );
}
