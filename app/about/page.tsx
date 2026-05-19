import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "About Nextiva | XBert",
  description:
    "XBert is built by Nextiva — nearly 20 years serving 100,000+ businesses, billions of customer interactions a year, 99.999% uptime. The infrastructure underneath the AI.",
};

export default function AboutPage() {
  const html = loadLegacyHtml("about.html");
  return (
    <LegacyPage
      bodyClass="page-about"
      pageStylesheet={["/styles/page-index.css", "/styles/page-about.css"]}
      html={html}
    />
  );
}
