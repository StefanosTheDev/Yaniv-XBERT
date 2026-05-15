import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Employee for Professional Services | XBert by Nextiva",
  description:
    "An AI employee that handles client intake, books consults, and never misses an after-hours inquiry — for law firms, accounting practices, and consultancies.",
};

export default function IndustriesProfessionalServicesPage() {
  const html = loadLegacyHtml("industry-professional-services.html");
  return (
    <LegacyPage
      bodyClass="page-industry industry-professional-services"
      pageStylesheet={["/styles/page-index.css", "/styles/page-industry.css"]}
      html={html}
    />
  );
}
