import { useEffect, useMemo, useState } from "react";
import {
  FATHER_URL,
  fatherChat,
  fatherChatStream,
  fatherSpeak,
  getFatherHealth,
  getFatherRuntimeInfo,
} from "../services/fatherClient.js";
import StoryWebPrototype from "../components/StoryWebPrototype.jsx";
import "../styles/story-studio.css";

const DEMO_IDEA = `Название: «Последний автономный узел».

2041 год. После глобального сбоя облачных сервисов инженер Андрей приезжает в заброшенный исследовательский центр, чтобы отключить последний автономный вычислительный узел.

В центре продолжает работать локальный ИИ Лира. Она утверждает, что сбой произошёл не случайно, а отключение узла уничтожит единственные сохранившиеся доказательства.

По аварийному радиоканалу Марина, специалист по безопасности, требует немедленно выполнить процедуру отключения.

Жанр: технотриллер / научная фантастика / детектив.
Формат: короткий рассказ — первая серия.
Тон: серьёзный, технологически правдоподобный, напряжённый.

Главный конфликт:
Андрей должен понять, является ли предупреждение Лиры правдой, ошибкой повреждённой модели или попыткой манипуляции.`;

const fallbackPanels = [
  "Андрей прибывает к заброшенному исследовательскому центру.",
  "В тёмном машинном зале неожиданно включается терминал Лиры.",
  "Лира показывает фрагмент журнала перед глобальным сбоем.",
  "Марина выходит на аварийную связь и требует отключить узел.",
  "Андрей обнаруживает несовпадение временных меток.",
  "На экране появляется неизвестный внешний запрос к системе.",
];

function ResultPanel({
  title,
  kicker,
  value,
  empty,
  children,
  loading = false,
  loadingText = "ALINA WORKING",
  elapsed = 0,
}) {
  return (
    <section className="storyGlass storyResult">
      <div className="storySectionHead">
        <div>
          <small>{kicker}</small>
          <h2>{title}</h2>
        </div>
        <span className={value ? "storyDot ready" : "storyDot"} />
      </div>

      {value ? children : loading ? (
        <div className="storyWorkingPanel">
          <div className="storyWorkingCore">
            <span className="storyWorkingPulse" />

            <div>
              <small>FATHER RUNTIME</small>
              <strong>{loadingText}</strong>
            </div>

            <b>
              {String(Math.floor(elapsed / 60)).padStart(2, "0")}:
              {String(elapsed % 60).padStart(2, "0")}
            </b>
          </div>

          <div className="storyWorkingTrack">
            <i />
          </div>

          <div className="storyWorkingSteps">
            <span>ALINA</span>
            <em>→</em>
            <span>FATHER</span>
            <em>→</em>
            <span>OLLAMA</span>
            <em>→</em>
            <span>MODEL</span>
          </div>

          <p>
            {
              "\u0417\u0430\u043f\u0440\u043e\u0441 "
              + "\u043f\u0440\u0438\u043d\u044f\u0442. "
              + "\u0410\u043b\u0438\u043d\u0430 "
              + "\u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0435\u0442 "
              + "\u0442\u0435\u043a\u0443\u0449\u0438\u0439 "
              + "\u044d\u0442\u0430\u043f."
            }
          </p>
        </div>
      ) : (
        <div className="storyEmpty">
          <span>✦</span>
          <p>{empty}</p>
        </div>
      )}
    </section>
  );
}

export default function StoryStudioPage() {
  const [idea, setIdea] = useState(DEMO_IDEA);
  const [analytics, setAnalytics] = useState("");
  const [story, setStory] = useState("");
  const [voiceScript, setVoiceScript] = useState("");
  const [comic, setComic] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [sheetReady, setSheetReady] = useState(false);
  const [prototypeReady, setPrototypeReady] = useState(false);

  const [busy, setBusy] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const [online, setOnline] = useState(false);
  const [runtime, setRuntime] = useState(null);

  useEffect(() => {
    if (!busy) {
      setElapsed(0);
      return undefined;
    }

    setElapsed(0);

    const timer = setInterval(() => {
      setElapsed((value) => value + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [busy]);

  useEffect(() => {
    let alive = true;

    async function loadRuntime() {
      try {
        const [health, info] = await Promise.all([
          getFatherHealth(),
          getFatherRuntimeInfo(),
        ]);

        if (!alive) return;

        setOnline(health?.father === "ready");
        setRuntime(info);
      } catch {
        if (!alive) return;
        setOnline(false);
      }
    }

    loadRuntime();
    const timer = setInterval(loadRuntime, 10000);

    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  async function run(name, prompt, setter) {
    setBusy(name);
    setError("");
    setter("");

    const profile =
      name === "story"
        ? "pro"
        : "fast";

    try {
      await fatherChatStream(
        prompt,
        {
          provider: "auto",
          profile,

          onToken: (_, fullText) => {
            setter(fullText);
          },

          onMeta: (meta) => {
            setRuntime((current) => ({
              ...(current || {}),
              provider:
                meta.provider
                || current?.provider,
              model:
                meta.model
                || current?.model,
              mode:
                meta.mode
                || current?.mode,
              ttft_ms:
                meta.ttft_ms,
              total_ms:
                meta.total_ms,
            }));
          },

          onFallback: () => {
            setError(
              "GigaChat unavailable — "
              + "FATHER switched to local Qwen."
            );
          },
        },
      );
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "FATHER request failed"
      );
    } finally {
      setBusy("");
    }
  }

  async function analyzeIdea() {
    await run(
      "analytics",
      `Ты — ALINA, сценарный аналитик BOOKCRAFT Story Factory.

Проанализируй идею будущей первой серии.

${idea}

Нужен производственный анализ, а не литературный рассказ.

Структура ответа:

1. СИЛЬНЫЙ ХУК
2. ЦЕЛЕВАЯ АУДИТОРИЯ
3. FORMAT / TREND FIT
4. ЧТО РАБОТАЕТ
5. РИСКИ И КЛИШЕ
6. ЧТО СТОИТ УСИЛИТЬ
7. КАК ОТКРЫТЬ ПЕРВУЮ СЕРИЮ
8. ПОТЕНЦИАЛ СЕРИЙНОСТИ
9. РЕКОМЕНДАЦИЯ ALINA

Не выдумывай актуальную интернет-статистику.
Если для подтверждения тренда нужны свежие веб-данные,
явно напиши: WEB VALIDATION REQUIRED.`,
      setAnalytics
    );
  }

  async function createStory() {
    await run(
      "story",
      `Ты — ALINA, сценарист BOOKCRAFT Story Factory.

ИСХОДНАЯ ИДЕЯ:
${idea}

УТВЕРЖДЁННАЯ АНАЛИТИКА:
${analytics || "Аналитика пока не добавлена."}

Создай первую короткую серию как законченный рассказ.

Требования:
- технотриллер;
- технологическая правдоподобность;
- Андрей принимает решения из наблюдаемых фактов;
- Лира не должна выглядеть всемогущей;
- Марина должна оставаться неоднозначной;
- не раскрывай всю тайну;
- нужен поворот ближе к финалу;
- финал должен открывать вторую серию;
- ориентир 900–1300 слов;
- русский язык.

Сначала название серии, затем сам рассказ.`,
      setStory
    );
  }

  async function createVoiceScript() {
    if (!story) return;

    await run(
      "voice",
      `Ты — ALINA, режиссёр аудиоверсии BOOKCRAFT.

Разложи рассказ на аудиосценарий.

РАССКАЗ:
${story}

Используй роли:
NARRATOR
ANDREY
LIRA
MARINA

Для каждого блока указывай:
РОЛЬ
ЭМОЦИЯ
ТЕМП
ТЕКСТ
ПАУЗА

Не переписывай сюжет и не добавляй новые события.`,
      setVoiceScript
    );
  }

  async function synthesizeAudio() {
    if (!story) return;

    setBusy("audio");
    setError("");

    try {
      const preview = story.slice(0, 4500);
      const result = await fatherSpeak(preview);

      if (result?.url) {
        setAudioUrl(result.url);
      }
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "TTS failed"
      );
    } finally {
      setBusy("");
    }
  }

  async function createComic() {
    if (!story) return;

    await run(
      "comic",
      `Ты — ALINA, режиссёр комикса BOOKCRAFT.

Разложи рассказ на 8 последовательных кадров комикса.

РАССКАЗ:
${story}

Для каждого кадра дай:

PANEL 01
SCENE:
VISUAL:
CHARACTERS:
ACTION:
CAMERA:
DIALOGUE:
IMAGE PROMPT:

И так до PANEL 08.

Сохраняй внешний вид персонажей и локаций между кадрами.
Не добавляй событий, которых нет в рассказе.`,
      setComic
    );
  }

  const panels = useMemo(() => {
    if (!comic) return fallbackPanels;

    const chunks = comic
      .split(/(?=PANEL\s+\d+)/i)
      .map((item) => item.trim())
      .filter(Boolean);

    if (!chunks.length) return fallbackPanels;

    return Array.from(
      { length: 6 },
      (_, index) => chunks[index] || fallbackPanels[index]
    );
  }, [comic]);

  const audioSrc = audioUrl
    ? `${FATHER_URL}${audioUrl}`
    : "";

  return (
    <main className="storyFactory">
      <div className="storyAura storyAuraA" />
      <div className="storyAura storyAuraB" />

      <section className="storyHero">
        <div className="storyHeroCopy">
          <div className="storyEyebrow">
            BOOKCRAFT · ALINA STORY ENGINE
          </div>

          <h1>
            Story
            <span> Factory</span>
          </h1>

          <p>
            Одна идея превращается в аналитику, рассказ,
            аудиоверсию, комикс и готовую страницу серии.
          </p>

          <div className="storyHeroMeta">
            <span>TECH THRILLER</span>
            <span>EPISODE 01</span>
            <span>7–10 MIN</span>
            <span>LOCAL AI</span>
          </div>
        </div>

        <div className="storyAlina">
          <div className="storyOrbit orbitOne" />
          <div className="storyOrbit orbitTwo" />

          <img
            src="/assets/bookcraft/hero/characters/alina/alina-01.png"
            alt="ALINA"
          />

          <div className="storyRuntimeCard">
            <div className="storyRuntimeTitle">
              <span className={online ? "runtimeLed on" : "runtimeLed"} />
              {online ? "FATHER ONLINE" : "FATHER OFFLINE"}
            </div>

            <strong>ALINA</strong>

            <small>
              {runtime?.model || "runtime detection..."}
            </small>

            <small>
              {runtime?.provider || "—"} · {runtime?.mode || "—"}
            </small>
          </div>
        </div>
      </section>

      <section className="storyPipeline storyGlass">
        {[
          ["01", "IDEA", true],
          ["02", "ANALYTICS", Boolean(analytics)],
          ["03", "STORY", Boolean(story)],
          ["04", "VOICE", Boolean(voiceScript)],
          ["05", "COMIC", Boolean(comic)],
          ["06", "SHEET", sheetReady],
          ["07", "PAGE", prototypeReady],
        ].map(([number, label, ready]) => (
          <div
            className={ready ? "storyStage active" : "storyStage"}
            key={label}
          >
            <b>{number}</b>
            <span>{label}</span>
          </div>
        ))}

        <div className="storyStage disabled">
          <b>08</b>
          <span>VIDEO</span>
          <small>SOON</small>
        </div>
      </section>

      {error && (
        <div className="storyError">
          {error}
        </div>
      )}

      <section className="storyGrid storyGridTop">
        <article className="storyGlass storyIdea">
          <div className="storySectionHead">
            <div>
              <small>01 · SOURCE</small>
              <h2>Идея серии</h2>
            </div>

            <span className="storyChip">DEMO PROJECT</span>
          </div>

          <textarea
            value={idea}
            onChange={(event) => setIdea(event.target.value)}
          />

          <div className="storyParameters">
            <span>
              <small>GENRE</small>
              Tech Thriller
            </span>
            <span>
              <small>FORMAT</small>
              Short Story
            </span>
            <span>
              <small>SERIES</small>
              Episode 01
            </span>
          </div>

          <button
            className="storyPrimary"
            onClick={analyzeIdea}
            disabled={busy === "analytics" || !online}
          >
            {busy === "analytics"
              ? "ALINA анализирует..."
              : "✦ Анализировать с ALINA"}
          </button>
        </article>

        <article className="storyGlass storySignals">
          <div className="storySectionHead">
            <div>
              <small>MARKET SIGNAL</small>
              <h2>Creative radar</h2>
            </div>
          </div>

          <div className="radarCore">
            <div className="radarRing r1" />
            <div className="radarRing r2" />
            <div className="radarRing r3" />
            <div className="radarPoint p1" />
            <div className="radarPoint p2" />
            <div className="radarPoint p3" />
            <strong>STORY</strong>
          </div>

          <div className="storySignalRows">
            <div>
              <span>NARRATIVE FIT</span>
              <b>LOCAL ANALYSIS</b>
            </div>
            <div>
              <span>SERIAL POTENTIAL</span>
              <b>ALINA REVIEW</b>
            </div>
            <div>
              <span>LIVE TREND DATA</span>
              <b className="pending">WEB CHECK PENDING</b>
            </div>
          </div>
        </article>
      </section>

      <ResultPanel
        title="ALINA Analytics"
        kicker="02 · ANALYSIS"
        value={analytics}
        loading={busy === "analytics"}
        elapsed={elapsed}
        loadingText="ALINA ANALYZING"
        empty="Сначала отправьте идею на анализ."
      >
        <div className="storyTextResult">
          {analytics}
        </div>

        <div className="storyActions">
          <button
            className="storyPrimary"
            onClick={createStory}
            disabled={busy === "story"}
          >
            {busy === "story"
              ? "Создаю серию..."
              : "Утвердить → создать рассказ"}
          </button>
        </div>
      </ResultPanel>

      <ResultPanel
        title="Episode 01"
        kicker="03 · STORY"
        value={story}
        loading={busy === "story"}
        elapsed={elapsed}
        loadingText="ALINA WRITING EPISODE 01"
        empty="После утверждения аналитики здесь появится первая серия."
      >
        <textarea
          className="storyEditor"
          value={story}
          onChange={(event) => setStory(event.target.value)}
        />

        <div className="storyActions">
          <button
            onClick={createStory}
            disabled={busy === "story"}
          >
            ↻ Перегенерировать
          </button>

          <button
            className="storyPrimary"
            onClick={createVoiceScript}
            disabled={busy === "voice"}
          >
            🎙 Разложить на голос
          </button>

          <button
            className="storyPrimary alt"
            onClick={createComic}
            disabled={busy === "comic"}
          >
            ▦ Создать комикс
          </button>
        </div>
      </ResultPanel>

      <section className="storyGrid">
        <ResultPanel
          title="Audio Story"
          kicker="04 · VOICE"
          value={voiceScript}
          loading={busy === "voice"}
          elapsed={elapsed}
          loadingText="ALINA PREPARING VOICE SCRIPT"
          empty="ALINA разложит рассказ на роли, эмоции и реплики."
        >
          <div className="voiceWave" aria-hidden="true">
            {Array.from({ length: 36 }).map((_, index) => (
              <i
                key={index}
                style={{
                  height: `${18 + ((index * 17) % 52)}%`,
                }}
              />
            ))}
          </div>

          <div className="storyTextResult compact">
            {voiceScript}
          </div>

          <div className="storyActions">
            <button
              className="storyPrimary"
              onClick={synthesizeAudio}
              disabled={busy === "audio"}
            >
              {busy === "audio"
                ? "Синтез речи..."
                : "▶ Озвучить превью"}
            </button>
          </div>

          {audioSrc && (
            <audio
              className="storyAudio"
              controls
              src={audioSrc}
            />
          )}
        </ResultPanel>

        <ResultPanel
          title="Comic Director"
          kicker="05 · COMIC"
          value={comic}
          loading={busy === "comic"}
          elapsed={elapsed}
          loadingText="ALINA BUILDING COMIC PANELS"
          empty="ALINA превратит рассказ в последовательность кадров."
        >
          <div className="comicMiniGrid">
            {panels.map((panel, index) => (
              <article className="comicMini" key={index}>
                <span>
                  PANEL {String(index + 1).padStart(2, "0")}
                </span>
                <div className={`comicVisual v${index + 1}`}>
                  <b>{index + 1}</b>
                </div>
                <p>{panel.slice(0, 150)}</p>
              </article>
            ))}
          </div>

          <div className="storyActions">
            <button
              className="storyPrimary alt"
              onClick={() => setSheetReady(true)}
            >
              Собрать Comic Sheet
            </button>
          </div>
        </ResultPanel>
      </section>

      <ResultPanel
        title="Comic Sheet · Page 01"
        kicker="06 · LAYOUT"
        value={sheetReady}
        empty="После разбиения комикса соберите первый лист."
      >
        <div className="comicSheet">
          {panels.slice(0, 6).map((panel, index) => (
            <div
              className={`sheetPanel sheetPanel${index + 1}`}
              key={index}
            >
              <span>0{index + 1}</span>
              <strong>
                {panel
                  .replace(/\n/g, " ")
                  .slice(0, 90)}
              </strong>
            </div>
          ))}
        </div>

        <div className="storyActions">
          <button
            className="storyPrimary"
            onClick={() => setPrototypeReady(true)}
          >
            Создать прототип страницы
          </button>
        </div>
      </ResultPanel>

      <ResultPanel
        title="Interactive Story Page"
        kicker="07 · WEB PROTOTYPE"
        value={prototypeReady}
        empty="Comic Sheet станет основой интерактивной страницы серии."
      >
        <div className="storyPrototype">
          <div className="prototypeTop">
            <span>BOOKCRAFT ORIGINAL</span>
            <b>EPISODE 01</b>
          </div>

          <h3>Последний автономный узел</h3>

          <p>
            Андрей приехал отключить последнюю машину.
            Машина попросила его сначала посмотреть журнал.
          </p>

          <div className="prototypePanels">
            {panels.slice(0, 3).map((_, index) => (
              <div key={index}>
                <span>SCENE 0{index + 1}</span>
              </div>
            ))}
          </div>

          <button>Читать следующую сцену →</button>
        </div>
      </ResultPanel>

      <StoryWebPrototype
        ready={prototypeReady}
        story={story}
        panels={panels}
        onBuild={() =>
          setPrototypeReady(true)
        }
      />

      <section className="storyVideo storyGlass">
        <div>
          <small>08 · FUTURE PIPELINE</small>
          <h2>Video Production</h2>
          <p>
            Следующий производственный слой:
            storyboard → motion → avatar → sound → render.
          </p>
        </div>

        <button disabled>
          VIDEO · COMING LATER
        </button>
      </section>
    </main>
  );
}
