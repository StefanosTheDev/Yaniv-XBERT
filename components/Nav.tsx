/**
 * Desktop + mobile-toggle navigation. Visual structure is byte-identical to
 * the original static markup; the only change is href targets now resolve
 * to real routes for the pages we have built (or will build in subsequent
 * phases).
 *
 * Mobile drawer panel is rendered separately by <MobileNav />.
 * Scroll/dropdown/mobile-toggle behavior is bound by /script.js.
 */
export default function Nav() {
  return (
    <nav className="navbar">
      <div className="nav-wrapper">
        <div className="nav-left">
          <a href="/" className="nav-logo" aria-label="XBert home">
            <svg
              className="nav-logo-svg"
              viewBox="0 0 76.49 27.41"
              aria-hidden="true"
              focusable="false"
            >
              <use href="#xbert-logo-full" />
            </svg>
          </a>
          <ul className="nav-menu">
            <li className="nav-dropdown nav-dropdown-mega">
              <a href="#">
                Product <span className="nav-carat" />
              </a>
              <div className="mega-menu">
                <div className="mega-menu-inner">
                  <div className="mega-menu-section">
                    <span className="mega-menu-label">About XBert</span>
                    <a href="/how-xbert-works" className="mega-menu-item">
                      <span className="mega-menu-title">How XBert works</span>
                      <span className="mega-menu-desc">
                        AI that does actual work, not just conversation.
                      </span>
                    </a>
                    <a href="/integrations" className="mega-menu-item">
                      <span className="mega-menu-title">Integrations</span>
                      <span className="mega-menu-desc">
                        Connect your calendars, CRMs, and tools.
                      </span>
                    </a>
                    <a href="/security" className="mega-menu-item">
                      <span className="mega-menu-title">Security &amp; Trust</span>
                      <span className="mega-menu-desc">
                        AI safety, guardrails, and compliance foundation.
                      </span>
                    </a>
                    <a href="/platform" className="mega-menu-item">
                      <span className="mega-menu-title">The Platform</span>
                      <span className="mega-menu-desc">
                        AI and humans in tandem. The platform advantage.
                      </span>
                    </a>
                  </div>

                  <div className="mega-menu-section">
                    <span className="mega-menu-label">Featured Capabilities</span>
                    <a href="/ai-employee" className="mega-menu-item">
                      <span className="mega-menu-title">AI Employee</span>
                    </a>
                    <a href="/agent-assist" className="mega-menu-item">
                      <span className="mega-menu-title">Agent Assist</span>
                    </a>
                    <a href="/ai-receptionist" className="mega-menu-item">
                      <span className="mega-menu-title">AI Receptionist</span>
                    </a>
                  </div>

                  <div className="mega-menu-section">
                    <span className="mega-menu-label">Industries</span>
                    <a href="/industries/healthcare" className="mega-menu-item">
                      <span className="mega-menu-title">Healthcare</span>
                    </a>
                    <a href="/industries/insurance" className="mega-menu-item">
                      <span className="mega-menu-title">Insurance</span>
                    </a>
                    <a href="/industries/real-estate" className="mega-menu-item">
                      <span className="mega-menu-title">Real Estate</span>
                    </a>
                    <a
                      href="/industries/retail-ecommerce"
                      className="mega-menu-item"
                    >
                      <span className="mega-menu-title">Retail &amp; E-commerce</span>
                    </a>
                    <a
                      href="/industries/professional-services"
                      className="mega-menu-item"
                    >
                      <span className="mega-menu-title">Professional Services</span>
                    </a>
                  </div>
                </div>
              </div>
            </li>
            <li className="nav-dropdown nav-dropdown-mega">
              <a href="#">
                Resources <span className="nav-carat" />
              </a>
              <div className="mega-menu">
                <div className="mega-menu-inner">
                  <div className="mega-menu-section">
                    <span className="mega-menu-label">Learn</span>
                    <a href="/our-customers" className="mega-menu-item">
                      <span className="mega-menu-title">Our Customers</span>
                      <span className="mega-menu-desc">
                        Delivering for every business.
                      </span>
                    </a>
                    <a href="/customer-stories" className="mega-menu-item">
                      <span className="mega-menu-title">Customer Stories</span>
                      <span className="mega-menu-desc">
                        How businesses use XBert.
                      </span>
                    </a>
                    <a href="/about" className="mega-menu-item">
                      <span className="mega-menu-title">About Nextiva</span>
                      <span className="mega-menu-desc">
                        The company behind XBert.
                      </span>
                    </a>
                    <a href="/leadership" className="mega-menu-item">
                      <span className="mega-menu-title">Leadership</span>
                      <span className="mega-menu-desc">
                        Meet our executive team.
                      </span>
                    </a>
                  </div>
                  <div className="mega-menu-section">
                    <span className="mega-menu-label">Support</span>
                    <a href="/help" className="mega-menu-item">
                      <span className="mega-menu-title">Help Center</span>
                      <span className="mega-menu-desc">
                        Guides, docs, and support.
                      </span>
                    </a>
                  </div>
                </div>
              </div>
            </li>
            <li>
              <a href="/pricing">Pricing</a>
            </li>
          </ul>
        </div>
        <div className="nav-right">
          <a
            href="tel:18883071013"
            className="btn btn-primary nav-cta nav-phone"
          >
            <i className="ri-headphone-line" aria-hidden="true" />
            <span className="nav-phone-label">Sales</span>
            <span className="nav-phone-number">888-307-1013</span>
          </a>
          <a href="/login" className="btn btn-primary nav-cta">
            Log In
          </a>
          <a href="/demo" className="btn btn-primary nav-cta nav-cta-demo">
            Get A Demo
          </a>
          <a
            href="https://www.nextiva.com/join"
            className="btn btn-primary nav-cta-primary"
            target="_blank"
            rel="noopener noreferrer"
          >
            Start Free Trial
          </a>
          <button
            className="nav-toggle"
            aria-label="Toggle navigation"
            aria-expanded="false"
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </nav>
  );
}
