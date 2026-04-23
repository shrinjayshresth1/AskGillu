import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import { ThumbsUp, ThumbsDown, Check } from "lucide-react";
import API_BASE_URL from "../config";

/**
 * ChatMessage — renders a single message bubble (user or AI)
 * Props:
 *   role        : "user" | "ai"
 *   content     : string (markdown for AI, plain for user)
 *   timestamp   : Date
 *   sources     : { docs, web, image, tool, cached } (booleans)
 *   agentAction : { tool_used, result } | null
 *   isTyping    : boolean (animated dots when AI is streaming)
 *   imageUrl    : string | null (preview of uploaded image in user bubble)
 *   originalQuestion: string (the user question that prompted this AI response)
 */
const ChatMessage = ({
  role,
  content,
  timestamp,
  sources = {},
  agentAction = null,
  isTyping = false,
  imageUrl = null,
  originalQuestion = "",
}) => {
  const isUser = role === "user";
  const timeStr = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "";

  const [feedbackState, setFeedbackState] = useState(null); // null, "form", "submitted"
  const [missingInfo, setMissingInfo] = useState("");
  const [suggestion, setSuggestion] = useState("");

  const handlePositiveFeedback = async () => {
    setFeedbackState("submitted");
    try {
      const fd = new FormData();
      fd.append("question", originalQuestion || "unknown");
      fd.append("rating", "5");
      fd.append("feedback_type", "relevant");
      await axios.post(`${API_BASE_URL}/api/feedback`, fd);
    } catch (e) {
      console.error("Failed to submit feedback", e);
    }
  };

  const submitNegativeFeedback = async () => {
    setFeedbackState("submitted");
    try {
      const fd = new FormData();
      fd.append("question", originalQuestion || "unknown");
      fd.append("rating", "1");
      fd.append("feedback_type", "irrelevant");
      if (missingInfo) fd.append("missing_info", missingInfo);
      if (suggestion) fd.append("suggested_improvement", suggestion);
      await axios.post(`${API_BASE_URL}/api/feedback`, fd);
    } catch (e) {
      console.error("Failed to submit feedback", e);
    }
  };

  return (
    <div className={`message-row ${isUser ? "user-row" : ""}`}>
      {/* Avatar */}
      <div className={`message-avatar ${isUser ? "user-avatar" : "ai-avatar"}`}>
        {isUser ? (
          "U"
        ) : (
          <img src="/bot-icon-squirrel-90.png" alt="AskGillu" />
        )}
      </div>

      {/* Body */}
      <div className="message-body">
        {/* Agent action pill (AI only) */}
        {!isUser && agentAction && (
          <div className="agent-action-pill">
            🔧 Agent took action:{" "}
            <strong>{agentAction.tool_used}</strong>
            {agentAction.result && (
              <span style={{ opacity: 0.8, fontWeight: 400 }}>
                {" "}→ {agentAction.result}
              </span>
            )}
          </div>
        )}

        {/* Image preview (user bubble) */}
        {isUser && imageUrl && (
          <div style={{ marginBottom: 6 }}>
            <div className="file-preview-chip">
              <img src={imageUrl} alt="uploaded" />
              <span>Image attached</span>
            </div>
          </div>
        )}

        {/* Bubble */}
        {isTyping ? (
          <div className="typing-indicator">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        ) : (
          <div className={`message-bubble ${isUser ? "bubble-user" : "bubble-ai"}`}>
            {isUser ? (
              <span>{content}</span>
            ) : (
              <div className="md-content">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            )}
          </div>
        )}

        {/* Meta row & Feedback */}
        <div className="message-meta">
          <span className="message-time">{timeStr}</span>
          {/* Source badges for AI messages */}
          {!isUser && !isTyping && (
            <div className="source-badges" style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
              {sources.docs   && <span className="source-badge docs">📄 Documents</span>}
              {sources.web    && <span className="source-badge web">🌐 Web</span>}
              {sources.image  && <span className="source-badge image">🖼️ Image</span>}
              {sources.tool   && <span className="source-badge tool">🔧 Tool</span>}
              {sources.cached && <span className="source-badge cached">⚡ Cached</span>}
              
              {/* Feedback Buttons */}
              {!feedbackState && (
                <div style={{ display: "flex", gap: 4, marginLeft: "auto" }}>
                  <button className="icon-btn" onClick={handlePositiveFeedback} title="Helpful">
                    <ThumbsUp size={14} />
                  </button>
                  <button className="icon-btn" onClick={() => setFeedbackState("form")} title="Not Helpful">
                    <ThumbsDown size={14} />
                  </button>
                </div>
              )}
              {feedbackState === "submitted" && (
                <span style={{ fontSize: "0.75rem", color: "var(--accent-green)", marginLeft: "auto", display: "flex", alignItems: "center", gap: 4 }}>
                  <Check size={12} /> Thanks for the feedback!
                </span>
              )}
            </div>
          )}
        </div>

        {/* Negative Feedback Form */}
        {feedbackState === "form" && (
          <div style={{ 
            marginTop: 8, 
            padding: 12, 
            background: "var(--surface-color)", 
            borderRadius: 8, 
            border: "1px solid var(--border-color)",
            display: "flex",
            flexDirection: "column",
            gap: 8,
            maxWidth: 400
          }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 500 }}>What went wrong?</span>
            <input 
              type="text" 
              placeholder="What information is missing?" 
              value={missingInfo}
              onChange={(e) => setMissingInfo(e.target.value)}
              style={{ padding: "6px 10px", fontSize: "0.85rem", borderRadius: 6, border: "1px solid var(--border-color)", background: "var(--bg-color)", color: "var(--text-color)" }}
            />
            <input 
              type="text" 
              placeholder="Any suggestions to improve?" 
              value={suggestion}
              onChange={(e) => setSuggestion(e.target.value)}
              style={{ padding: "6px 10px", fontSize: "0.85rem", borderRadius: 6, border: "1px solid var(--border-color)", background: "var(--bg-color)", color: "var(--text-color)" }}
            />
            <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
              <button 
                onClick={() => setFeedbackState(null)}
                style={{ padding: "4px 10px", fontSize: "0.8rem", cursor: "pointer", background: "transparent", border: "none", color: "var(--text-secondary)" }}
              >
                Cancel
              </button>
              <button 
                onClick={submitNegativeFeedback}
                style={{ padding: "4px 12px", fontSize: "0.8rem", cursor: "pointer", background: "var(--accent-purple)", color: "white", border: "none", borderRadius: 4 }}
              >
                Submit
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
