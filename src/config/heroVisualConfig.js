export const heroVisualConfig = {
  scene: {
    background: {
      enabled: true,
      asset: "/assets/bookcraft/hero/backgrounds/studio-01.png",
    },

    laptop: {
      enabled: true,
      asset: "/assets/bookcraft/hero/equipment/laptop/laptop-angle-01.png",
    },
  },

  layers: {
    character: {
      enabled: true,
      mode: "sequence",
      intervalMs: 8000,
      startIndex: 0,
      transitionMs: 700,

      items: [
        {
          id: "alina-01",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/characters/alina/alina-01.png",
          tags: ["alina", "light"],
        },
        {
          id: "alina-02",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/characters/alina/alina-02.png",
          tags: ["alina", "dark"],
        },
        {
          id: "alina-03",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/characters/alina/alina-03.png",
          tags: ["alina", "white-jacket"],
        },
        {
          id: "alina-04",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/characters/alina/alina-04.png",
          tags: ["alina", "white"],
        },
      ],
    },

    books: {
      enabled: true,
      mode: "sequence",
      intervalMs: 11000,
      startIndex: 0,
      transitionMs: 700,

      items: [
        {
          id: "books-01",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/foreground/books/books-01.png",
        },
        {
          id: "books-02",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/foreground/books/books-02.png",
        },
        {
          id: "books-03",
          enabled: true,
          asset:
            "/assets/bookcraft/hero/foreground/books/books-03.png",
        },
      ],
    },

    props: {
      enabled: false,
      mode: "sequence",
      intervalMs: 13000,
      startIndex: 0,
      transitionMs: 700,
      items: [],
    },
  },
};

export default heroVisualConfig;