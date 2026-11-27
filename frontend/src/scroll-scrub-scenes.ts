import type { ScrollScrubScene, ScrollScrubTheme } from "./components/scroll-scrub/scroll-scrub";
export const scrollScrubTheme: ScrollScrubTheme = { accent: "#C6E85B", background: "#F2F4EF", ink: "#202722", muted: "#46534A" };
export const scrollScrubScenes: ScrollScrubScene[] = [{
  id: "intelligence-journey",
  label: "The intelligence journey",
  poster: "/assets/world/scene-01-poster.webp",
  mobilePoster: "/assets/world/scene-01-mobile-poster.webp",
  clip: "/assets/world/scene-01.mp4",
  mobileClip: "/assets/world/scene-01-mobile.mp4",
  title: "See the signal.",
  body: "One continuous journey from raw observations to an explainable decision.",
  kicker: "InsightX / Predictive intelligence",
  tags: ["Signal", "Structure", "Prediction", "Explanation", "Decision"],
  align: "left",
  scroll: 5.2,
}];
