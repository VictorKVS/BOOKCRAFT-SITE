const UI = {
  kicker: "07 \u00b7 WEB PROTOTYPE",
  title: "\u041f\u0440\u043e\u0442\u043e\u0442\u0438\u043f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b",
  description:
    "\u0421\u043e\u0431\u0438\u0440\u0430\u0435\u043c \u0432\u044b\u043f\u0443\u0441\u043a "
    + "\u0443\u0436\u0435 \u0441\u0435\u0439\u0447\u0430\u0441. "
    + "\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f "
    + "\u043f\u043e\u043a\u0430 \u0437\u0430\u043c\u0435\u043d\u0435\u043d\u044b "
    + "\u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u043c\u0438 "
    + "\u0437\u0430\u0433\u043b\u0443\u0448\u043a\u0430\u043c\u0438.",
  build:
    "\u2716 \u0421\u043e\u0431\u0440\u0430\u0442\u044c "
    + "\u043f\u0440\u043e\u0442\u043e\u0442\u0438\u043f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b",
  rebuild:
    "\u21bb \u041f\u0435\u0440\u0435\u0441\u043e\u0431\u0440\u0430\u0442\u044c",
  episode: "EPISODE 01",
  project: "BOOKCRAFT ORIGINAL",
  genre: "TECH THRILLER",
  placeholder: "IMAGE SLOT",
  visuals: "VISUALS \u00b7 PLACEHOLDERS",
  story: "\u0420\u0430\u0441\u0441\u043a\u0430\u0437",
  pending:
    "\u0422\u0435\u043a\u0441\u0442 \u0441\u0435\u0440\u0438\u0438 "
    + "\u0435\u0449\u0451 \u043d\u0435 \u0441\u043e\u0437\u0434\u0430\u043d.",
};


function panelText(panel, index) {
  if (typeof panel === "string") {
    return panel;
  }

  if (!panel) {
    return `PANEL ${String(index + 1).padStart(2, "0")}`;
  }

  return (
    panel.text
    || panel.content
    || panel.description
    || panel.scene
    || panel.prompt
    || JSON.stringify(panel)
  );
}


function shortText(text, max = 230) {
  if (!text) return "";

  const clean = String(text)
    .replace(/\s+/g, " ")
    .trim();

  return clean.length > max
    ? `${clean.slice(0, max)}...`
    : clean;
}


export default function StoryWebPrototype({
  ready,
  story,
  panels,
  onBuild,
}) {
  const visiblePanels = Array.isArray(panels)
    ? panels.slice(0, 6)
    : [];

  return (
    <section className="storyWebPrototype storyGlass">
      <div className="storyWebPrototypeHeader">
        <div>
          <small>{UI.kicker}</small>
          <h2>{UI.title}</h2>
          <p>{UI.description}</p>
        </div>

        <button
          type="button"
          className="storyPrimary"
          onClick={onBuild}
        >
          {ready
            ? UI.rebuild
            : UI.build}
        </button>
      </div>

      {!ready ? (
        <div className="storyWebPrototypeEmpty">
          <div className="storyWebSkeletonHero" />

          <div className="storyWebSkeletonGrid">
            {Array.from({ length: 6 }).map(
              (_, index) => (
                <div
                  key={index}
                  className="storyWebSkeletonCard"
                >
                  <span>
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
              )
            )}
          </div>
        </div>
      ) : (
        <article className="storyWebPage">
          <header className="storyWebPageTop">
            <strong>{UI.project}</strong>

            <nav>
              <span>{UI.genre}</span>
              <span>{UI.episode}</span>
            </nav>
          </header>

          <section className="storyWebHero">
            <div>
              <small>{UI.episode}</small>

              <h1>
                {"\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 "
                  + "\u0430\u0432\u0442\u043e\u043d\u043e\u043c\u043d\u044b\u0439 "
                  + "\u0443\u0437\u0435\u043b"}
              </h1>

              <p>
                {
                  "\u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0439 "
                  + "\u0442\u0440\u0438\u043b\u043b\u0435\u0440 "
                  + "\u043e \u0434\u043e\u0432\u0435\u0440\u0438\u0438, "
                  + "\u0434\u0430\u043d\u043d\u044b\u0445 "
                  + "\u0438 \u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0435\u043c "
                  + "\u0440\u0430\u0431\u043e\u0442\u0430\u044e\u0449\u0435\u043c "
                  + "\u0443\u0437\u043b\u0435."
                }
              </p>
            </div>

            <div className="storyWebHeroVisual">
              <span>01</span>

              <small>
                {UI.placeholder}
              </small>
            </div>
          </section>

          <div className="storyWebStatus">
            <span>{UI.visuals}</span>

            <span>
              FATHER STORY FACTORY
            </span>
          </div>

          <section className="storyWebPanels">
            {visiblePanels.map(
              (panel, index) => {
                const text =
                  panelText(panel, index);

                return (
                  <article
                    className="storyWebPanel"
                    key={index}
                  >
                    <div className="storyWebPanelVisual">
                      <strong>
                        {String(index + 1).padStart(2, "0")}
                      </strong>

                      <small>
                        {UI.placeholder}
                      </small>
                    </div>

                    <div className="storyWebPanelText">
                      <small>
                        PANEL{" "}
                        {String(index + 1).padStart(2, "0")}
                      </small>

                      <p>
                        {shortText(text)}
                      </p>
                    </div>
                  </article>
                );
              }
            )}
          </section>

          <section className="storyWebStory">
            <div className="storyWebStoryHeading">
              <small>
                NARRATIVE
              </small>

              <h2>{UI.story}</h2>
            </div>

            <p>
              {story
                ? shortText(story, 1500)
                : UI.pending}
            </p>
          </section>

          <footer className="storyWebFooter">
            <span>
              BOOKCRAFT \u00b7 ALINA
            </span>

            <span>
              FATHER AI PRODUCTION
            </span>
          </footer>
        </article>
      )}
    </section>
  );
}
