import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

const ratios = ["16:9","1:1","4:5","9:16"];

export default function ImagesPage() {
  const [searchParams] = useSearchParams();
  const demoMode = searchParams.get("demo") === "1";

  const [prompt, setPrompt] = useState(demoMode ? "Кинематографичная обложка: ночная библиотека, золотой свет, открытая книга превращается в фантастический город, premium editorial look" : "");
  const [style, setStyle] = useState("Cinematic");
  const [ratio, setRatio] = useState("16:9");
  const [generated, setGenerated] = useState(demoMode);
  const [selected, setSelected] = useState(demoMode ? 2 : 0);

  function generate() {
    setGenerated(true);
    setSelected(1);
  }

  return (
    <WorkspacePage
      eyebrow="✦ IMAGE ENGINE"
      title="Генерация изображений"
      description="Бонусный визуальный модуль: промпт, стиль, формат, варианты и выбор результата."
      status={demoMode ? "DZ PRO · BONUS SCREENSHOT" : "UI DEMO · COMFYUI NEXT"}
    >
      <div className="moduleHero moduleHero--images">
        <div><small>PROMPT</small><b>Описание сцены</b></div>
        <span>→</span>
        <div><small>MODEL</small><b>Image engine</b></div>
        <span>→</span>
        <div><small>SELECT</small><b>Лучший вариант</b></div>
      </div>

      <label className="field">
        <span>Промпт</span>
        <textarea rows="6" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Опишите персонажа, сцену, свет, композицию..." />
      </label>

      <div className="imageControlRow">
        <label className="field">
          <span>Стиль</span>
          <select value={style} onChange={(e) => setStyle(e.target.value)}>
            <option>Cinematic</option>
            <option>Editorial</option>
            <option>Illustration</option>
            <option>Technical</option>
          </select>
        </label>

        <div className="ratioControl">
          <span>Формат</span>
          <div>{ratios.map((item) => <button key={item} type="button" className={ratio === item ? "active" : ""} onClick={() => setRatio(item)}>{item}</button>)}</div>
        </div>

        <SpectralAction variant="primary" onClick={generate}>✦ Создать DEMO-варианты</SpectralAction>
      </div>

      <div className={`imageGrid imageGrid--studio ${generated ? "isReady" : ""}`}>
        {[1,2,3,4].map((n) => (
          <button key={n} type="button" className={selected === n ? "selected" : ""} onClick={() => generated && setSelected(n)}>
            <div className={`generatedArt generatedArt--${n}`} />
            <span>{generated ? `VARIANT 0${n}` : "IMAGE SLOT"}</span>
            <small>{generated ? `${style} · ${ratio}` : "waiting"}</small>
          </button>
        ))}
      </div>

      {selected > 0 && <div className="selectionSummary isReady"><small>SELECTED</small><b>Variant 0{selected}</b><span>Готов к использованию в контентном пайплайне.</span></div>}
    </WorkspacePage>
  );
}
