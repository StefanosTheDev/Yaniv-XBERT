import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Security | XBert by Nextiva",
};

export default function SecurityPage() {
  const html = loadLegacyHtml("security.html");
  return (
    <LegacyPage
      bodyClass="page-security"
      pageStylesheet="/styles/page-security.css"
      html={html}
    />
  );
}
