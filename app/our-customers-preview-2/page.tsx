import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Our Customers (Preview 2 — Symbolic) | XBert by Nextiva",
  description:
    "Alternative preview of /our-customers using portraits that are symbolic for each industry — people captured doing the work the page is talking about.",
  robots: { index: false, follow: false },
};

export default function OurCustomersPreview2Page() {
  const html = loadLegacyHtml("our-customers-preview-2.html");
  return (
    <LegacyPage
      bodyClass="page-our-customers page-our-customers-preview"
      pageStylesheet={[
        "/styles/page-index.css",
        "/styles/page-our-customers.css",
      ]}
      html={html}
    />
  );
}
