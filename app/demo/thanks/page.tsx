import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Thanks — Demo Request Received | XBert by Nextiva",
  description:
    "Your demo request was received. A solutions engineer will reach out within one business day.",
  // Stays out of the index — it's a post-conversion landing page, not
  // organic search content.
  robots: { index: false, follow: false },
};

export default function DemoThanksPage() {
  const html = loadLegacyHtml("demo-thanks.html");
  return (
    <LegacyPage
      bodyClass="page-auth page-demo-thanks"
      pageStylesheet={["/styles/page-index.css", "/styles/page-auth.css"]}
      html={html}
    />
  );
}
