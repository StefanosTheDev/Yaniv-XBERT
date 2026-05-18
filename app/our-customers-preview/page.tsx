import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Our Customers (Preview) | XBert by Nextiva",
  description:
    "Preview of /our-customers with the new industry portrait photos swapped into the body cards. Hero collage and live page are unchanged.",
  robots: { index: false, follow: false },
};

export default function OurCustomersPreviewPage() {
  const html = loadLegacyHtml("our-customers-preview.html");
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
