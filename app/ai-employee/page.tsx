import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Employee | XBert by Nextiva",
  description:
    "XBert is an AI employee that handles your customer conversations end-to-end. Voice, SMS, chat, follow-ups. Trained in hours, working 24/7, smarter every shift.",
};

export default function AiEmployeePage() {
  const html = loadLegacyHtml("ai-employee.html");
  return (
    <LegacyPage
      bodyClass="page-ai-employee"
      pageStylesheet={[
        "/styles/page-index.css",
        "/styles/page-ai-employee.css",
      ]}
      html={html}
    />
  );
}
