export default function HeroStage() {
  return (
    <div className="heroStage heroStage--layered" aria-label="Сценическая зона BOOK-CRAFT">
      <img
        className="heroStage__backgroundAsset"
        src="/assets/bookcraft/backgrounds/hero-studio-ru-v1.png"
        alt=""
        aria-hidden="true"
      />

      <div className="heroStage__backgroundShade" aria-hidden="true" />
      <div className="heroStage__halo heroStage__halo--warm" aria-hidden="true" />
      <div className="heroStage__halo heroStage__halo--cyan" aria-hidden="true" />

      <div className="heroStage__portraitFrame">
        <img
          className="heroStage__characterAsset"
          src="/assets/bookcraft/hero/candidates/hero-main-v1.png"
          alt="Креативный AI-редактор BOOK-CRAFT"
        />
      </div>
    </div>
  );
}
