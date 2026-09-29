export default function HeroStage() {
  return (
    <div className="heroStage heroStage--layered" aria-label="Сценическая зона BOOK-CRAFT">
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
