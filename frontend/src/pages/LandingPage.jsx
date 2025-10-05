import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import './LandingPage.css'

export default function LandingPage() {
  // Carousel auto-advance removed per user request — features will remain static.
  // We randomize hero tile layout on each mount and avoid placing tiles behind the central hero content.

  useEffect(() => {
    // ensure container starts at top so hero is visible first
    const container = document.querySelector('.lp-container')
    if (container) container.scrollTop = 0

    // Randomize hero tiles positions on each load
    const tiles = Array.from(document.querySelectorAll('.lp-hero-tile'))
    if (!tiles.length) return

    // Compute exclusion zone by unioning the bounding boxes of important hero children
    // (the main content block and the centered logo area) so tiles never sit behind text or CTA.
    const heroEl = document.getElementById('hero')
    const innerEl = heroEl ? heroEl.querySelector('.lp-inner') : null
    let excludeRectPercent = { left: 28, top: 28, width: 44, height: 44 }
    if (heroEl && innerEl) {
      const heroRect = heroEl.getBoundingClientRect()

      // elements to exclude: the textual content and the logo (if present)
      const contentEl = heroEl.querySelector('.lp-hero-content')
      const logoEl = heroEl.querySelector('.lp-hero-logo-wrap')

      const rects = []
      if (contentEl) rects.push(contentEl.getBoundingClientRect())
      if (logoEl) rects.push(logoEl.getBoundingClientRect())
      // fallback to innerEl if nothing else
      if (!rects.length) rects.push(innerEl.getBoundingClientRect())

      // compute union of rects
      const union = rects.reduce((acc, r) => {
        if (!acc) return { left: r.left, top: r.top, right: r.right, bottom: r.bottom }
        return {
          left: Math.min(acc.left, r.left),
          top: Math.min(acc.top, r.top),
          right: Math.max(acc.right, r.right),
          bottom: Math.max(acc.bottom, r.bottom)
        }
      }, null)

      if (union) {
        const left = ((union.left - heroRect.left) / heroRect.width) * 100
        const top = ((union.top - heroRect.top) / heroRect.height) * 100
        const width = ((union.right - union.left) / heroRect.width) * 100
        const height = ((union.bottom - union.top) / heroRect.height) * 100
        const pad = 6 // percent padding so tiles keep clear room around CTA/text
        excludeRectPercent = {
          left: Math.max(0, left - pad),
          top: Math.max(0, top - pad),
          width: Math.min(100, width + pad * 2),
          height: Math.min(100, height + pad * 2)
        }
      }
    }

    const rndBetween = (min, max) => Math.random() * (max - min) + min

    // precompute heroRect and union rectangle in pixels for exact overlap tests
    const heroRectPx = heroEl ? heroEl.getBoundingClientRect() : null
    // compute union rect in px if available (we computed excludeRectPercent earlier)
    let unionPx = null
    if (heroRectPx && innerEl) {
      // derive unionPx from excludeRectPercent for pixel-level tests
      unionPx = {
        left: heroRectPx.left + (excludeRectPercent.left / 100) * heroRectPx.width,
        top: heroRectPx.top + (excludeRectPercent.top / 100) * heroRectPx.height,
        right: heroRectPx.left + ((excludeRectPercent.left + excludeRectPercent.width) / 100) * heroRectPx.width,
        bottom: heroRectPx.top + ((excludeRectPercent.top + excludeRectPercent.height) / 100) * heroRectPx.height
      }
    }

    tiles.forEach((tile, i) => {
      // try many times to find a position that does not overlap the unionRectPx
      let attempts = 0
      let leftPct, topPct, widthPct, heightPct
      const maxAttempts = 40
      let fits = false

      while (attempts < maxAttempts && !fits) {
        widthPct = Math.round(rndBetween(10, 26)) // percent width
        heightPct = Math.round(rndBetween(12, 32)) // percent height
        leftPct = Math.round(rndBetween(0, 100 - widthPct))
        topPct = Math.round(rndBetween(0, 100 - heightPct))

        if (!unionPx || !heroRectPx) {
          fits = true
          break
        }

        // convert tile to pixels and test overlap with unionPx
        const tileLeftPx = heroRectPx.left + (leftPct / 100) * heroRectPx.width
        const tileTopPx = heroRectPx.top + (topPct / 100) * heroRectPx.height
        const tileRightPx = tileLeftPx + (widthPct / 100) * heroRectPx.width
        const tileBottomPx = tileTopPx + (heightPct / 100) * heroRectPx.height

        const noOverlap = tileRightPx < unionPx.left || tileLeftPx > unionPx.right || tileBottomPx < unionPx.top || tileTopPx > unionPx.bottom

        if (noOverlap) fits = true
        attempts++
      }

      // fallback: if we couldn't find a non-overlapping position after many attempts, accept last pos
      const rotate = Math.round(rndBetween(-10, 10))

      // apply CSS custom properties for precise placement/visuals
      tile.style.setProperty('--tile-left', leftPct + '%')
      tile.style.setProperty('--tile-top', topPct + '%')
      tile.style.setProperty('--tile-w', widthPct + '%')
      tile.style.setProperty('--tile-h', heightPct + '%')
      tile.style.setProperty('--tile-rotate', rotate + 'deg')
      // slightly vary initial blur/opacity for depth (as vars so :hover can override)
      tile.style.setProperty('--tile-blur', Math.round(rndBetween(6, 10)) + 'px')
      tile.style.setProperty('--tile-opacity', `${rndBetween(0.72, 0.95)}`)
    })
  }, [])

  return (
    <div className="lp-container">
      <nav className="lp-navbar">
        <div className="lp-navbar-brand">
          <img src="/logo.png" alt="Patiently" className="lp-navbar-logo" />
          <span className="lp-navbar-title">Patiently</span>
        </div>
        {/* auth buttons removed per design */}
      </nav>
  <section id="hero" className="lp-slide lp-hero">
        {/* Picture tile grid background */}
        <div className="lp-hero-tiles">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="lp-hero-tile" style={{backgroundImage: `url(/${i + 1}.jpg)`}}></div>
          ))}
        </div>
        <div className="lp-inner">
          <div className="lp-hero-logo-wrap">
            {/* Using logo.png from public folder as logo */}
            <img src="/logo.png" alt="logo" className="lp-hero-logo" />
          </div>
          <div className="lp-hero-content">
            <h1 className="lp-hero-tagline">Clarity in every test result.</h1>
            <p className="lp-hero-description">
              From lab numbers to clear insights, Patiently explains what your results mean, 
              highlights what matters, and helps you know the right questions to ask.
            </p>
            <Link to="/dashboard" className="lp-hero-cta glow" role="button">Begin Now →</Link>
          </div>
        </div>
      </section>

  <section id="features" className="lp-slide lp-features">
        <div className="lp-inner">
          <h2 className="lp-section-title">Features that put patients first</h2>
          <div className="lp-feat-list-rows">
            {[
              {
                key: 'ai-translation',
                img: '/1.jpg',
                title: 'AI Translation & Explanation',
                desc: 'Plain-language explanations of complex medical terms and test results.'
              },
              {
                key: 'dashboard',
                img: '/2.jpg',
                title: 'Visual Dashboard & Highlights',
                desc: 'See what matters most with visual indicators and trend tracking.'
              },
              {
                key: 'questions',
                img: '/3.jpg',
                title: 'Question Generator',
                desc: 'Automatically suggests relevant questions to ask your healthcare provider.'
              },
              {
                key: 'trends',
                img: '/4.jpg',
                title: 'History & Trends',
                desc: 'Track how your results change over time and spot meaningful trends.'
              }
            ].map((feat, i) => (
              <div key={feat.key} className={`lp-feature-row ${i % 2 === 1 ? 'reverse' : ''}`}>
                <div className="lp-feature-media"><img src={feat.img} alt={feat.title} className="lp-feature-media-img"/></div>
                <div className="lp-feature-text">
                  <h3 className="lp-feat-title">{feat.title}</h3>
                  <p className="lp-feat-desc">{feat.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

  <section id="howto" className="lp-slide lp-howto">
        <div className="lp-inner">
          <h2 className="lp-section-title">How to use (patiently)</h2>
          <div className="lp-how-grid" aria-label="How it works steps">
            <div className="lp-how-card">
              <h3 className="lp-how-title">Upload your report</h3>
              <p className="lp-how-desc">Drag & drop or click to upload your medical report in seconds.</p>
            </div>
            <div className="lp-how-card">
              <h3 className="lp-how-title">We analyze it</h3>
              <p className="lp-how-desc">Our engine reads the file and identifies tests, values and context.</p>
            </div>
            <div className="lp-how-card">
              <h3 className="lp-how-title">Clear explanations</h3>
              <p className="lp-how-desc">Get plain-language explanations and what the numbers mean for you.</p>
            </div>
            <div className="lp-how-card">
              <h3 className="lp-how-title">Next steps</h3>
              <p className="lp-how-desc">Download, share, or use suggested questions for your provider visit.</p>
            </div>
          </div>
          <p className="lp-note">Tip: Large files take longer — please be patient while we process them.</p>
        </div>
      </section>

  <footer id="contact" className="lp-slide lp-footer">
        <div className="lp-inner">
          <div>© {new Date().getFullYear()} My App</div>
          <div className="lp-footer-links">
            <a href="#">Privacy</a>
            <a href="#">Terms</a>
            <a href="#">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
