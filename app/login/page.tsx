import type { Metadata } from "next";
import LegacyPage from "@/components/LegacyPage";
import { loadLegacyHtml } from "@/components/loadLegacy";

export const metadata: Metadata = {
  title: "Log In | XBert by Nextiva",
  description:
    "Sign in to your XBert workspace — manage AI sessions, integrations, transcripts, and analytics for your AI employee.",
  robots: { index: false, follow: false },
};

export default function LoginPage() {
  const html = loadLegacyHtml("login.html");
  return (
    <LegacyPage
      bodyClass="page-auth page-login"
      pageStylesheet={["/styles/page-index.css", "/styles/page-auth.css"]}
      html={html}
    />
  );
}
