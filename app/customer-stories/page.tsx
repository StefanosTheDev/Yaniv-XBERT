import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Customer Stories | XBert by Nextiva",
  description:
    "How real businesses use XBert to handle customer conversations end-to-end — across healthcare, real estate, insurance, retail, and professional services.",
};

export default function CustomerStoriesPage() {
  const html = loadLegacyHtml("customer-stories.html");
  return (
    <LegacyPage
      bodyClass="page-customer-stories"
      pageStylesheet={[
        "/styles/page-index.css",
        "/styles/page-industry.css",
        "/styles/page-customer-stories.css",
      ]}
      html={html}
    />
  );
}
