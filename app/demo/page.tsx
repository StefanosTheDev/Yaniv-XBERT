import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Get a Demo | XBert by Nextiva",
  description:
    "Book a 25-minute walkthrough on your stack — calls, calendars, CRMs — with the team who built XBert. Most demos scheduled within 24 hours.",
};

export default function DemoPage() {
  const html = loadLegacyHtml("demo.html");
  return (
    <LegacyPage
      bodyClass="page-auth page-demo"
      pageStylesheet={["/styles/page-index.css", "/styles/page-auth.css"]}
      html={html}
    />
  );
}
