import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Employee for Real Estate | XBert by Nextiva",
  description:
    "An AI employee that qualifies leads, books showings, and chases follow-ups — so brokerages, teams, and property managers never miss a high-intent inquiry.",
};

export default function IndustriesRealEstatePage() {
  const html = loadLegacyHtml("industry-real-estate.html");
  return (
    <LegacyPage
      bodyClass="page-industry industry-real-estate"
      pageStylesheet={["/styles/page-index.css", "/styles/page-industry.css"]}
      html={html}
    />
  );
}
