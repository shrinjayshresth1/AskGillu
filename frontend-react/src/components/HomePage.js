import React, { useState } from "react";
import {
  MessageCircle,
  Users,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Star,
  Award,
  BookOpen,
  Globe,
  Mail,
  Phone,
  MapPin,
  Zap,
  Camera,
  Languages,
  RefreshCw,
  Brain,
} from "lucide-react";

const PILLARS = [
  {
    key: "multimodal",
    icon: "📸",
    title: "Multimodal",
    desc: "Upload images, scanned notices or fee receipts — AskGillu reads and understands them.",
    badge: "Vision AI",
    cls: "multimodal",
  },
  {
    key: "multilingual",
    icon: "🌐",
    title: "Multilingual",
    desc: "Ask in Hindi, get answers in Hindi. Seamless Hindi ↔ English RAG pipeline.",
    badge: "Hindi + English",
    cls: "multilingual",
  },
  {
    key: "agentic",
    icon: "🤖",
    title: "Agentic RAG",
    desc: "The AI doesn't just answer — it acts. Book facilities, raise grievances, check fee status.",
    badge: "Tool Calling",
    cls: "agentic",
  },
  {
    key: "realtime",
    icon: "⚡",
    title: "Real-time Ingestion",
    desc: "New document uploaded to docs/? The system detects it and re-indexes instantly.",
    badge: "Live Updates",
    cls: "realtime",
  },
];

const HomePage = ({ onNavigateToChat }) => {
  const [openFAQ, setOpenFAQ] = useState(null);
  const toggleFAQ = (i) => setOpenFAQ(openFAQ === i ? null : i);

  const teamMembers = [
    {
      name: "Shrinjay Shresth",
      role: "Head Developer",
      image: "/shrinjay.jpeg",
      description:
        "Data-driven problem solver blending machine learning expertise with backend engineering to build scalable, impactful solutions at the intersection of data, engineering, and community.",
      specialties: ["Machine Learning", "NLP", "Artificial Intelligence"],
    },
  ];

  const faqs = [
    {
      question: "What is AskGillu 2.0?",
      answer:
        "AskGillu 2.0 is the next-generation version of SRMU's AI assistant, now featuring multimodal understanding (images & PDFs), Hindi/English multilingual support, agentic tool calling, and real-time document ingestion — built on top of GraphRAG.",
    },
    {
      question: "Can I ask questions in Hindi?",
      answer:
        "Yes! Switch to हिंदी using the language toggle in the chat interface. Your query is translated to English, processed through the RAG pipeline, and the response is translated back to Hindi automatically.",
    },
    {
      question: "What can I upload?",
      answer:
        "You can upload images (PNG, JPG, JPEG) and PDFs — such as fee receipts, scanned notices, timetable images, or mark sheets. AskGillu's vision model extracts and understands the content.",
    },
    {
      question: "What are Agentic capabilities?",
      answer:
        "In Agentic Mode, AskGillu can take actions — like checking fee status, booking a facility, or raising a grievance — based on your request intent. It decides which tool to call automatically.",
    },
    {
      question: "What is real-time ingestion?",
      answer:
        "A file watcher monitors the docs/ folder. When a new PDF is dropped in, it is automatically chunked, embedded, and added to the knowledge graph — no manual re-indexing needed.",
    },
    {
      question: "How accurate is the information?",
      answer:
        "AskGillu uses official SRMU documents loaded into a hybrid vector database (Qdrant). For critical decisions, always confirm with official university departments.",
    },
    {
      question: "Is my data private?",
      answer:
        "Yes. Conversations are stored only in your browser session and are cleared on refresh. Uploaded images are processed in memory and not stored permanently.",
    },
    {
      question: "What's the difference between AskGillu 1.0 and 2.0?",
      answer:
        "AskGillu 1.0 (P2) proved GraphRAG outperforms Vector RAG by 72–83% on comprehensiveness. AskGillu 2.0 (P3) adds vision, language, agency, and real-time updates — making the system fully agentic.",
    },
  ];

  return (
    <div className="homepage">
      {/* ── NAVBAR ── */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <img src="/bot-icon-squirrel-90.png" alt="AskGillu" className="nav-logo" />
            <span className="nav-title">AskGillu</span>
            <span className="nav-version-badge">2.0</span>
          </div>
          <div className="nav-links">
            <a href="#home" className="nav-link">Home</a>
            <a href="#pillars" className="nav-link">Features</a>
            <a href="#about" className="nav-link">About</a>
            <a href="#team" className="nav-link">Team</a>
            <a href="#faq" className="nav-link">FAQ</a>
            <button onClick={onNavigateToChat} className="nav-cta-button">
              <MessageCircle size={16} />
              Launch Chat
            </button>
          </div>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section id="home" className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-eyebrow">
              <span className="hero-eyebrow-dot" />
              AskGillu 2.0 — Now Live
            </div>
            <h1 className="hero-title">
              Meet <span className="hero-highlight">AskGillu</span>
              <br />
              Your Smart SRMU
              <br />
              Assistant
            </h1>
            <p className="hero-subtitle">
              An agentic, multimodal, multilingual AI built for Shri Ramswaroop
              Memorial University — powered by GraphRAG and real-time ingestion.
            </p>

            <div className="hero-tags">
              <span className="hero-tag multimodal">📸 Multimodal</span>
              <span className="hero-tag multilingual">🌐 Multilingual</span>
              <span className="hero-tag agentic">🤖 Agentic RAG</span>
              <span className="hero-tag realtime">⚡ Real-time</span>
            </div>

            <div className="hero-actions">
              <button onClick={onNavigateToChat} className="hero-primary-btn">
                <MessageCircle size={20} />
                Start Chatting
              </button>
              <button
                onClick={() =>
                  document.getElementById("pillars")?.scrollIntoView({ behavior: "smooth" })
                }
                className="hero-secondary-btn"
              >
                <Zap size={18} />
                See Features
              </button>
            </div>
          </div>

          <div className="hero-visual">
            <div className="hero-card">
              <img
                src="/bot-icon-squirrel-90.png"
                alt="AskGillu"
                className="hero-image"
              />
              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">24/7</div>
                  <div className="stat-label">Available</div>
                </div>
                <div className="stat">
                  <div className="stat-number">4</div>
                  <div className="stat-label">AI Pillars</div>
                </div>
                <div className="stat">
                  <div className="stat-number">83%</div>
                  <div className="stat-label">Better RAG</div>
                </div>
              </div>
              <div className="hero-chat-preview">
                <div className="preview-msg user-msg">होस्टल की फीस कितनी है?</div>
                <div className="preview-msg ai-msg">🤖 Searching documents... ✅ Hostels fees are ₹45,000/year for standard rooms.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ── 4 PILLARS ── */}
      <section id="pillars" className="pillars-section">
        <div className="section-container">
          <p className="section-eyebrow">Core Capabilities</p>
          <h2 className="section-title">The 4 Pillars of AskGillu 2.0</h2>
          <p className="section-subtitle">
            Each pillar maps directly to SAP Business AI priorities —
            making AskGillu an enterprise-grade intelligent campus platform.
          </p>
          <div className="pillars-grid">
            {PILLARS.map((p) => (
              <div key={p.key} className={`pillar-card ${p.cls}`}>
                <div className="pillar-icon">{p.icon}</div>
                <div className="pillar-title">{p.title}</div>
                <div className="pillar-desc">{p.desc}</div>
                <span className="pillar-badge">{p.badge}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ── ABOUT ── */}
      <section id="about" className="about-section">
        <div className="section-container">
          <p className="section-eyebrow">About</p>
          <h2 className="section-title">About AskGillu</h2>
          <div className="about-content">
            <p className="about-description">
              AskGillu is SRMU's revolutionary AI-powered assistant built with
              cutting-edge GraphRAG technology. Version 2.0 proves — what if the
              system could also <em>act</em>, <em>see</em>, <em>update itself</em>, and speak
              your language?
            </p>
            <div className="about-highlights">
              <div className="highlight-item">
                <Star size={22} />
                <div>
                  <h4>GraphRAG Architecture</h4>
                  <p>72–83% better comprehensiveness vs standard vector RAG — knowledge graph preserves entity relationships across documents.</p>
                </div>
              </div>
              <div className="highlight-item">
                <BookOpen size={22} />
                <div>
                  <h4>Comprehensive Knowledge Base</h4>
                  <p>Loaded with complete SRMU documentation, policies, academic procedures, and campus facility information.</p>
                </div>
              </div>
              <div className="highlight-item">
                <Brain size={22} />
                <div>
                  <h4>Agentic Intelligence</h4>
                  <p>Intent classification routes your query to the right tool or knowledge pipeline — the AI decides what action to take.</p>
                </div>
              </div>
              <div className="highlight-item">
                <Globe size={22} />
                <div>
                  <h4>Always Available, Always Fresh</h4>
                  <p>24/7 availability with real-time document ingestion — the knowledge base stays current without manual intervention.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ── TEAM ── */}
      <section id="team" className="team-section">
        <div className="section-container">
          <p className="section-eyebrow">The Team</p>
          <h2 className="section-title">Meet Our Team</h2>
          <p className="section-subtitle">
            The minds behind AskGillu, dedicated to enhancing university experiences through AI.
          </p>
          <div className="team-grid">
            {teamMembers.map((member, i) => (
              <div key={i} className="team-card">
                <div className="team-image-container">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="team-image"
                  />
                </div>
                <div>
                  <h3 className="team-name">{member.name}</h3>
                  <p className="team-role">{member.role}</p>
                  <p className="team-description">{member.description}</p>
                  <div className="team-specialties">
                    {member.specialties.map((s, idx) => (
                      <span key={idx} className="specialty-tag">{s}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="section-divider" />

      {/* ── FAQ ── */}
      <section id="faq" className="faq-section">
        <div className="section-container">
          <p className="section-eyebrow">FAQ</p>
          <h2 className="section-title">Frequently Asked Questions</h2>
          <p className="section-subtitle">Everything you need to know about AskGillu 2.0</p>
          <div className="faq-container">
            {faqs.map((faq, i) => (
              <div key={i} className="faq-item">
                <button className="faq-question" onClick={() => toggleFAQ(i)}>
                  <span>{faq.question}</span>
                  {openFAQ === i ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>
                {openFAQ === i && (
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-brand">
                <img src="/bot-icon-squirrel-90.png" alt="AskGillu" className="footer-logo" />
                <span className="footer-title">AskGillu</span>
              </div>
              <p className="footer-description">
                Agentic · Multimodal · Multilingual AI for SRMU.
                Available 24/7 to help you navigate university life.
              </p>
              <button onClick={onNavigateToChat} className="footer-cta">
                <MessageCircle size={16} />
                Chat with AskGillu
              </button>
            </div>

            <div className="footer-section">
              <h4 className="footer-heading">Quick Links</h4>
              <ul className="footer-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#pillars">Features</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#team">Team</a></li>
                <li><a href="#faq">FAQ</a></li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-heading">University</h4>
              <ul className="footer-links">
                <li><a href="https://srmu.ac.in" target="_blank" rel="noopener noreferrer">SRMU Website</a></li>
                <li><a href="https://srmu.ac.in/admissions" target="_blank" rel="noopener noreferrer">Admissions</a></li>
                <li><a href="https://srmu.ac.in/academics" target="_blank" rel="noopener noreferrer">Academics</a></li>
                <li><a href="https://srmu.ac.in/placements" target="_blank" rel="noopener noreferrer">Placements</a></li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-heading">Contact SRMU</h4>
              <div className="contact-info">
                <div className="contact-item">
                  <MapPin size={15} />
                  <span>Lucknow-Deva Road, Barabanki, UP</span>
                </div>
                <div className="contact-item">
                  <Phone size={15} />
                  <span>+91-5248-270270</span>
                </div>
                <div className="contact-item">
                  <Mail size={15} />
                  <span>info@srmu.ac.in</span>
                </div>
              </div>
            </div>
          </div>

          <div className="footer-bottom">
            <p>© 2025 Shri Ramswaroop Memorial University. All rights reserved.</p>
            <div className="footer-pills">
              <span className="footer-pill">Multimodal</span>
              <span className="footer-pill">Multilingual</span>
              <span className="footer-pill">Agentic</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
