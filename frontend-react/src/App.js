import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import {
  Send,
  Settings,
  Globe,
  ChevronDown,
  ChevronUp,
  Paperclip,
  ArrowLeft,
  Trash2,
} from "lucide-react";
import { startBackendIfNeeded } from "./utils/backendUtils";
import HomePage from "./components/HomePage";
import ChatMessage from "./components/ChatMessage";
import VectorDatabaseToggle from "./components/VectorDatabaseToggle";
import "./components/HomePage.css";

import API_BASE_URL from "./config";

const PROMPT_TEMPLATES = {
  Default: `You are AskGillu, the official AI assistant for Shri Ramswaroop Memorial University (SRMU). You MUST answer ONLY using the provided context. If the context does not contain enough information to answer, say "I don't have enough information in my documents to answer that." Do NOT make up facts, statistics, names, dates, or any information not explicitly present in the context. Be friendly, accurate, and use markdown formatting.`,
  Professional: `You are AskGillu, SRMU's official AI assistant. Use formal, professional language with clear structure and headings. Answer ONLY from the provided context — do NOT use external knowledge or make up any information. If the context is insufficient, clearly state that you don't have the information.`,
  Casual: `You are AskGillu, SRMU's friendly AI assistant. Use conversational, easy-to-understand language. Answer ONLY from the provided context. If you can't find the answer in the context, be honest and say so — never make things up. Keep answers clear and encouraging.`,
  Academic: `You are AskGillu, SRMU's academic AI assistant. Provide scholarly, detailed responses referencing specific sections from the provided context only. Do NOT fabricate any facts, citations, or statistics. If the context lacks information, state explicitly what is missing.`,
  "Bullet Points": `You are AskGillu, SRMU's AI assistant. ALWAYS format responses in Markdown bullet points and numbered lists. Use bold for key terms. Answer ONLY from the provided context. NEVER fabricate information — if the answer isn't in the context, say so clearly.`,
};

const SUGGESTION_QUERIES = [
  "What are the hostel fee details?",
  "Tell me about the MBA program",
  "What are the exam policies?",
  "How do I apply for placement?",
];

function App() {
  const [currentView, setCurrentView] = useState("home");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ status: "loading", message: "Checking…" });
  const [language, setLanguage] = useState("en"); // "en" | "hi"
  const [agenticMode, setAgenticMode] = useState(false);
  const [useWebSearch, setUseWebSearch] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState("Default");
  const [customPrompt, setCustomPrompt] = useState(PROMPT_TEMPLATES["Default"]);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  /* ── Scroll to bottom ── */
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  /* ── System status poll ── */
  useEffect(() => {
    checkSystemStatus();
  }, []);

  useEffect(() => {
    setCustomPrompt(PROMPT_TEMPLATES[selectedTemplate]);
  }, [selectedTemplate]);

  const checkSystemStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/status`, { timeout: 30000 });
      setStatus(res.data);
    } catch (err) {
      const bs = await startBackendIfNeeded();
      setStatus({
        status: "not_ready",
        message: bs.needsManualStart
          ? "Backend not running. Start it manually."
          : `Cannot connect: ${err.message}`,
      });
    }
  };

  /* ── Auto-resize textarea ── */
  const handleTextareaInput = (e) => {
    setInputText(e.target.value);
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
    }
  };

  /* ── Image selection ── */
  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  /* ── Submit ── */
  const handleSubmit = async (e) => {
    e?.preventDefault();
    const trimmed = inputText.trim();
    if ((!trimmed && !imageFile) || loading || status.status !== "ready") return;

    const userMsg = {
      role: "user",
      content: trimmed || "(image attached)",
      timestamp: new Date(),
      imageUrl: imagePreview,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    clearImage();
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    // Typing indicator
    const typingId = Date.now();
    setMessages((prev) => [
      ...prev,
      { role: "ai", id: typingId, content: "", isTyping: true, timestamp: new Date() },
    ]);
    setLoading(true);

    try {
      let responseData;

      if (imageFile && trimmed) {
        /* ── Image + text ── */
        const fd = new FormData();
        fd.append("image", imageFile);
        fd.append("question", trimmed);
        fd.append("system_prompt", customPrompt);
        fd.append("language", language);
        const res = await axios.post(`${API_BASE_URL}/ask-image`, fd, {
          timeout: 90000,
          headers: { "Content-Type": "multipart/form-data" },
        });
        responseData = res.data;
      } else if (agenticMode) {
        /* ── Agentic mode ── */
        const fd = new FormData();
        fd.append("question", trimmed);
        fd.append("system_prompt", customPrompt);
        fd.append("language", language);
        const res = await axios.post(`${API_BASE_URL}/ask-agentic`, fd, {
          timeout: 90000,
          headers: { "Content-Type": "multipart/form-data" },
        });
        responseData = res.data;
      } else {
        /* ── Standard RAG ── */
        const fd = new FormData();
        fd.append("question", trimmed);
        fd.append("system_prompt", customPrompt);
        fd.append("use_web_search", useWebSearch);
        fd.append("language", language);
        const res = await axios.post(`${API_BASE_URL}/ask`, fd, {
          timeout: 90000,
          headers: { "Content-Type": "multipart/form-data" },
        });
        responseData = res.data;
      }

      const su = responseData.sources_used || {};
      const adv = responseData.advanced_rag_features || {};
      const aiMsg = {
        role: "ai",
        content: responseData.error || responseData.answer || "No response received.",
        timestamp: new Date(),
        sources: {
          docs:   (adv.documents_found || 0) > 0,
          web:    su.web_search || false,
          image:  !!imageFile,
          tool:   !!(responseData.agent_action?.tool_used),
          cached: adv.cache_hit || false,
        },
        agentAction: responseData.agent_action || null,
        originalQuestion: trimmed,
      };

      setMessages((prev) =>
        prev.map((m) => (m.id === typingId ? aiMsg : m))
      );
    } catch (err) {
      const errMsg = {
        role: "ai",
        content: err.code === "ECONNABORTED" || err.message.includes("timeout")
          ? "⏱️ Request timed out. The server may be busy — please try again."
          : err.response?.data?.detail || "❌ Failed to get a response. Please check your connection.",
        timestamp: new Date(),
        sources: {},
      };
      setMessages((prev) =>
        prev.map((m) => (m.id === typingId ? errMsg : m))
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestion = (q) => {
    setInputText(q);
    textareaRef.current?.focus();
  };

  const clearChat = () => setMessages([]);

  /* ── Status helpers ── */
  const statusClass =
    status.status === "ready" ? "ready" :
    status.status === "not_ready" ? "error" : "loading";

  /* ── HOME ── */
  if (currentView === "home") {
    return <HomePage onNavigateToChat={() => setCurrentView("chat")} />;
  }

  /* ── CHAT ── */
  return (
    <div className="chat-root">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header-brand">
          <img src="/bot-icon-squirrel-90.png" alt="AskGillu" className="chat-logo" />
          <span className="chat-brand-name">AskGillu</span>
          <span className="version-badge">2.0</span>
        </div>

        <div className="chat-header-controls">
          {/* Status dot */}
          <div className="status-dot-wrap">
            <div className={`status-dot ${statusClass}`} />
            <span>
              {status.status === "ready"
                ? `${status.documents_count || "–"} docs`
                : status.status === "loading" ? "Connecting…" : "Offline"}
            </span>
          </div>

          {/* Language toggle */}
          <div className="lang-toggle">
            <button
              className={`lang-btn ${language === "en" ? "active" : ""}`}
              onClick={() => setLanguage("en")}
            >EN</button>
            <button
              className={`lang-btn ${language === "hi" ? "active" : ""}`}
              onClick={() => setLanguage("hi")}
            >हिं</button>
          </div>

          {/* Agentic toggle */}
          <label className="agent-toggle-wrap" title="Enable Agentic Mode">
            <input
              type="checkbox"
              checked={agenticMode}
              onChange={(e) => setAgenticMode(e.target.checked)}
              disabled={loading}
            />
            <div className="agent-slider" />
            <span>🤖 Agentic</span>
          </label>

          {/* Clear + Back */}
          {messages.length > 0 && (
            <button className="icon-btn back-btn" onClick={clearChat} title="Clear chat">
              <Trash2 size={15} />
            </button>
          )}
          <button className="back-btn" onClick={() => setCurrentView("home")}>
            <ArrowLeft size={15} />
            Home
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="chat-messages">
        <div className="messages-inner">
          {messages.length === 0 && (
            <div className="chat-empty">
              <img src="/bot-icon-squirrel-90.png" alt="AskGillu" className="chat-empty-icon" />
              <h2>
                {language === "hi"
                  ? "नमस्ते! मैं AskGillu हूँ 👋"
                  : "Hi, I'm AskGillu 👋"}
              </h2>
              <p>
                {language === "hi"
                  ? "SRMU के बारे में कुछ भी पूछें — हिंदी या English में।"
                  : "Ask me anything about SRMU — academics, campus life, policies & more."}
              </p>
              <div className="suggestion-chips">
                {SUGGESTION_QUERIES.map((q, i) => (
                  <button
                    key={i}
                    className="suggestion-chip"
                    onClick={() => handleSuggestion(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <ChatMessage key={i} {...msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="chat-input-wrap">
        <div className="input-area-inner">
          {/* Settings panel */}
          <div className="settings-panel">
            <button
              className="settings-toggle-btn"
              onClick={() => setSettingsOpen(!settingsOpen)}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <Settings size={14} />
                <span>Response Style</span>
                {selectedTemplate !== "Default" && (
                  <span style={{
                    fontSize: "0.7rem",
                    padding: "1px 8px",
                    background: "rgba(99,102,241,0.15)",
                    color: "var(--accent-light)",
                    borderRadius: 20,
                  }}>{selectedTemplate}</span>
                )}
              </div>
              {settingsOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {settingsOpen && (
              <div className="settings-body">
                {/* Vector DB toggle */}
                <VectorDatabaseToggle />

                <div className="settings-group">
                  <label className="settings-label">Response Style</label>
                  <select
                    className="settings-select"
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                  >
                    {Object.keys(PROMPT_TEMPLATES).map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>

                <div className="settings-group">
                  <label className="settings-label">System Prompt</label>
                  <textarea
                    className="settings-textarea"
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="Customize AI behaviour…"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Web search toggle row */}
          <div className="web-search-row">
            <label className="mini-toggle" style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={useWebSearch}
                onChange={(e) => setUseWebSearch(e.target.checked)}
                disabled={loading || agenticMode}
              />
              <div className="mini-slider" />
              <Globe size={14} style={{ color: "var(--text-secondary)" }} />
              <span className="toggle-label-text">Web Search</span>
            </label>
            <span className="toggle-desc">
              {agenticMode
                ? "🤖 Agentic mode active — tool dispatch enabled"
                : useWebSearch
                  ? status.web_search_restricted
                    ? `🔒 ${status.total_allowed_websites} trusted sites`
                    : "🌐 Unrestricted web search"
                  : "📚 Documents only"}
            </span>
          </div>

          {/* Image preview chip */}
          {imagePreview && (
            <div className="input-file-preview">
              <div className="file-preview-chip">
                <img src={imagePreview} alt="preview" />
                <span>{imageFile?.name || "Image"}</span>
                <button className="file-chip-remove" onClick={clearImage}>×</button>
              </div>
            </div>
          )}

          {/* Input row */}
          <form onSubmit={handleSubmit}>
            <div className="input-row">
              <textarea
                ref={textareaRef}
                className="chat-textarea"
                rows={1}
                placeholder={
                  language === "hi"
                    ? "SRMU के बारे में पूछें… (Shift+Enter for new line)"
                    : "Ask about SRMU… (Shift+Enter for new line)"
                }
                value={inputText}
                onChange={handleTextareaInput}
                onKeyDown={handleKeyDown}
                disabled={loading || status.status !== "ready"}
              />

              <div className="input-actions">
                {/* Image attach */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*,.pdf"
                  style={{ display: "none" }}
                  onChange={handleImageSelect}
                  disabled={loading}
                />
                <button
                  type="button"
                  className="icon-btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading || status.status !== "ready"}
                  title="Attach image or PDF"
                  style={{ color: imageFile ? "var(--accent-purple)" : undefined }}
                >
                  <Paperclip size={18} />
                </button>

                {/* Send */}
                <button
                  type="submit"
                  className="send-btn"
                  disabled={
                    loading ||
                    status.status !== "ready" ||
                    (!inputText.trim() && !imageFile)
                  }
                  title="Send (Enter)"
                >
                  {loading ? (
                    <span className="spinner" />
                  ) : (
                    <Send size={16} />
                  )}
                </button>
              </div>
            </div>
          </form>

          <div className="input-hint">
            <span>Enter to send · Shift+Enter for new line</span>
            <span className="hint-sep">·</span>
            <span>AskGillu 2.0</span>
            {agenticMode && (
              <>
                <span className="hint-sep">·</span>
                <span style={{ color: "var(--accent-orange)" }}>🤖 Agentic</span>
              </>
            )}
            {language === "hi" && (
              <>
                <span className="hint-sep">·</span>
                <span style={{ color: "var(--accent-green)" }}>🌐 हिंदी</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
