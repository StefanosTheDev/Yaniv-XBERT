import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Agent Assist | XBert by Nextiva",
  description:
    "When your team steps in, XBert coaches them. Suggested responses, cited sources, and full customer context — your agents perform like your best ones from day one.",
};

export default function AgentAssistPage() {
  const html = loadLegacyHtml("agent-assist.html");
  return (
    <LegacyPage
      bodyClass="page-agent-assist"
      pageStylesheet={[
        "/styles/page-index.css",
        "/styles/page-agent-assist.css",
      ]}
      html={html}
    />
  );
}
