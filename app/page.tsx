import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "XBert — AI Employee by Nextiva",
};

export default function HomePage() {
  const html = loadLegacyHtml("index.html");
  return (
    <LegacyPage
      bodyClass="page-index"
      pageStylesheet="/styles/page-index.css"
      html={html}
    />
  );
}
