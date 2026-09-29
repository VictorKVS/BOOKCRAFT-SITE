export default function HeroStage() {
  return (
    <div className="heroStage heroStage--layered" aria-label="Сценическая зона BOOK-CRAFT">
      <div className="heroStage__halo heroStage__halo--warm" aria-hidden="true" />
      <div className="heroStage__halo heroStage__halo--cyan" aria-hidden="true" />

      <div className="heroStage__portraitFrame" data-layer="character">
        <img
          className="heroStage__characterAsset"
          src="/assets/bookcraft/hero/character/active/alina-v1.png"
          alt="Креативный AI-редактор BOOK-CRAFT"
        />
      </div>

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
