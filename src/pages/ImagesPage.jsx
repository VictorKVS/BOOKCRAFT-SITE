import { useState } from "react";
import WorkspacePage from "../components/WorkspacePage.jsx";
import SpectralAction from "../components/SpectralAction.jsx";

export default function ImagesPage() {
  const [prompt, setPrompt] = useState("");
  const [generated, setGenerated] = useState(false);

  return (
    <WorkspacePage
      eyebrow="✦ IMAGE ENGINE"
      title="Генерация изображений"
      description="Черновой UI-контракт для существующей локальной ComfyUI-интеграции. Сейчас без реальной генерации."
      status="UI DEMO"
    >
      <label className="field">
        <span>Промпт</span>
        <textarea
          rows="6"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Опишите изображение..."
        />
      </label>

      <SpectralAction variant="primary" onClick={() => setGenerated(true)}>
        Создать DEMO-слоты
      </SpectralAction>

      <div className={`imageGrid imageGrid--skeleton ${generated ? "isReady" : ""}`}>
        {[1,2,3,4].map((n) => (
          <div key={n}>
            <span>{generated ? `VARIANT ${n}` : "IMAGE SLOT"}</span>
          </div>
        ))}
      </div>
    </WorkspacePage>
  );
}
