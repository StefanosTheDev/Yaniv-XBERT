import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Receptionist | XBert by Nextiva",
  description:
    "XBert answers every call in two rings. Books appointments, takes messages, transfers urgent calls, and never puts a customer on hold. 23+ voices and accents.",
};

export default function AiReceptionistPage() {
  const html = loadLegacyHtml("ai-receptionist.html");
  return (
    <LegacyPage
      bodyClass="page-ai-receptionist"
      pageStylesheet={[
        "/styles/page-index.css",
        "/styles/page-ai-receptionist.css",
      ]}
      html={html}
    />
  );
}
