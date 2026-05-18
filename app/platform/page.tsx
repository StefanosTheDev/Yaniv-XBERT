import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "The Platform | XBert by Nextiva",
  description:
    "Infrastructure, real-time data, and agentic AI — fused into one platform. The Nextiva backbone XBert runs on, that compounds with every customer interaction.",
};

export default function PlatformPage() {
  const html = loadLegacyHtml("platform.html");
  return (
    <LegacyPage
      bodyClass="page-platform"
      pageStylesheet={["/styles/page-index.css", "/styles/page-platform.css"]}
      html={html}
    />
  );
}
