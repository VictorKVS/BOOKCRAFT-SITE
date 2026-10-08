import {
  storyCharacters,
} from "../data/storyCharacters.js";


const UI = {
  kicker: "\u0030\u0033 \u00b7 CHARACTERS",
  title: "\u0413\u0435\u0440\u043e\u0438",
  subtitle:
    "\u0421\u043d\u0430\u0447\u0430 \u0444\u0438\u043a\u0441\u0438\u0440\u0443\u0435\u043c "
    + "\u043a\u0430\u043d\u043e\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0439 "
    + "\u043e\u0431\u0440\u0430\u0437 \u043a\u0430\u0436\u0434\u043e\u0433\u043e "
    + "\u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0430.",
  profile: "\u041f\u0440\u043e\u0444\u0438\u043b\u044c",
  visual: "\u0412\u0438\u0437\u0443\u0430\u043b\u044c\u043d\u044b\u0439 \u043a\u0430\u043d\u043e\u043d",
  expressions: "\u042d\u043c\u043e\u0446\u0438\u0438",
  outfits: "\u041e\u0431\u0440\u0430\u0437\u044b",
  pending: "\u041d\u0435 \u0443\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043d",
  approved: "\u0423\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043d",
  approve: "\u0423\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c",
  revoke: "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c",
  approveAll:
    "\u2713 \u0423\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c "
    + "\u0432\u0441\u0435\u0445 \u0433\u0435\u0440\u043e\u0435\u0432",
  locked:
    "\u041a\u0430\u043d\u043e\u043d \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u0436\u0435\u0439 "
    + "\u0437\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043d.",
  next:
    "\u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0448\u0430\u0433: "
    + "Character Pack \u2192 ComfyUI \u2192 Face/Body Lock",
};


function CharacterCard({
  character,
  approved,
  onToggle,
}) {
  return (
    <article
      className={
        "storyCharacterCard"
        + (approved
          ? " isApproved"
          : "")
      }
    >
      <div className="storyCharacterHero">
        <div className="storyCharacterPlaceholder">
          <span>
            {character.name.slice(0, 1)}
          </span>
        </div>

        <div className="storyCharacterIdentity">
          <small>{character.id}</small>
          <h3>{character.name}</h3>
          <p>{character.role}</p>

          <span
            className={
              "storyCharacterStatus "
              + (approved
                ? "approved"
                : "pending")
            }
          >
            {approved
              ? UI.approved
              : UI.pending}
          </span>
        </div>
      </div>

      <div className="storyCharacterInfo">
        <div>
          <small>{UI.profile}</small>

          <p>
            <strong>
              {character.age || "AI"}
            </strong>
          </p>

          <p>{character.profession}</p>

          <p>
            {character.personality.join(
              " \u00b7 "
            )}
          </p>
        </div>

        <div>
          <small>{UI.visual}</small>

          <p>
            {character.visual.canonicalLook}
          </p>
        </div>

        <div>
          <small>{UI.expressions}</small>

          <p>
            {character.expressions.join(
              " \u00b7 "
            )}
          </p>
        </div>

        <div>
          <small>{UI.outfits}</small>

          <p>
            {character.visual.outfits.join(
              " \u00b7 "
            )}
          </p>
        </div>
      </div>

      <div className="storyCharacterPalette">
        {character.visual.palette.map(
          (color) => (
            <i
              key={color}
              style={{
                background: color,
              }}
              title={color}
            />
          )
        )}
      </div>

      <button
        type="button"
        className={
          approved
            ? "storyCharacterButton approved"
            : "storyCharacterButton"
        }
        onClick={() =>
          onToggle(character.id)
        }
      >
        {approved
          ? UI.revoke
          : UI.approve}
      </button>
    </article>
  );
}


export default function StoryCharacterStage({
  approvedIds,
  onToggle,
  onApproveAll,
}) {
  const allApproved =
    storyCharacters.every(
      (character) =>
        approvedIds.includes(
          character.id
        )
    );

  return (
    <section
      id="story-characters"
      className="storyCharacters storyGlass"
    >
      <div className="storyCharacterHeader">
        <div>
          <small>{UI.kicker}</small>
          <h2>{UI.title}</h2>
          <p>{UI.subtitle}</p>
        </div>

        <div
          className={
            "storyCharacterGate "
            + (allApproved
              ? "ready"
              : "")
          }
        >
          <span>
            {approvedIds.length}
            /
            {storyCharacters.length}
          </span>

          <small>
            CHARACTER LOCK
          </small>
        </div>
      </div>

      <div className="storyCharacterGrid">
        {storyCharacters.map(
          (character) => (
            <CharacterCard
              key={character.id}
              character={character}
              approved={
                approvedIds.includes(
                  character.id
                )
              }
              onToggle={onToggle}
            />
          )
        )}
      </div>

      <div className="storyCharacterFooter">
        <div>
          <strong>
            {allApproved
              ? UI.locked
              : UI.next}
          </strong>

          <p>
            FACE \u2192 BODY \u2192 POSES
            \u2192 EXPRESSIONS \u2192 OUTFITS
            \u2192 PROPS
          </p>
        </div>

        <button
          type="button"
          className="storyPrimary"
          onClick={onApproveAll}
          disabled={allApproved}
        >
          {allApproved
            ? UI.approved
            : UI.approveAll}
        </button>
      </div>
    </section>
  );
}
