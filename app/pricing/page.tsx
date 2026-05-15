import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Pricing | XBert by Nextiva",
};

export default function PricingPage() {
  const html = loadLegacyHtml("pricing.html");
  return (
    <LegacyPage
      bodyClass="page-pricing"
      pageStylesheet="/styles/page-pricing.css"
      html={html}
    />
  );
}
