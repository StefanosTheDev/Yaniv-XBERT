/**
 * Mobile slide-in nav drawer. Visual structure is byte-identical to the
 * original; href targets now resolve to real routes for the pages we have
 * built (or will build in subsequent phases).
 *
 * Open/close behavior is bound by /script.js via .nav-toggle in <Nav />.
 */
export default function MobileNav() {
  return (
    <>
      <div className="mobile-nav-overlay" />
      <div className="mobile-nav-panel">
        <div className="mobile-nav-links">
          <div className="mobile-nav-dropdown">
            <a href="#">
              Product <span className="mobile-carat" />
            </a>
            <div className="mobile-dropdown-items">
              <a href="/ai-employee">AI Employee</a>
              <a href="/agent-assist">Agent Assist</a>
              <a href="/ai-receptionist">AI Receptionist</a>
              <a href="/how-xbert-works">How XBert works</a>
              <a href="/integrations">Integrations</a>
              <a href="/security">Security &amp; Trust</a>
              <a href="/platform">The Platform</a>
            </div>
          </div>
          <div className="mobile-nav-dropdown">
            <a href="#">
              Industries <span className="mobile-carat" />
            </a>
            <div className="mobile-dropdown-items">
              <a href="/industries/healthcare">Healthcare</a>
              <a href="/industries/insurance">Insurance</a>
              <a href="/industries/real-estate">Real Estate</a>
              <a href="/industries/retail-ecommerce">Retail &amp; E-commerce</a>
              <a href="/industries/professional-services">
                Professional Services
              </a>
            </div>
          </div>
          <div className="mobile-nav-dropdown">
            <a href="#">
              Resources <span className="mobile-carat" />
            </a>
            <div className="mobile-dropdown-items">
              <a href="/our-customers">Our Customers</a>
              <a href="/customer-stories">Customer Stories</a>
              <a href="/about">About Nextiva</a>
              <a href="/leadership">Leadership</a>
              <a href="/help">Help Center</a>
            </div>
          </div>
          <a href="/pricing">Pricing</a>
          <a href="tel:18883071013">Sales: 888-307-1013</a>
        </div>
        <div className="mobile-nav-actions">
          <a
            href="https://www.nextiva.com/join"
            className="btn btn-primary"
            target="_blank"
            rel="noopener noreferrer"
          >
            Start Free Trial
          </a>
          <a href="/demo" className="btn btn-secondary">
            Get A Demo
          </a>
          <a href="/login" className="nav-signin">
            Log In
          </a>
        </div>
      </div>
    </>
  );
}
