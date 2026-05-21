import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Leadership (Preview) | XBert by Nextiva",
  description:
    "Preview of /leadership for iteration. Live page is unchanged.",
  robots: { index: false, follow: false },
};

export default function LeadershipPreviewPage() {
  const html = loadLegacyHtml("leadership-preview.html");
  return (
    <LegacyPage
      bodyClass="page-leadership page-leadership-preview"
      pageStylesheet={["/styles/page-index.css", "/styles/page-leadership.css"]}
      html={html}
    />
  );
}
