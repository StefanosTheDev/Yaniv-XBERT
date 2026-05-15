/**
 * Site footer. Visual structure is byte-identical to the original; href
 * targets now resolve to real routes for the pages we have built (or will
 * build in subsequent phases).
 *
 * The dynamic year is filled in by /script.js via the [data-year] hook.
 */
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        <div className="grid-12 footer-main">
          <div className="footer-brand">
            <a href="/" className="footer-logo" aria-label="XBert home">
              <svg
                className="footer-logo-svg"
                viewBox="0 0 76.49 27.41"
                aria-hidden="true"
                focusable="false"
              >
                <use href="#xbert-logo-full" />
              </svg>
            </a>
            <p>
              XBert is the AI employee for customer conversations. Built on
              Nextiva infrastructure for businesses that need every call,
              text, and chat handled well.
            </p>
            <a href="tel:18007990600" className="footer-phone">
              <i className="ri-phone-line" aria-hidden="true" />
              1-800-799-0600
            </a>
            <div className="footer-badges" aria-label="Trust signals">
              <span>SOC 2 Certified</span>
              <span>HIPAA Compliant</span>
              <span>99.999% Uptime</span>
            </div>
          </div>

          <div className="grid-12 footer-nav-grid">
            <div className="footer-nav-col">
              <h4>Product</h4>
              <ul>
                <li>
                  <a href="/ai-employee">AI Employee</a>
                </li>
                <li>
                  <a href="/agent-assist">Agent Assist</a>
                </li>
                <li>
                  <a href="/ai-receptionist">AI Receptionist</a>
                </li>
                <li>
                  <a href="/how-xbert-works">How XBert works</a>
                </li>
                <li>
                  <a href="/integrations">Integrations</a>
                </li>
                <li>
                  <a href="/security">Security &amp; Trust</a>
                </li>
                <li>
                  <a href="/pricing">Pricing</a>
                </li>
              </ul>
            </div>
            <div className="footer-nav-col">
              <h4>Industries</h4>
              <ul>
                <li>
                  <a href="/industries/healthcare">Healthcare</a>
                </li>
                <li>
                  <a href="/industries/insurance">Insurance</a>
                </li>
                <li>
                  <a href="/industries/real-estate">Real Estate</a>
                </li>
                <li>
                  <a href="/industries/retail-ecommerce">
                    Retail &amp; E-commerce
                  </a>
                </li>
                <li>
                  <a href="/industries/professional-services">
                    Professional Services
                  </a>
                </li>
              </ul>
            </div>
            <div className="footer-nav-col">
              <h4>Resources</h4>
              <ul>
                <li>
                  <a href="/customer-stories">Customer Stories</a>
                </li>
                <li>
                  <a href="/help">Help Center</a>
                </li>
                <li>
                  <a href="/about">About Nextiva</a>
                </li>
                <li>
                  <a href="/leadership">Leadership</a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <span className="footer-bottom-left">
            A Product from{" "}
            <a
              href="https://www.nextiva.com"
              target="_blank"
              rel="noopener"
            >
              Nextiva.com
            </a>
          </span>
          <span className="footer-bottom-center">
            &copy; <span data-year />
          </span>
          <div className="footer-bottom-right">
            <a href="#">Terms</a>
            <a href="#">Privacy</a>
            <a href="/security">Security</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
