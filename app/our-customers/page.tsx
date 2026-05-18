import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Our Customers | XBert by Nextiva",
  description:
    "Built for the businesses that keep the economy running. 93,000+ Main Street operators, mid-market teams, and the brands behind every Friday night — running on the Nextiva platform.",
};

export default function OurCustomersPage() {
  const html = loadLegacyHtml("our-customers.html");
  return (
    <LegacyPage
      bodyClass="page-our-customers"
      pageStylesheet={[
        "/styles/page-index.css",
        "/styles/page-our-customers.css",
      ]}
      html={html}
    />
  );
}
