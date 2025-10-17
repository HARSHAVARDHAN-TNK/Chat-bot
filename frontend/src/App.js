import React, { useState, useRef, useEffect } from "react";
import { askEduBot } from "./services/api";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages or typing change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  async function handleSend() {
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { sender: "user", text: input }]);
    setInput("");
    setTyping(true); // show typing indicator

    try {
      const data = await askEduBot(input);
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: data.reply, tag: data.intent }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        { sender: "bot", text: "⚠️ Backend error", tag: "error" }
      ]);
    } finally {
      setTyping(false); // hide typing indicator
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">EduBot</div>
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.sender} ${
              msg.tag === "fallback" ? "fallback" : ""
            }`}
          >
            <div className="message-bubble">{msg.text}</div>
          </div>
        ))}

        {/* Typing indicator */}
        {typing && (
          <div className="message bot">
            <div className="message-bubble typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSend()}
          placeholder="Type your question..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default App;