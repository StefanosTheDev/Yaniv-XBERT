import Script from "next/script";

type LegacyPageProps = {
  bodyClass: string;
  pageStylesheet: string;
  html: string;
};

/**
 * Renders the body content of one of the original static HTML pages verbatim.
 * The wrapper carries the page-level body class so that descendant selectors
 * like `.page-index .foo` keep working exactly as before.
 *
 * The original /script.js is loaded with strategy="afterInteractive" so it
 * runs after the DOM is in place, matching the behavior of a defer-less
 * <script> at the end of <body>.
 */
export default function LegacyPage({
  bodyClass,
  pageStylesheet,
  html,
}: LegacyPageProps) {
  return (
    <>
      <link rel="stylesheet" href={pageStylesheet} />
      {/*
        suppressHydrationWarning: the children of this div come from an opaque
        HTML string and are rendered on the server. React occasionally reports
        a hydration mismatch here even when the strings are byte-identical
        (whitespace/attribute tokenization, browser extensions mutating the
        DOM pre-hydration). We treat the server HTML as authoritative.
      */}
      <div
        className={bodyClass}
        suppressHydrationWarning
        dangerouslySetInnerHTML={{ __html: html }}
      />
      <Script src="/script.js" strategy="afterInteractive" />
    </>
  );
}
