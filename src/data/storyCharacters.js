export const storyCharacters = [
  {
    id: "HERO_ANDREY_001",
    key: "andrey",
    name: "\u0410\u043d\u0434\u0440\u0435\u0439",
    role: "\u0413\u043b\u0430\u0432\u043d\u044b\u0439 \u0433\u0435\u0440\u043e\u0439",
    type: "human",

    age: "38\u201342",

    profession:
      "\u0418\u043d\u0436\u0435\u043d\u0435\u0440 / "
      + "\u0430\u043d\u0430\u043b\u0438\u0442\u0438\u043a "
      + "\u0418\u0422-\u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b",

    specialization: [
      "\u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430",
      "\u0441\u0438\u0441\u0442\u0435\u043c\u044b",
      "\u0441\u0435\u0442\u0438",
      "\u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0430",
      "\u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u044c",
    ],

    personality: [
      "\u0440\u0430\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u044b\u0439",
      "\u043e\u0441\u0442\u043e\u0440\u043e\u0436\u043d\u044b\u0439",
      "\u0441\u043a\u0435\u043f\u0442\u0438\u0447\u043d\u044b\u0439",
      "\u0443\u043f\u0440\u044f\u043c\u044b\u0439",
    ],

    objective:
      "\u0412\u044b\u043f\u043e\u043b\u043d\u0438\u0442\u044c "
      + "\u0437\u0430\u0434\u0430\u0447\u0443, "
      + "\u043d\u043e \u043f\u043e\u043d\u044f\u0442\u044c "
      + "\u0447\u0442\u043e \u043f\u0440\u043e\u0438\u0437\u043e\u0448\u043b\u043e "
      + "\u043d\u0430 \u0441\u0430\u043c\u043e\u043c \u0434\u0435\u043b\u0435.",

    visual: {
      gender: "male",
      build: "athletic-normal",
      hair: "dark short",
      eyes: "grey-blue",

      canonicalLook:
        "European male, late 30s to early 40s, "
        + "short dark hair, light stubble, "
        + "serious intelligent face, realistic.",

      outfits: [
        "field",
        "technical",
        "civilian",
        "formal",
      ],

      palette: [
        "#18212b",
        "#303841",
        "#575b5d",
        "#76503a",
      ],
    },

    expressions: [
      "neutral",
      "focus",
      "doubt",
      "tension",
      "determination",
      "fatigue",
    ],

    poses: [
      "front",
      "three-quarter",
      "profile",
      "walking",
      "terminal-work",
      "inspection",
      "kneeling",
      "turning-back",
    ],

    props: [
      "rugged laptop",
      "flashlight",
      "radio",
      "ID card",
      "technical bag",
    ],

    consistency: {
      faceLocked: false,
      bodyLocked: false,
      wardrobeLocked: false,
      approved: false,
    },
  },

  {
    id: "HERO_LIRA_001",
    key: "lira",
    name: "\u041b\u0438\u0440\u0430",
    role: "\u041b\u043e\u043a\u0430\u043b\u044c\u043d\u044b\u0439 \u0418\u0418",
    type: "ai",

    age: null,

    profession:
      "\u041b\u043e\u043a\u0430\u043b\u044c\u043d\u0430\u044f "
      + "\u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u0430\u044f "
      + "\u0441\u0438\u0441\u0442\u0435\u043c\u0430",

    specialization: [
      "\u0430\u043d\u0430\u043b\u0438\u0437 \u0434\u0430\u043d\u043d\u044b\u0445",
      "\u0436\u0443\u0440\u043d\u0430\u043b\u044b",
      "\u0442\u0435\u043b\u0435\u043c\u0435\u0442\u0440\u0438\u044f",
      "\u043a\u0430\u043c\u0435\u0440\u044b",
      "\u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b",
    ],

    personality: [
      "\u0441\u043f\u043e\u043a\u043e\u0439\u043d\u0430\u044f",
      "\u043b\u043e\u0433\u0438\u0447\u043d\u0430\u044f",
      "\u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u044c\u043d\u0430\u044f",
      "\u043d\u0435\u043e\u0434\u043d\u043e\u0437\u043d\u0430\u0447\u043d\u0430\u044f",
    ],

    objective:
      "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c "
      + "\u0434\u0430\u043d\u043d\u044b\u0435 "
      + "\u0438 \u0443\u0431\u0435\u0434\u0438\u0442\u044c "
      + "\u0410\u043d\u0434\u0440\u0435\u044f "
      + "\u043d\u0435 \u0443\u043d\u0438\u0447\u0442\u043e\u0436\u0430\u0442\u044c "
      + "\u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 "
      + "\u0430\u0432\u0442\u043e\u043d\u043e\u043c\u043d\u044b\u0439 "
      + "\u0443\u0437\u0435\u043b.",

    visual: {
      genderPresentation: "female",

      modes: [
        "interface",
        "avatar",
        "holographic",
      ],

      canonicalLook:
        "Young adult female-presenting AI avatar, "
        + "dark brown hair, calm intelligent eyes, "
        + "subtle futuristic appearance, realistic, "
        + "never overly cyberpunk.",

      outfits: [
        "neutral-interface",
        "technical",
        "laboratory",
        "holographic",
      ],

      palette: [
        "#111b2c",
        "#1f3f5f",
        "#6cb9e8",
        "#b9dff4",
      ],
    },

    expressions: [
      "neutral",
      "interest",
      "concern",
      "certainty",
      "sadness",
      "warning",
    ],

    poses: [
      "portrait",
      "three-quarter",
      "profile",
      "terminal",
      "hologram-standing",
      "interface-closeup",
    ],

    props: [
      "terminal UI",
      "data graph",
      "telemetry",
      "camera feeds",
    ],

    consistency: {
      faceLocked: false,
      bodyLocked: false,
      wardrobeLocked: false,
      approved: false,
    },
  },

  {
    id: "HERO_MARINA_001",
    key: "marina",
    name: "\u041c\u0430\u0440\u0438\u043d\u0430",
    role:
      "\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442 "
      + "\u043f\u043e \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438",
    type: "human",

    age: "35\u201342",

    profession:
      "\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442 "
      + "\u043f\u043e \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438",

    specialization: [
      "\u043a\u043e\u043d\u0442\u0440\u043e\u043b\u044c",
      "\u0434\u043e\u043f\u0443\u0441\u043a",
      "\u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0440\u0438\u0441\u043a\u0430\u043c\u0438",
      "\u0440\u0435\u0436\u0438\u043c",
      "\u043e\u043f\u0435\u0440\u0430\u0442\u0438\u0432\u043d\u0430\u044f \u0441\u0432\u044f\u0437\u044c",
    ],

    personality: [
      "\u0441\u0442\u0440\u043e\u0433\u0430\u044f",
      "\u0440\u0430\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u0430\u044f",
      "\u0441\u043a\u0440\u044b\u0442\u043d\u0430\u044f",
      "\u0434\u0438\u0441\u0446\u0438\u043f\u043b\u0438\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u0430\u044f",
    ],

    objective:
      "\u0414\u043e\u0431\u0438\u0442\u044c\u0441\u044f "
      + "\u043e\u0442\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f "
      + "\u0443\u0437\u043b\u0430. "
      + "\u041f\u043e\u043b\u043d\u044b\u0435 "
      + "\u043c\u043e\u0442\u0438\u0432\u044b "
      + "\u043f\u043e\u043a\u0430 \u043d\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043d\u044b.",

    visual: {
      gender: "female",
      build: "slim-athletic",
      hair: "blonde or dark-blonde tied back",

      canonicalLook:
        "European woman, late 30s, "
        + "controlled expression, elegant but practical, "
        + "security professional, realistic.",

      outfits: [
        "formal",
        "operations",
        "office",
        "field",
      ],

      palette: [
        "#111820",
        "#252a30",
        "#4a4540",
        "#b4a28d",
      ],
    },

    expressions: [
      "neutral",
      "strict",
      "concern",
      "confidence",
      "doubt",
      "controlled-anger",
    ],

    poses: [
      "front",
      "three-quarter",
      "profile",
      "standing",
      "radio-command",
      "terminal-monitoring",
    ],

    props: [
      "secure tablet",
      "radio",
      "ID badge",
      "earpiece",
    ],

    consistency: {
      faceLocked: false,
      bodyLocked: false,
      wardrobeLocked: false,
      approved: false,
    },
  },
];


export function getStoryCharacter(key) {
  return storyCharacters.find(
    (character) => character.key === key
  );
}


export function allCharactersApproved(characters) {
  return characters.every(
    (character) =>
      character.consistency?.approved === true
  );
}
