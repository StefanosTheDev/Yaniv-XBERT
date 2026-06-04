import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Leadership (legacy) | XBert by Nextiva",
  robots: { index: false, follow: false },
};

/**
 * Snapshot of the previous /leadership page (4 individuals + 6 department
 * cards), preserved at /leadership-old after the new named-executive grid
 * rolled out at /leadership.
 */
export default function LeadershipOldPage() {
  const html = loadLegacyHtml("leadership-old.html");
  return (
    <LegacyPage
      bodyClass="page-leadership"
      pageStylesheet={["/styles/page-index.css", "/styles/page-leadership.css"]}
      html={html}
    />
  );
}
