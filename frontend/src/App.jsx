
import { useState, useRef, useEffect } from "react";
import {
  Send,
  Plus,
  MessageSquare,
  Trash2,
  Bot,
  User,
  Sparkles,
  Menu,
  X,
  Copy,
  Check,
} from "lucide-react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Load all saved conversations from SQLite
  const refreshConversations = async () => {
    try {
      const response = await fetch(`${API_URL}/conversations`);

      if (!response.ok) {
        throw new Error("Unable to load chat history.");
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (err) {
      console.error("Chat history error:", err);
      setError("Unable to load saved conversations.");
    }
  };

  // Load saved history when the application opens
  useEffect(() => {
    refreshConversations();
  }, []);

  // Scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // Start a new chat without deleting saved chats
  const newChat = () => {
    setMessages([]);
    setConversationId(null);
    setInput("");
    setError("");
    inputRef.current?.focus();
  };

  // Open an existing conversation
  const openConversation = async (id) => {
    if (loading) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/conversation/${encodeURIComponent(id)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to open conversation."
        );
      }

      const formattedMessages = data.messages.map((item) => ({
        role: item.role === "user" ? "user" : "assistant",
        content: item.content,
      }));

      setConversationId(data.conversation_id);
      setMessages(formattedMessages);
      setInput("");

      if (window.innerWidth <= 768) {
        setSidebarOpen(false);
      }
    } catch (err) {
      setError(err.message || "Unable to load conversation.");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Delete a saved conversation
  const deleteConversation = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this conversation?"
    );

    if (!confirmed) return;

    try {
      const response = await fetch(
        `${API_URL}/conversation/${encodeURIComponent(id)}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to delete conversation."
        );
      }

      if (conversationId === id) {
        setMessages([]);
        setConversationId(null);
        setInput("");
      }

      await refreshConversations();
      setError("");
    } catch (err) {
      setError(err.message || "Unable to delete conversation.");
    }
  };

  // Send a message to Nova AI
  const sendMessage = async (e) => {
    e.preventDefault();

    const userMessage = input.trim();

    if (!userMessage || loading) return;

    setError("");
    setInput("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ]);

    setLoading(true);

    try {
      const payload = {
        message: userMessage,
      };

      if (conversationId) {
        payload.conversation_id = conversationId;
      }

      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to get a response. Please try again."
        );
      }

      if (!data.conversation_id || !data.response) {
        throw new Error("Invalid response received from the server.");
      }

      setConversationId(data.conversation_id);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);

      // Update sidebar with the newly saved conversation
      await refreshConversations();
    } catch (err) {
      setError(err.message || "Server connection failed.");

      setMessages((prev) => [
        ...prev,
        {
          role: "error",
          content: "I couldn't process your message. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // Copy assistant response
  const copyMessage = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 1500);
    } catch {
      setError("Unable to copy message.");
    }
  };

  return (
    <div className="app-container">

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>

        <div className="sidebar-header">
          <div className="brand">
            <div className="brand-icon">
              <Sparkles size={22} />
            </div>
            <span>Nova AI</span>
          </div>

          <button
            className="icon-button mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={19} />
          </button>
        </div>

        <button className="new-chat-button" onClick={newChat}>
          <Plus size={19} />
          <span>New Chat</span>
        </button>

        {/* Saved conversation history */}
        <div className="sidebar-section">
          <p className="section-label">CHAT HISTORY</p>

          {conversations.length > 0 ? (
            <div className="history-list">
              {conversations.map((chat) => (
                <div
                  className={`history-item ${
                    conversationId === chat.conversation_id ? "active" : ""
                  }`}
                  key={chat.conversation_id}
                >
                  <button
                    className="history-open-button"
                    onClick={() =>
                      openConversation(chat.conversation_id)
                    }
                    disabled={loading}
                    title={chat.title}
                  >
                    <MessageSquare size={16} />
                    <span>{chat.title || "New Chat"}</span>
                  </button>

                  <button
                    className="history-delete-button"
                    onClick={() =>
                      deleteConversation(chat.conversation_id)
                    }
                    title="Delete conversation"
                    aria-label="Delete conversation"
                    disabled={loading}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-history">
              No conversations yet
            </p>
          )}
        </div>

        <div className="sidebar-footer">
          <div className="profile-icon">N</div>
          <div className="profile-info">
            <strong>Nova AI</strong>
            <span>Gemini Powered</span>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="main-area">

        <header className="topbar">
          <button
            className="icon-button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            <Menu size={21} />
          </button>

          <div className="topbar-title">
            <Bot size={20} />
            <span>Nova AI Assistant</span>
          </div>

          <div className="status-indicator">
            <span className="status-dot"></span>
            Online
          </div>

          <button
            className="icon-button clear-button"
            onClick={() =>
              conversationId
                ? deleteConversation(conversationId)
                : newChat()
            }
            title={
              conversationId
                ? "Delete current conversation"
                : "New chat"
            }
          >
            <Trash2 size={18} />
          </button>
        </header>

        <section className="chat-area">

          {messages.length === 0 ? (
            <div className="welcome-screen">

              <div className="welcome-icon">
                <Sparkles size={34} />
              </div>

              <h1>
                Welcome to <span>Nova AI</span>
              </h1>

              <p className="welcome-description">
                Your intelligent AI assistant. Ask questions,
                explore ideas and have meaningful conversations.
              </p>

              <div className="suggestion-grid">
                <button
                  onClick={() => setInput("Introduce yourself.")}
                >
                  <Sparkles size={18} />
                  <strong>Introduce yourself</strong>
                  <span>Get to know Nova AI</span>
                </button>

                <button
                  onClick={() =>
                    setInput("Explain machine learning.")
                  }
                >
                  <Bot size={18} />
                  <strong>Learn something</strong>
                  <span>Explore AI and technology</span>
                </button>

                <button
                  onClick={() =>
                    setInput("Help me write Python code.")
                  }
                >
                  <MessageSquare size={18} />
                  <strong>Write code</strong>
                  <span>Get programming assistance</span>
                </button>

                <button
                  onClick={() => setInput("Give me study tips.")}
                >
                  <User size={18} />
                  <strong>Study smarter</strong>
                  <span>Improve your learning</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="messages-container">

              {messages.map((message, index) => (
                <div
                  className={`message-row ${
                    message.role === "error"
                      ? "assistant"
                      : message.role
                  }`}
                  key={index}
                >
                  <div className="message-avatar">
                    {message.role === "user" ? (
                      <User size={18} />
                    ) : (
                      <Bot size={19} />
                    )}
                  </div>

                  <div className="message-content">
                    <div className="message-name">
                      {message.role === "user" ? "You" : "Nova AI"}
                    </div>

                    <div className="message-text">
                      {message.content}
                    </div>

                    {message.role === "assistant" && (
                      <button
                        className="copy-button"
                        onClick={() =>
                          copyMessage(message.content, index)
                        }
                        title="Copy response"
                      >
                        {copiedIndex === index ? (
                          <Check size={15} />
                        ) : (
                          <Copy size={15} />
                        )}

                        {copiedIndex === index ? "Copied" : "Copy"}
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant">
                  <div className="message-avatar">
                    <Bot size={19} />
                  </div>

                  <div className="message-content">
                    <div className="message-name">Nova AI</div>
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

        </section>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError("")}>
              Dismiss
            </button>
          </div>
        )}

        {/* Input Area */}
        <footer className="input-section">

          <form className="input-box" onSubmit={sendMessage}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(e);
                }
              }}
              placeholder="Message Nova AI..."
              rows={1}
              disabled={loading}
            />

            <button
              type="submit"
              className="send-button"
              disabled={!input.trim() || loading}
              aria-label="Send message"
            >
              <Send size={19} />
            </button>
          </form>

          <p className="input-disclaimer">
            Nova AI can make mistakes. Verify important information.
          </p>

        </footer>

      </main>
    </div>
  );
}

export default App;
