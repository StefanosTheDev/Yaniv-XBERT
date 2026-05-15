import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "AI Employee for Healthcare | XBert by Nextiva",
  description:
    "An AI employee that books appointments, verifies insurance, takes after-hours messages, and stays HIPAA-compliant — for clinics, dental practices, and patient-facing teams.",
};

export default function IndustriesHealthcarePage() {
  const html = loadLegacyHtml("industry-healthcare.html");
  return (
    <LegacyPage
      bodyClass="page-industry industry-healthcare"
      pageStylesheet={["/styles/page-index.css", "/styles/page-industry.css"]}
      html={html}
    />
  );
}
