import { useEffect, useMemo, useState } from "react";
import heroVisualConfig from "../config/heroVisualConfig";

function enabledItems(items = []) {
  return items.filter((item) => item?.enabled !== false && item?.asset);
}

export default function HeroStage() {
  const characters = useMemo(
    () => enabledItems(heroVisualConfig.layers.character?.items),
    []
  );

  const books = useMemo(
    () => enabledItems(heroVisualConfig.layers.books?.items),
    []
  );

  const laptops = useMemo(
    () => enabledItems(heroVisualConfig.layers.laptop?.items),
    []
  );

  const scenes = heroVisualConfig.rotation?.scenes ?? [];
  const [sceneIndex, setSceneIndex] = useState(0);

  useEffect(() => {
    if (!heroVisualConfig.rotation?.enabled || scenes.length <= 1) {
      return undefined;
    }

    const mediaQuery = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    );

    if (mediaQuery.matches) {
      return undefined;
    }

    const intervalMs = Math.max(
      Number(heroVisualConfig.rotation?.intervalMs) || 10000,
      1000
    );

    const timer = window.setInterval(() => {
      setSceneIndex((current) => (current + 1) % scenes.length);
    }, intervalMs);

    return () => window.clearInterval(timer);
  }, [scenes.length]);

  const scene = scenes[sceneIndex] ?? {
    character: 0,
    books: 0,
    laptop: 0,
  };

  return (
    <div
      className="heroStage heroStage--layered heroStage--rotating"
      aria-label="Сценическая зона BOOK-CRAFT"
      data-scene={sceneIndex + 1}
    >
      <div
        className="heroStage__halo heroStage__halo--warm"
        aria-hidden="true"
      />
      <div
        className="heroStage__halo heroStage__halo--cyan"
        aria-hidden="true"
      />

      <div
        className="heroStage__rotationLayer heroStage__rotationLayer--character"
        data-layer="character"
      >
        {characters.map((item, index) => (
          <img
            key={item.id}
            className={`heroStage__characterAsset heroStage__rotatingAsset ${index === scene.character ? "is-active" : ""}`}
            src={item.asset}
            alt={
              index === scene.character
                ? "Креативный AI-редактор BOOK-CRAFT"
                : ""
            }
            aria-hidden={index === scene.character ? undefined : "true"}
          />
        ))}
      </div>

      <div
        className="heroStage__rotationLayer heroStage__rotationLayer--books"
        data-layer="books"
      >
        {books.map((item, index) => (
          <img
            key={item.id}
            className={`heroStage__booksLayer heroStage__rotatingAsset ${index === scene.books ? "is-active" : ""}`}
            src={item.asset}
            alt=""
            aria-hidden="true"
          />
        ))}
      </div>

      <div
        className="heroStage__rotationLayer heroStage__rotationLayer--laptop"
        data-layer="laptop"
      >
        {laptops.map((item, index) => (
          <img
            key={item.id}
            className={`heroStage__laptopLayer heroStage__rotatingAsset ${index === scene.laptop ? "is-active" : ""}`}
            src={item.asset}
            alt=""
            aria-hidden="true"
          />
        ))}
      </div>
    </div>
  );
}
