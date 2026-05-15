import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Employee for Insurance | XBert by Nextiva",
  description:
    "An AI employee that handles policy questions, claims status, and renewals — built for the regulated language and audit-readiness insurance teams require.",
};

export default function IndustriesInsurancePage() {
  const html = loadLegacyHtml("industry-insurance.html");
  return (
    <LegacyPage
      bodyClass="page-industry industry-insurance"
      pageStylesheet={["/styles/page-index.css", "/styles/page-industry.css"]}
      html={html}
    />
  );
}
