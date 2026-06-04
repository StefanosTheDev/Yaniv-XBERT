import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Start Free Trial | XBert by Nextiva",
  description:
    "Bring your first AI employee online today. 14 days, 100 free sessions, full platform — no credit card. Most teams are live on their number in under an hour.",
};

export default function FreeTrialPage() {
  const html = loadLegacyHtml("free-trial.html");
  return (
    <LegacyPage
      bodyClass="page-auth page-trial"
      pageStylesheet={["/styles/page-index.css", "/styles/page-auth.css"]}
      html={html}
    />
  );
}
