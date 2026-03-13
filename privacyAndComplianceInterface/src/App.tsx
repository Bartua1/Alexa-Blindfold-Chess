import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import './index.css';

const PrivacyPolicy = () => (
  <div className="content-card">
    <h1>Privacy Policy</h1>
    <section>
      <h2>Introduction</h2>
      <p>Your privacy is important to us. This Privacy Policy explains how "Blindfold Chess" (the "Skill") handles your information when you use it through Amazon Alexa.</p>
    </section>
    <section>
      <h2>Information We Collect</h2>
      <p>The Skill does not collect, store, or share any personal information. We process voice commands to play chess, but these are handled entirely within the Alexa ecosystem.</p>
      <ul>
        <li><strong>Game State:</strong> We store the current board position (FEN) during your session to allow you to continue your game.</li>
        <li><strong>No Personal Data:</strong> We do not have access to your name, email, or physical location.</li>
      </ul>
    </section>
    <section>
      <h2>Third-Party Services</h2>
      <p>The Skill uses standard Alexa interfaces. Amazon's Privacy Policy applies to your use of Alexa devices.</p>
    </section>
    <section>
      <h2>Contact</h2>
      <p>If you have any questions, please contact the developer through the Alexa Skill Store contact options.</p>
    </section>
  </div>
);

const TermsOfUse = () => (
  <div className="content-card">
    <h1>Terms of Use</h1>
    <section>
      <h2>1. Acceptance of Terms</h2>
      <p>By using the Blindfold Chess skill, you agree to these terms. If you do not agree, please do not use the Skill.</p>
    </section>
    <section>
      <h2>2. Use of the Skill</h2>
      <p>This skill is provided for entertainment purposes only. You are allowed to use it for personal, non-commercial play.</p>
    </section>
    <section>
      <h2>3. Disclaimer</h2>
      <p>The Skill is provided "as is" without any warranties. We are not responsible for any issues arising from the use of the Skill or errors in the chess engine logic.</p>
    </section>
    <section>
      <h2>4. Changes to Terms</h2>
      <p>We may update these terms at any time. Your continued use of the Skill constitutes acceptance of the new terms.</p>
    </section>
  </div>
);

function App() {
  return (
    <BrowserRouter basename="/blindfoldchess">
      <div className="layout">
        <header className="header">
          <div className="logo">Blindfold<span>Chess</span></div>
          <nav style={{ marginTop: '1rem' }}>
            <Link to="/privacy-policy" style={{ color: 'var(--accent-color)', marginRight: '1rem', textDecoration: 'none' }}>Privacy Policy</Link>
            <Link to="/terms-of-use" style={{ color: 'var(--accent-color)', textDecoration: 'none' }}>Terms of Use</Link>
          </nav>
        </header>

        <main style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
          <Routes>
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms-of-use" element={<TermsOfUse />} />
            <Route path="/" element={<PrivacyPolicy />} />
          </Routes>
        </main>

        <footer className="footer">
          &copy; {new Date().getFullYear()} Blindfold Chess. All rights reserved.
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
