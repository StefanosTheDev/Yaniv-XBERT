import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Leadership | XBert by Nextiva",
  description:
    "Meet the leaders behind XBert and Nextiva — engineers, ML researchers, and operators who have spent two decades on the frontline of customer work.",
};

export default function LeadershipPage() {
  const html = loadLegacyHtml("leadership.html");
  return (
    <LegacyPage
      bodyClass="page-leadership"
      pageStylesheet={["/styles/page-index.css", "/styles/page-leadership.css"]}
      html={html}
    />
  );
}
