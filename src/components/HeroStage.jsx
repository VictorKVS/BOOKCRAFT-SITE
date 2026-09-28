export default function HeroStage() {
  return (
    <div className="heroStage heroStage--art" aria-label="Сценическая зона BOOK-CRAFT">
      <div className="heroStage__halo heroStage__halo--warm" aria-hidden="true" />
      <div className="heroStage__halo heroStage__halo--cyan" aria-hidden="true" />

      <div className="heroStage__tagline" aria-hidden="true">
        <span>ideas become</span>
        <strong>stories ✦</strong>
      </div>

      <div className="heroStage__portraitFrame">
        <img
          className="heroStage__characterAsset"
          src="/assets/bookcraft/hero/candidates/hero-main-v1.png"
          alt="Креативный AI-редактор BOOK-CRAFT"
        />
        <span className="heroStage__assetBadge">ART CANDIDATE · V1</span>
      </div>

      <div className="heroStage__laptop" aria-label="Ноутбук">
        <div className="heroStage__screen">
          <span className="screenDot screenDot--orange" />
          <span className="screenDot screenDot--cyan" />
          <span className="screenLine screenLine--one" />
          <span className="screenLine screenLine--two" />
          <span className="screenLine screenLine--three" />
          <strong>BOOK-CRAFT</strong>
        </div>
        <div className="heroStage__laptopBase" />
      </div>

      <div className="heroStage__desk" aria-hidden="true" />

      <div className="sceneProp sceneProp--script" aria-label="Сценарий">
        <small>SCENE 07</small>
        <b>Сценарий</b>
        <i /><i /><i />
      </div>

      <div className="sceneProp sceneProp--storyboard" aria-label="Storyboard">
        <small>STORYBOARD</small>
        <div className="storyFrames"><span>01</span><span>02</span><span>03</span></div>
      </div>

      <div className="sceneProp sceneProp--notebook" aria-label="Блокнот"><span /><span /><span /></div>
      <div className="sceneProp sceneProp--cup" aria-label="Чашка"><span className="cupSteam">~~~</span></div>
      <div className="sceneProp sceneProp--pencils" aria-label="Карандаши"><i /><i /><i /></div>

      <div className="sceneSpark sceneSpark--one" aria-hidden="true">✦</div>
      <div className="sceneSpark sceneSpark--two" aria-hidden="true">✦</div>
      <div className="sceneSpark sceneSpark--three" aria-hidden="true">·</div>
    </div>
  );
}
