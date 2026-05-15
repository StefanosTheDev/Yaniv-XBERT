import Script from "next/script";

type LegacyPageProps = {
  bodyClass: string;
  /**
   * Page stylesheet(s). Accepts a single href or an ordered list. Listed
   * sheets are loaded in order, so later entries override earlier ones —
   * use this to layer a page-specific stylesheet on top of a shared
   * section vocabulary (e.g. ["/styles/page-index.css", "/styles/page-ai-employee.css"]).
   */
  pageStylesheet: string | string[];
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
  const stylesheets = Array.isArray(pageStylesheet)
    ? pageStylesheet
    : [pageStylesheet];
  return (
    <>
      {stylesheets.map((href) => (
        <link key={href} rel="stylesheet" href={href} />
      ))}
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
