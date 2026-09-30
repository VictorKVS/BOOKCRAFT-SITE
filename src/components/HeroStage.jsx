import heroVisualConfig from "../config/heroVisualConfig";
import { useRotatingAsset } from "../hooks/useRotatingAsset";

export default function HeroStage() {
  const character = useRotatingAsset(
    heroVisualConfig.layers.character
  );

  const books = useRotatingAsset(
    heroVisualConfig.layers.books
  );

  return (
    <div
      className="heroStage heroStage--layered"
      aria-label="Сценическая зона BOOK-CRAFT"
    >
      {/* Atmospheric light */}
      <div
        className="heroStage__halo heroStage__halo--warm"
        aria-hidden="true"
      />

      <div
        className="heroStage__halo heroStage__halo--cyan"
        aria-hidden="true"
      />

      {/* LAYER 20 — ALINA */}
      <div
        className="heroStage__portraitFrame"
        data-layer="character"
        data-asset-id={character.item?.id ?? "fallback"}
      >
        <img
          key={character.item?.id ?? "fallback"}
          className="heroStage__characterAsset"
          src={
            character.item?.asset ??
            "/assets/bookcraft/hero/character/active/alina-v1.png"
          }
          alt="Креативный AI-редактор BOOK-CRAFT"
        />
      </div>

      {/* LAYER 30 — BOOKS + CUP */}
      {books.item && (
        <img
          key={books.item.id}
          className="heroStage__booksLayer"
          data-layer="books"
          data-asset-id={books.item.id}
          src={books.item.asset}
          alt=""
          aria-hidden="true"
        />
      )}

      {/* LAYER 40 — LAPTOP */}
      <img
        className="heroStage__laptopLayer"
        data-layer="laptop"
        src="/assets/bookcraft/hero/objects/laptop/laptop-angle-v1.png"
        alt=""
        aria-hidden="true"
      />
    </div>
  );
}