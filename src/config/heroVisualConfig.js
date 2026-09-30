export const heroVisualConfig = {
  scene: {
    background: {
      enabled: true,
      asset: "/assets/bookcraft/hero/backgrounds/studio-01.png",
    },
  },

  rotation: {
    enabled: true,
    intervalMs: 10000,
    transitionMs: 900,

    scenes: [
      { character: 0, books: 0, laptop: 0 },
      { character: 1, books: 1, laptop: 1 },
      { character: 2, books: 2, laptop: 0 },
      { character: 3, books: 0, laptop: 1 },
      { character: 4, books: 1, laptop: 0 },
      { character: 5, books: 2, laptop: 1 },
    ],
  },

  layers: {
    character: {
      enabled: true,
      items: [
        {
          id: "alina-01",
          enabled: true,
          asset: "/assets/bookcraft/hero/characters/alina/alina-01.png",
        },
        {
          id: "alina-02",
          enabled: true,
          asset: "/assets/bookcraft/hero/characters/alina/alina-02.png",
        },
        {
          id: "alina-03",
          enabled: true,
          asset: "/assets/bookcraft/hero/characters/alina/alina-03.png",
        },
        {
          id: "alina-04",
          enabled: true,
          asset: "/assets/bookcraft/hero/characters/alina/alina-04.png",
        },
        {
          id: "alina-05",
          enabled: true,
          asset: "/assets/bookcraft/hero/characters/alina/alina-05.png",
        },
        {
          id: "alina-06",
          enabled: true,
          asset: "/assets/bookcraft/hero/characters/alina/alina-06.png",
        },
      ],
    },

    books: {
      enabled: true,
      items: [
        {
          id: "books-01",
          enabled: true,
          asset: "/assets/bookcraft/hero/foreground/books/books-01.png",
        },
        {
          id: "books-02",
          enabled: true,
          asset: "/assets/bookcraft/hero/foreground/books/books-02.png",
        },
        {
          id: "books-03",
          enabled: true,
          asset: "/assets/bookcraft/hero/foreground/books/books-03.png",
        },
      ],
    },

    laptop: {
      enabled: true,
      items: [
        {
          id: "laptop-angle-01",
          enabled: true,
          asset: "/assets/bookcraft/hero/equipment/laptop/laptop-angle-01.png",
        },
        {
          id: "laptop-front-01",
          enabled: true,
          asset: "/assets/bookcraft/hero/equipment/laptop/laptop-front-01.png",
        },
      ],
    },
  },
};

export default heroVisualConfig;
