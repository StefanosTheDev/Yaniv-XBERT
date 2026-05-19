import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "XBert — AI Employee by Nextiva (legacy homepage)",
  robots: { index: false, follow: false },
};

/**
 * Snapshot of the previous homepage hero (toast-stack version),
 * preserved at /home-old so the original design stays accessible
 * after the new XBert-monogram hero rolls out at /.
 */
export default function HomeOldPage() {
  const html = loadLegacyHtml("index-old.html");
  return (
    <LegacyPage
      bodyClass="page-index"
      pageStylesheet="/styles/page-index.css"
      html={html}
    />
  );
}
