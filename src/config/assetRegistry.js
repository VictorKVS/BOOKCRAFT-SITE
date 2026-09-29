export const assetRegistry = {
  hero: {
    key: "hero.main",
    status: "candidate",
    path: "/assets/bookcraft/hero/hero-main.webp",
    candidatePath: "/assets/bookcraft/hero/candidates/hero-main-v1.png",
    role: "Main hero character / central visual",
    desktop: { width: 760, height: 610, fit: "contain" },
    tablet: { width: 620, height: 520, fit: "contain" },
    mobile: { width: 390, height: 360, fit: "contain" },
    notes: "Separate asset; no baked-in text, HUD, buttons or navigation."
  },
  background: {
    key: "hero.background",
    status: "selected",
    path: "/assets/bookcraft/backgrounds/hero-studio-ru-v1.png",
    alternatePath: "/assets/bookcraft/backgrounds/hero-studio-en-v1.png",
    role: "Hero studio environment / decorative narrative scene",
    desktop: { width: 1200, height: 610, fit: "cover" },
    tablet: { width: 940, height: 520, fit: "cover" },
    mobile: { width: 680, height: 360, fit: "cover" },
    notes: "Russian background is active. English variant is retained for future locale switching. Live navigation, CTA and analytics HUD remain React."
  },
  props: {
    script: {
      key: "props.script",
      status: "placeholder",
      path: "/assets/bookcraft/props/script.webp",
      role: "Floating script card art",
      desktop: { width: 180, height: 128, fit: "contain" }
    },
    storyboard: {
      key: "props.storyboard",
      status: "placeholder",
      path: "/assets/bookcraft/props/storyboard.webp",
      role: "Floating storyboard art",
      desktop: { width: 200, height: 132, fit: "contain" }
    },
    desk: {
      key: "props.desk",
      status: "placeholder",
      path: "/assets/bookcraft/props/desk.webp",
      role: "Desk / foreground prop layer",
      desktop: { width: 850, height: 170, fit: "cover" }
    }
  },
  cards: {
    books: {
      key: "card.books",
      status: "placeholder",
      path: "/assets/bookcraft/cards/books.webp",
      role: "Books card artwork",
      desktop: { width: 360, height: 86, fit: "cover" }
    },
    scripts: {
      key: "card.scripts",
      status: "placeholder",
      path: "/assets/bookcraft/cards/scripts.webp",
      role: "Scripts card artwork",
      desktop: { width: 360, height: 86, fit: "cover" }
    },
    avatar: {
      key: "card.avatar",
      status: "placeholder",
      path: "/assets/bookcraft/cards/avatar.webp",
      role: "Video avatar card artwork",
      desktop: { width: 360, height: 86, fit: "cover" }
    },
    images: {
      key: "card.images",
      status: "placeholder",
      path: "/assets/bookcraft/cards/images.webp",
      role: "Image generation card artwork",
      desktop: { width: 360, height: 86, fit: "cover" }
    }
  }
};

export const requiredVisualAssetKeys = [
  "hero.main",
  "hero.background",
  "card.books",
  "card.scripts",
  "card.avatar",
  "card.images"
];
