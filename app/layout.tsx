import type { Metadata, Viewport } from "next";
import Script from "next/script";
import XBertSvgSprite from "@/components/XBertSvgSprite";
import Nav from "@/components/Nav";
import MobileNav from "@/components/MobileNav";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "XBert — AI Employee by Nextiva",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#0B1428",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="color-scheme" content="dark" />

        {/* Fonts */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght,SOFT@0,9..144,400..700,0..100;1,9..144,400..700,0..100&family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap"
          rel="stylesheet"
        />

        {/* Icons */}
        <link
          href="https://cdn.jsdelivr.net/npm/remixicon@4.7.0/fonts/remixicon.css"
          rel="stylesheet"
        />

        {/* Shared styles (page-specific css is injected per page) */}
        <link rel="stylesheet" href="/styles/tokens.css" />
        <link rel="stylesheet" href="/styles/base.css" />
        <link rel="stylesheet" href="/styles/nav.css" />
        <link rel="stylesheet" href="/styles/shared.css" />
        <link rel="stylesheet" href="/styles/section-hero.css" />
        <link rel="stylesheet" href="/styles/section-pricing.css" />
        <link rel="stylesheet" href="/styles/footer.css" />
      </head>
      <body>
        {/* Lottie web-component player — must be registered before page scripts */}
        <Script
          src="https://unpkg.com/@lottiefiles/lottie-player@2.0.8/dist/lottie-player.js"
          strategy="beforeInteractive"
        />
        <XBertSvgSprite />
        <Nav />
        <MobileNav />
        {children}
        <Footer />
      </body>
    </html>
  );
}
