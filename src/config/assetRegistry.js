export const assetRegistry = {
  hero: {
    key: "hero.main",
    status: "rotation",
    role: "Coordinated hero scene rotation",
    intervalMs: 10000,
    background: "/assets/bookcraft/hero/backgrounds/studio-01.png",
    characters: [
      "/assets/bookcraft/hero/characters/alina/alina-01.png",
      "/assets/bookcraft/hero/characters/alina/alina-02.png",
      "/assets/bookcraft/hero/characters/alina/alina-03.png",
      "/assets/bookcraft/hero/characters/alina/alina-04.png",
      "/assets/bookcraft/hero/characters/alina/alina-05.png",
      "/assets/bookcraft/hero/characters/alina/alina-06.png",
    ],
    books: [
      "/assets/bookcraft/hero/foreground/books/books-01.png",
      "/assets/bookcraft/hero/foreground/books/books-02.png",
      "/assets/bookcraft/hero/foreground/books/books-03.png",
    ],
    laptops: [
      "/assets/bookcraft/hero/equipment/laptop/laptop-angle-01.png",
      "/assets/bookcraft/hero/equipment/laptop/laptop-front-01.png",
    ],
  },

  cards: {
    books: {
      key: "card.books",
      status: "selected",
      path: "/assets/bookcraft/cards/books.webp",
    },
    scripts: {
      key: "card.scripts",
      status: "selected",
      path: "/assets/bookcraft/cards/scripts.webp",
    },
    avatar: {
      key: "card.avatar",
      status: "selected",
      path: "/assets/bookcraft/cards/avatar.webp",
    },
    images: {
      key: "card.images",
      status: "selected",
      path: "/assets/bookcraft/cards/images.webp",
    },
  },
};

export const heroLayerOrder = [
  "background",
  "character",
  "books",
  "laptop",
  "live-ui",
  "hud",
];

export const requiredVisualAssetKeys = [
  "hero.background",
  "hero.characters",
  "hero.books",
  "hero.laptops",
  "card.books",
  "card.scripts",
  "card.avatar",
  "card.images",
];
