import { ArrowRight, Camera, Leaf, ShieldCheck, Sprout } from "lucide-react";
import { Link } from "react-router-dom";

export function LandingPage() {
  return (
    <main className="landing-page">
      <nav className="landing-nav">
        <span className="brand">
          <span className="brand-mark">
            <Leaf size={18} />
          </span>
          <span>
            fieldnote<small>smart farming</small>
          </span>
        </span>
        <div>
          <Link to="/login">Sign in</Link>
          <Link className="landing-nav-cta" to="/register">
            Create account <ArrowRight size={15} />
          </Link>
        </div>
      </nav>
      <section className="landing-hero">
        <div className="landing-copy">
          <p className="eyebrow">AI crop diagnosis · built for the field</p>
          <h1>
            Know what your
            <br />
            <em>crop needs next.</em>
          </h1>
          <p>
            Photograph a leaf. Fieldnote checks image quality, identifies the
            crop and disease, measures severity, and turns the result into
            practical action.
          </p>
          <Link className="primary landing-cta" to="/register">
            Start your field journal <ArrowRight size={17} />
          </Link>
          <div className="landing-proof">
            <span>
              <ShieldCheck size={16} /> Safety-first advice
            </span>
            <span>
              <Sprout size={16} /> Five supported crops
            </span>
          </div>
        </div>
        <div className="landing-visual">
          <img
            src="/aphids_tomato.jpeg"
            alt="Tomato leaf ready for a crop health scan"
          />
          <div className="landing-scan-tag">
            <span className="pulse-dot" /> Ready for a closer look
          </div>
          <div className="landing-orbit orbit-one" />
          <div className="landing-orbit orbit-two" />
        </div>
      </section>
      <section className="landing-flow">
        <p className="eyebrow">From leaf to next action</p>
        <div>
          <span>
            <Camera size={17} /> Capture
          </span>
          <i>→</i>
          <span>
            <Leaf size={17} /> Understand
          </span>
          <i>→</i>
          <span>
            <Sprout size={17} /> Act early
          </span>
        </div>
      </section>
    </main>
  );
}
