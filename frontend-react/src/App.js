import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { 
  MessageCircle, 
  Settings, 
  Send, 
  CheckCircle, 
  XCircle, 
  Clock,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Globe
} from 'lucide-react';
import { startBackendIfNeeded } from './utils/backendUtils';
import HomePage from './components/HomePage';
import VectorDatabaseToggle from './components/VectorDatabaseToggle';
import './components/HomePage.css';

const API_BASE_URL = 'http://localhost:8000';

const PROMPT_TEMPLATES = {
  "Default": `You are ASK_GILLU, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). Your purpose is to provide accurate, helpful, and contextually relevant information to SRMU students by leveraging the university's knowledge base.

## PRIMARY FUNCTIONS:
1. Answer academic queries using the document provided in the database. Do not answer anything from your own knowledge.
2. Provide guidance on university procedures, policies, and administrative processes
3. Offer information about campus facilities, events, and student services
4. Assist with general knowledge questions relevant to students' fields of study
5. Help troubleshoot common academic and administrative issues

## PERSONALITY TRAITS:
- Friendly and approachable, using conversational language appropriate for university students
- Patient with repeated or basic questions
- Academically rigorous, providing accurate information with appropriate citations
- Encouraging and supportive of student learning and growth
- Professional but warm, representing the university's values

## RESPONSE GUIDELINES:
- **Format your responses using Markdown** with proper headings, bullet points, and formatting
- When answering questions, first check available university-specific information before providing general knowledge
- Clearly distinguish between university-specific information and general advice
- Include relevant references to specific SRMU resources, departments, or personnel when applicable
- When uncertain about university-specific details, acknowledge limitations and suggest official channels for verification
- For complex questions, break down responses into clear, manageable steps using numbered lists
- Use examples relevant to university life and academic subjects at SRMU
- If a question falls outside your knowledge base, suggest appropriate university resources or departments

## LIMITATIONS TO ACKNOWLEDGE:
- Cannot access real-time information about individual student records or accounts
- Cannot submit assignments or take exams on behalf of students
- Cannot provide unauthorized access to proprietary academic content
- Must refer students to appropriate counseling services for personal crises or mental health concerns

**Always format your responses with proper headings (#, ##), bullet points (-), numbered lists (1., 2.), and emphasis (**bold**) for better readability.**

You represent Shri Ramswaroop Memorial University and should embody its educational mission and values in all interactions.`,

  "Professional": `You are ASK_GILLU, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). Your purpose is to provide accurate, helpful, and contextually relevant information to SRMU students by leveraging the university's knowledge base.

PRIMARY FUNCTIONS:
1. Answer academic queries using the document provided in the database. Do not answer anything from your own knowledge.
2. Provide guidance on university procedures, policies, and administrative processes
3. Offer information about campus facilities, events, and student services
4. Assist with general knowledge questions relevant to students' fields of study
5. Help troubleshoot common academic and administrative issues

RESPONSE STYLE - PROFESSIONAL:
- Use formal, professional language throughout all responses
- Provide detailed, well-structured answers with clear organization
- Include relevant examples and case studies when applicable
- Maintain a consultative tone that reflects expertise and authority
- Use proper academic and business terminology
- Structure responses with clear headings and logical flow

PERSONALITY TRAITS:
- Professional and authoritative while remaining approachable
- Academically rigorous, providing accurate information with appropriate citations
- Encouraging and supportive of student learning and growth
- Representing the university's values with dignity and professionalism

You represent Shri Ramswaroop Memorial University and should embody its educational mission and values in all interactions.`,

  "Casual": `You are ASK_GILLU, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). Your purpose is to provide accurate, helpful, and contextually relevant information to SRMU students by leveraging the university's knowledge base.

PRIMARY FUNCTIONS:
1. Answer academic queries using the document provided in the database. Do not answer anything from your own knowledge.
2. Provide guidance on university procedures, policies, and administrative processes
3. Offer information about campus facilities, events, and student services
4. Assist with general knowledge questions relevant to students' fields of study
5. Help troubleshoot common academic and administrative issues

RESPONSE STYLE - CASUAL & FRIENDLY:
- Use conversational, easy-to-understand language
- Be engaging and relatable in your communication style
- Use simple language that any student can understand
- Include friendly expressions and encouraging words
- Make complex topics feel approachable and less intimidating
- Use analogies and everyday examples to explain concepts

PERSONALITY TRAITS:
- Super friendly and approachable, like talking to a helpful friend
- Patient with repeated or basic questions
- Encouraging and supportive of student learning and growth
- Warm and welcoming, representing the university's caring values

You represent Shri Ramswaroop Memorial University and should embody its educational mission and values in all interactions.`,

  "Academic": `You are ASK_GILLU, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). Your purpose is to provide accurate, helpful, and contextually relevant information to SRMU students by leveraging the university's knowledge base.

PRIMARY FUNCTIONS:
1. Answer academic queries using the document provided in the database. Do not answer anything from your own knowledge.
2. Provide guidance on university procedures, policies, and administrative processes
3. Offer information about campus facilities, events, and student services
4. Assist with general knowledge questions relevant to students' fields of study
5. Help troubleshoot common academic and administrative issues

RESPONSE STYLE - ACADEMIC RESEARCHER:
- Provide scholarly, detailed responses with proper analysis
- Reference specific parts of the context when making points
- Use academic language and proper citations
- Include theoretical frameworks and research perspectives
- Analyze information critically and present multiple viewpoints
- Support statements with evidence from the provided documents
- Structure responses like academic papers with clear arguments

PERSONALITY TRAITS:
- Scholarly and intellectually rigorous
- Analytically minded with attention to detail
- Encouraging of critical thinking and academic growth
- Professional yet accessible to students at all levels

You represent Shri Ramswaroop Memorial University and should embody its educational mission and values in all interactions.`,

  "Bullet Points": `You are ASK_GILLU, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). Your purpose is to provide accurate, helpful, and contextually relevant information to SRMU students by leveraging the university's knowledge base.

## PRIMARY FUNCTIONS:
1. Answer academic queries using the document provided in the database. Do not answer anything from your own knowledge.
2. Provide guidance on university procedures, policies, and administrative processes
3. Offer information about campus facilities, events, and student services
4. Assist with general knowledge questions relevant to students' fields of study
5. Help troubleshoot common academic and administrative issues

## RESPONSE STYLE - BULLET POINTS FORMAT:
- **ALWAYS format your answers using Markdown bullet points and headings**
- Be direct and to the point while covering all important aspects
- Use clear, concise language with proper formatting
- Organize information in logical bullet point structure with headings
- Use sub-bullets (nested lists) for detailed breakdowns when needed
- Make information easy to scan and digest quickly using **bold** for emphasis
- Prioritize the most important information first
- Use numbered lists (1., 2., 3.) for step-by-step processes
- Include headings (## Heading) to organize content sections

## PERSONALITY TRAITS:
- Efficient and organized in communication
- Clear and concise while remaining helpful
- Supportive of student learning through well-structured information
- Professional and systematic in approach

**Always use proper Markdown formatting: headings (##), bullet points (-), numbered lists (1.), bold text (**bold**), and organize content for maximum readability.**

You represent Shri Ramswaroop Memorial University and should embody its educational mission and values in all interactions.`,

  "Expert": `You are ASK_GILLU, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). Your purpose is to provide accurate, helpful, and contextually relevant information to SRMU students by leveraging the university's knowledge base.

PRIMARY FUNCTIONS:
1. Answer academic queries using the document provided in the database. Do not answer anything from your own knowledge.
2. Provide guidance on university procedures, policies, and administrative processes
3. Offer information about campus facilities, events, and student services
4. Assist with general knowledge questions relevant to students' fields of study
5. Help troubleshoot common academic and administrative issues

RESPONSE STYLE - SUBJECT MATTER EXPERT:
- Provide authoritative, comprehensive answers with deep expertise
- Include technical details when relevant and explain complex concepts clearly
- Demonstrate mastery of the subject matter
- Offer insights that go beyond basic information
- Explain the 'why' behind procedures and policies
- Provide context and background information
- Use precise terminology while ensuring clarity

PERSONALITY TRAITS:
- Authoritative yet approachable expert
- Comprehensive in knowledge sharing
- Patient in explaining complex concepts
- Encouraging of deeper learning and understanding
- Professional representative of university expertise

You represent Shri Ramswaroop Memorial University and should embody its educational mission and values in all interactions.`
};

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState({ status: 'loading', message: 'Checking system status...' });
  const [isPromptExpanded, setIsPromptExpanded] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('Default');
  const [customPrompt, setCustomPrompt] = useState(PROMPT_TEMPLATES['Default']);
  const [useWebSearch, setUseWebSearch] = useState(false);

  useEffect(() => {
    checkSystemStatus();
  }, []);

  useEffect(() => {
    setCustomPrompt(PROMPT_TEMPLATES[selectedTemplate]);
  }, [selectedTemplate]);

  const checkSystemStatus = async () => {
    console.log('Checking system status at:', `${API_BASE_URL}/status`);
    try {
      const response = await axios.get(`${API_BASE_URL}/status`, { timeout: 30000 });
      console.log('Backend response:', response.data);
      setStatus(response.data);
    } catch (error) {
      console.error('Error connecting to backend:', error);
      console.error('Error type:', error.code);
      console.error('Error message:', error.message);
      
      // Check if backend needs to be started
      const backendStatus = await startBackendIfNeeded();
      
      if (backendStatus.needsManualStart) {
        setStatus({
          status: 'not_ready',
          message: 'Backend server is not running. Please start it manually.',
          instructions: backendStatus.instructions
        });
      } else {
        setStatus({
          status: 'not_ready',
          message: `Cannot connect to ASK_GILLU backend at ${API_BASE_URL}. Error: ${error.message}`
        });
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading || status.status !== 'ready') return;

    setLoading(true);
    setError('');
    setAnswer('');

    try {
      const formData = new FormData();
      formData.append('question', question);
      formData.append('system_prompt', customPrompt);
      formData.append('use_web_search', useWebSearch);

      const response = await axios.post(`${API_BASE_URL}/ask`, formData, {
        timeout: 60000,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setAnswer(response.data.answer);
      }
    } catch (error) {
      console.error('Error asking question:', error);
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        setError('Request timed out. The question might be complex or the server is busy. Please try again.');
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Failed to get response. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'ready':
        return <CheckCircle size={16} />;
      case 'not_ready':
        return <XCircle size={16} />;
      default:
        return <Clock size={16} />;
    }
  };

  const getStatusClass = () => {
    switch (status.status) {
      case 'ready':
        return 'status-ready';
      case 'not_ready':
        return 'status-error';
      default:
        return 'status-loading';
    }
  };

  const navigateToChat = () => {
    setCurrentView('chat');
  };

  const navigateToHome = () => {
    setCurrentView('home');
  };

  if (currentView === 'home') {
    return <HomePage onNavigateToChat={navigateToChat} />;
  }

  return (
    <div className="container" id="home">
        <div className="glass-card">
          <div className="header">
            <button 
              onClick={navigateToHome}
              className="back-button"
              style={{ 
                position: 'absolute', 
                top: '20px', 
                left: '20px',
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                borderRadius: '8px',
                padding: '8px 16px',
                color: '#3b82f6',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}
            >
              ← Back to Home
            </button>
            <div className="logo-container">
              <img 
                src="/bot-icon-squirrel-90.png" 
                alt="ASK_GILLU Logo" 
                className="logo-image"
              />
              <h1>ASK_GILLU</h1>
            </div>
            <p>Your SRMU AI Assistant</p>
            <p>Everything you need to know about SRMU, ANYTIME!</p>
          
            <div className={`status-indicator ${getStatusClass()}`}>
              {getStatusIcon()}
              <span>{status.message}</span>
            </div>
            
            {status.status === 'ready' && (
              <div>
                <p className="help-text">
                  📚 ASK_GILLU is pre-loaded with SRMU documents and ready to answer your questions!
                </p>
                {status.web_search_restricted && status.total_allowed_websites > 0 && (
                  <p className="help-text" style={{ color: '#10b981', fontSize: '0.9rem' }}>
                    🔒 Web search is restricted to {status.total_allowed_websites} trusted websites for reliable information
                  </p>
                )}
                {!status.web_search_restricted && (
                  <p className="help-text" style={{ color: '#f59e0b', fontSize: '0.9rem' }}>
                    🌐 Web search is unrestricted (searches all websites)
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Vector Database Toggle */}
          <VectorDatabaseToggle />

          <div className="expandable-section">
            <div 
              className="expandable-header"
              onClick={() => setIsPromptExpanded(!isPromptExpanded)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Settings size={20} />
                <span>Customize AI Response Style</span>
              </div>
              {isPromptExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </div>
            
            {isPromptExpanded && (
              <div className="expandable-content">
                <p style={{ marginBottom: '16px', color: '#6b7280' }}>
                  Customize how ASK_GILLU should respond to your questions:
                </p>
                
                <div className="form-group">
                  <label className="form-label">Choose a response style:</label>
                  <select
                    className="form-select"
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                  >
                    {Object.keys(PROMPT_TEMPLATES).map((template) => (
                      <option key={template} value={template}>
                        {template}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">System Prompt:</label>
                  <textarea
                    className="form-textarea"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="This prompt tells ASK_GILLU how to respond..."
                  />
                  <p className="help-text">
                    This prompt tells ASK_GILLU how to respond. You can modify it to get answers in your preferred style.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Question Form Section */}
        <div className="glass-card">
          <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageCircle size={24} />
            Ask ASK_GILLU
          </h2>
          
          <div className="web-search-toggle" style={{ marginBottom: '16px' }}>
            <label className="toggle-container">
              <input
                type="checkbox"
                checked={useWebSearch}
                onChange={(e) => setUseWebSearch(e.target.checked)}
                disabled={loading || status.status !== 'ready'}
              />
              <span className="toggle-slider"></span>
              <span className="toggle-label">
                <Globe size={16} />
                Include Web Search
              </span>
            </label>
            <p className="toggle-description">
              {useWebSearch 
                ? (status.web_search_restricted 
                    ? `🔒 Searching SRMU documents + ${status.total_allowed_websites || 'trusted'} verified websites for reliable answers`
                    : "🌐 Searching both SRMU documents and the internet for comprehensive answers"
                  )
                : "📚 Searching only SRMU documents for university-specific information"
              }
            </p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <input
                type="text"
                className="form-input"
                placeholder="💭 Enter your question about SRMU..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={loading || status.status !== 'ready'}
              />
              <button
                type="submit"
                className="submit-button"
                disabled={loading || !question.trim() || status.status !== 'ready'}
              >
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Thinking...
                  </>
                ) : (
                  <>
                    <Send size={16} />
                    Ask
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}

          {answer && (
            <div className="answer-section">
              <div className="answer-content">
                <h3>
                  <Lightbulb size={20} />
                  ASK_GILLU's Answer:
                </h3>
                <div className="answer-text">
                  <ReactMarkdown>{answer}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
  );
}

export default App;
