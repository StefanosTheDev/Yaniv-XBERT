import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "How XBert Works | XBert by Nextiva",
};

export default function HowXbertWorksPage() {
  const html = loadLegacyHtml("how-xbert-works.html");
  return (
    <LegacyPage
      bodyClass="page-how-xbert-works"
      pageStylesheet="/styles/page-how-xbert-works.css"
      html={html}
    />
  );
}
