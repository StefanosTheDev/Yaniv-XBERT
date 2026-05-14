import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Integrations | XBert by Nextiva",
};

export default function IntegrationsPage() {
  const html = loadLegacyHtml("integrations.html");
  return (
    <LegacyPage
      bodyClass="page-integrations"
      pageStylesheet="/styles/page-integrations.css"
      html={html}
    />
  );
}
