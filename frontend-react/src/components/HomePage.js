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
} from "lucide-react";

const HomePage = ({ onNavigateToChat }) => {
  const [openFAQ, setOpenFAQ] = useState(null);

  const toggleFAQ = (index) => {
    setOpenFAQ(openFAQ === index ? null : index);
  };

  const teamMembers = [
    {
      name: "Shrinjay Shresth",
      role: "Head Developer",
      image:
        "https://media.licdn.com/dms/image/v2/D4D03AQE7P7kmGAtwiw/profile-displayphoto-shrink_400_400/B4DZdOF7EvH4Ak-/0/1749361865606?e=1760572800&v=beta&t=UxLPH7V_kYlVHkvEFboF5u0MJuuVqzzXg3UEI7ekgTM",
      description:
        "Data-driven problem solver blending machine learning expertise with backend engineering to build scalable, impactful solutions at the intersection of data, engineering, and community.",
      specialties: ["Machine Learning", "NLP", "Artificial Intelligence"],
    },

    {
      name: "Mohd Tabish Khan",
      role: "Data Curator",
      image:
        "https://media.licdn.com/dms/image/v2/D4D03AQEIL9kSsX_99g/profile-displayphoto-shrink_400_400/B4DZZuBiRRG4Ag-/0/1745602619301?e=1760572800&v=beta&t=Lw0V7IKY8j0feDOLGkXbkxY9Ugzm62UxbLLJvXcY9wg",
      description:
        "Passionate software developer with strong expertise in building backend systems and AI-driven applications.",
      specialties: ["Full Stack Development", "UI/UX"],
    },
  ];

  const faqs = [
    {
      question: "What is ASK GILLU and how can it help me?",
      answer:
        "ASK GILLU is SRMU's official AI assistant designed to provide instant, accurate answers about university policies, procedures, academic programs, campus facilities, and student services. It's available 24/7 to help you navigate your university experience.",
    },
    {
      question: "What type of questions can I ask ASK GILLU?",
      answer:
        "You can ask about admission procedures, course requirements, exam schedules, fee structures, campus facilities, hostel information, placement opportunities, faculty details, academic calendars, library services, and much more. ASK GILLU has access to comprehensive SRMU documentation.",
    },
    {
      question: "Is ASK GILLU available 24/7?",
      answer:
        "Yes! ASK GILLU is available round the clock to assist you. Whether you need information at midnight before an exam or early morning about registration deadlines, ASK GILLU is always ready to help.",
    },
    {
      question: "How accurate is the information provided by ASK GILLU?",
      answer:
        "ASK GILLU uses official SRMU documents and verified information sources. The AI is regularly updated with the latest university policies and procedures to ensure accuracy. However, for critical decisions, we always recommend confirming with official university departments.",
    },
    {
      question: "Can ASK GILLU help with academic guidance?",
      answer:
        "Absolutely! ASK GILLU can provide information about course structures, degree requirements, academic policies, examination procedures, and general academic guidance based on official university documentation.",
    },
    {
      question: "Does ASK GILLU support multiple languages?",
      answer:
        "Currently, ASK GILLU primarily operates in English. However, the development team is working on expanding language support to better serve our diverse student community.",
    },
    {
      question: "How do I get started with ASK GILLU?",
      answer:
        "Simply click the 'Try ASK GILLU' button to access the chat interface. Type your question in natural language, and ASK GILLU will provide comprehensive answers based on SRMU's knowledge base.",
    },
    {
      question: "Is my conversation with ASK GILLU private?",
      answer:
        "Yes, your conversations are handled with privacy in mind. ASK GILLU doesn't store personal information from your queries, and interactions are designed to protect student privacy while providing helpful assistance.",
    },
  ];

  return (
    <div className="homepage">
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <img
              src="/bot-icon-squirrel-90.png"
              alt="ASK GILLU"
              className="nav-logo"
            />
            <span className="nav-title">ASK GILLU</span>
          </div>
          <div className="nav-links">
            <a href="#home" className="nav-link">
              Home
            </a>
            <a href="#about" className="nav-link">
              About
            </a>
            <a href="#team" className="nav-link">
              Team
            </a>
            <a href="#faq" className="nav-link">
              FAQ
            </a>
            <button onClick={onNavigateToChat} className="nav-cta-button">
              <MessageCircle size={18} />
              Try ASK GILLU
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Meet <span className="hero-highlight">ASK GILLU</span>
              <br />
              Your Smart SRMU Assistant
            </h1>
            <p className="hero-subtitle">
              Get instant, accurate answers about Shri Ramswaroop Memorial
              University. From admissions to academics, campus life to career
              guidance - ASK GILLU knows it all.
            </p>
            <div className="hero-features">
              <div className="hero-feature">
                <BookOpen size={24} />
                <span>Academic Guidance</span>
              </div>
              <div className="hero-feature">
                <Globe size={24} />
                <span>24/7 Availability</span>
              </div>
              <div className="hero-feature">
                <Award size={24} />
                <span>Official Information</span>
              </div>
            </div>
            <div className="hero-actions">
              <button onClick={onNavigateToChat} className="hero-primary-btn">
                <MessageCircle size={20} />
                Start Chatting with ASK GILLU
              </button>
              <button
                onClick={() =>
                  document
                    .getElementById("about")
                    .scrollIntoView({ behavior: "smooth" })
                }
                className="hero-secondary-btn"
              >
                Learn More
              </button>
            </div>
          </div>
          <div className="hero-visual">
            <div className="hero-card">
              <img
                src="/bot-icon-squirrel-90.png"
                alt="ASK GILLU"
                className="hero-image"
              />
              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">24/7</div>
                  <div className="stat-label">Available</div>
                </div>
                <div className="stat">
                  <div className="stat-number">1000+</div>
                  <div className="stat-label">Topics</div>
                </div>
                <div className="stat">
                  <div className="stat-number">Instant</div>
                  <div className="stat-label">Responses</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <div className="section-container">
          <h2 className="section-title">About ASK GILLU</h2>
          <div className="about-content">
            <div className="about-text">
              <p className="about-description">
                ASK GILLU is SRMU's revolutionary AI-powered assistant, designed
                to transform how students, faculty, and staff access university
                information. Built with cutting-edge natural language processing
                technology, ASK GILLU understands your questions and provides
                precise, helpful answers from our comprehensive knowledge base.
              </p>
              <div className="about-highlights">
                <div className="highlight-item">
                  <Star size={24} />
                  <div>
                    <h4>Intelligent Responses</h4>
                    <p>
                      Advanced AI technology ensures accurate and contextual
                      answers to your queries.
                    </p>
                  </div>
                </div>
                <div className="highlight-item">
                  <BookOpen size={24} />
                  <div>
                    <h4>Comprehensive Knowledge</h4>
                    <p>
                      Access to complete SRMU documentation, policies, and
                      procedures.
                    </p>
                  </div>
                </div>
                <div className="highlight-item">
                  <Globe size={24} />
                  <div>
                    <h4>Always Available</h4>
                    <p>Get help anytime, anywhere - ASK GILLU never sleeps.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section id="team" className="team-section">
        <div className="section-container">
          <h2 className="section-title">Meet Our Team</h2>
          <p className="section-subtitle">
            The brilliant minds behind ASK GILLU, dedicated to enhancing your
            university experience
          </p>
          <div className="team-grid">
            {teamMembers.map((member, index) => (
              <div key={index} className="team-card">
                <div className="team-image-container">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="team-image"
                  />
                </div>
                <div className="team-info">
                  <h3 className="team-name">{member.name}</h3>
                  <p className="team-role">{member.role}</p>
                  <p className="team-description">{member.description}</p>
                  <div className="team-specialties">
                    {member.specialties.map((specialty, idx) => (
                      <span key={idx} className="specialty-tag">
                        {specialty}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="faq-section">
        <div className="section-container">
          <h2 className="section-title">Frequently Asked Questions</h2>
          <p className="section-subtitle">
            Everything you need to know about ASK GILLU
          </p>
          <div className="faq-container">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <button
                  className="faq-question"
                  onClick={() => toggleFAQ(index)}
                >
                  <span>{faq.question}</span>
                  {openFAQ === index ? (
                    <ChevronUp size={20} />
                  ) : (
                    <ChevronDown size={20} />
                  )}
                </button>
                {openFAQ === index && (
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-brand">
                <img
                  src="/bot-icon-squirrel-90.png"
                  alt="ASK GILLU"
                  className="footer-logo"
                />
                <span className="footer-title">ASK GILLU</span>
              </div>
              <p className="footer-description">
                Your intelligent SRMU assistant, available 24/7 to help you
                navigate university life with ease.
              </p>
              <button onClick={onNavigateToChat} className="footer-cta">
                <MessageCircle size={18} />
                Chat with ASK GILLU
              </button>
            </div>

            <div className="footer-section">
              <h4 className="footer-heading">Quick Links</h4>
              <ul className="footer-links">
                <li>
                  <a href="#home">Home</a>
                </li>
                <li>
                  <a href="#about">About</a>
                </li>
                <li>
                  <a href="#team">Team</a>
                </li>
                <li>
                  <a href="#faq">FAQ</a>
                </li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-heading">University</h4>
              <ul className="footer-links">
                <li>
                  <a
                    href="https://srmu.ac.in"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    SRMU Website
                  </a>
                </li>
                <li>
                  <a
                    href="https://srmu.ac.in/admissions"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Admissions
                  </a>
                </li>
                <li>
                  <a
                    href="https://srmu.ac.in/academics"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Academics
                  </a>
                </li>
                <li>
                  <a
                    href="https://srmu.ac.in/placements"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Placements
                  </a>
                </li>
              </ul>
            </div>

            <div className="footer-section">
              <h4 className="footer-heading">Contact SRMU</h4>
              <div className="contact-info">
                <div className="contact-item">
                  <MapPin size={16} />
                  <span>Lucknow-Deva Road, Barabanki, UP</span>
                </div>
                <div className="contact-item">
                  <Phone size={16} />
                  <span>+91-5248-270270</span>
                </div>
                <div className="contact-item">
                  <Mail size={16} />
                  <span>info@srmu.ac.in</span>
                </div>
              </div>
            </div>
          </div>

          <div className="footer-bottom">
            <p>
              &copy; 2025 Shri Ramswaroop Memorial University. All rights
              reserved.
            </p>
            <p>ASK GILLU - Empowering Education with AI</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
