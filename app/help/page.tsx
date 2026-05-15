import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Help Center | XBert by Nextiva",
  description:
    "Guides, docs, and support for XBert. Setup, channels, integrations, security, billing, and the full FAQ.",
};

export default function HelpPage() {
  const html = loadLegacyHtml("help.html");
  return (
    <LegacyPage
      bodyClass="page-help"
      pageStylesheet={["/styles/page-index.css", "/styles/page-help.css"]}
      html={html}
    />
  );
}
