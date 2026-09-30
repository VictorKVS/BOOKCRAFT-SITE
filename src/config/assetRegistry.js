export const assetRegistry = {
  hero: {
    key: "hero.main",
    status: "selected",
    path: "/assets/bookcraft/hero/character/active/alina-v1.png",
    role: "Active foreground character layer",
    desktop: { width: 760, height: 610, fit: "contain" },
    tablet: { width: 620, height: 520, fit: "contain" },
    mobile: { width: 390, height: 360, fit: "contain" },
    notes: "Character is independent from background and laptop.",
    character: {
      active: "/assets/bookcraft/hero/character/active/alina-v1.png",
      candidates: [
        {
          id: "alina-v2",
          path: "/assets/bookcraft/hero/character/candidates/alina-v2.png",
          status: "candidate",
          notes: "Latest portrait candidate. Keep inactive until background is removed / transparency is verified."
        }
      ]
    },
    laptop: {
      active: "/assets/bookcraft/hero/objects/laptop/laptop-front-v1.png",
      alternates: [
        "/assets/bookcraft/hero/objects/laptop/laptop-angle-v1.png"
      ],
      role: "Foreground occlusion layer that seats the character behind the workstation."
    }
  },
  background: {
    key: "hero.background",
    status: "selected",
    path: "/assets/bookcraft/backgrounds/hero-studio-ru-v1.png",
    alternatePath: "/assets/bookcraft/backgrounds/hero-studio-en-v1.png",
    role: "Full-width hero studio environment / decorative narrative scene",
    desktop: { width: 1200, height: 610, fit: "cover" },
    tablet: { width: 940, height: 520, fit: "cover" },
    mobile: { width: 680, height: 360, fit: "cover" },
    notes: "Background is independent from character, laptop, navigation, headline, CTA, metrics and HUD."
  },
  props: {
    script: {
      key: "props.script",
      status: "optional",
      path: "/assets/bookcraft/props/script.webp",
      role: "Floating script card art",
      desktop: { width: 180, height: 128, fit: "contain" }
    },
    storyboard: {
      key: "props.storyboard",
      status: "optional",
      path: "/assets/bookcraft/props/storyboard.webp",
      role: "Floating storyboard art",
      desktop: { width: 200, height: 132, fit: "contain" }
    },
    desk: {
      key: "props.desk",
      status: "background",
      path: "/assets/bookcraft/backgrounds/hero-studio-ru-v1.png",
      role: "Desk is currently part of the selected studio background."
    }
  },
  cards: {
    books: {
      key: "card.books",
      status: "selected",
      path: "/assets/bookcraft/cards/books.webp",
      role: "Books full-image button artwork"
    },
    scripts: {
      key: "card.scripts",
      status: "selected",
      path: "/assets/bookcraft/cards/scripts.webp",
      role: "Scripts full-image button artwork"
    },
    avatar: {
      key: "card.avatar",
      status: "selected",
      path: "/assets/bookcraft/cards/avatar.webp",
      role: "Video avatar full-image button artwork"
    },
    images: {
      key: "card.images",
      status: "selected",
      path: "/assets/bookcraft/cards/images.webp",
      role: "Image generation full-image button artwork"
    }
  }
};

export const heroLayerOrder = [
  "background",
  "character",
  "laptop",
  "live-ui",
  "hud"
];

export const requiredVisualAssetKeys = [
  "hero.main",
  "hero.background",
  "hero.laptop",
  "card.books",
  "card.scripts",
  "card.avatar",
  "card.images"
];
