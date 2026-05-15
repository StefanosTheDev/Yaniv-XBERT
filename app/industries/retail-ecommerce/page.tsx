import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Employee for Retail & E-commerce | XBert by Nextiva",
  description:
    "An AI employee that handles order status, returns, and seasonal spikes across voice, chat, and SMS — so retailers and e-commerce brands scale support without scaling headcount.",
};

export default function IndustriesRetailEcommercePage() {
  const html = loadLegacyHtml("industry-retail-ecommerce.html");
  return (
    <LegacyPage
      bodyClass="page-industry industry-retail-ecommerce"
      pageStylesheet={["/styles/page-index.css", "/styles/page-industry.css"]}
      html={html}
    />
  );
}
