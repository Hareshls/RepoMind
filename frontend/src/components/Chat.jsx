import React, { useState, useRef, useEffect } from 'react';
import { Brain, Send, Trash2, FileCode, User as UserIcon, Loader2 } from 'lucide-react';

const QUICK_PROMPTS = [
  "Explain the architecture",
  "How does authentication work?",
  "What are the main modules?",
  "How to make an API request?",
  "Show error handling approach"
];

export default function Chat({ messages, onSendMessage, onClearChat, isWaiting }) {
  const [input, setInput] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isWaiting]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || isWaiting) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handlePromptClick = (prompt) => {
    if (isWaiting) return;
    onSendMessage(prompt);
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Ask RepoMind
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Ask questions about this repository
          </p>
        </div>
      </div>

      {/* Two Column Interior */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '20px',
        minHeight: '440px'
      }}>
        {/* Left Column: Quick Prompts */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          paddingRight: '12px',
          borderRight: '1px solid var(--border-color)'
        }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
            Quick Prompts
          </span>
          
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handlePromptClick(prompt)}
              disabled={isWaiting}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '12px 14px',
                color: 'var(--text-secondary)',
                fontSize: '0.85rem',
                fontWeight: 500,
                textAlign: 'left',
                cursor: isWaiting ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                lineHeight: 1.4,
                opacity: isWaiting ? 0.6 : 1
              }}
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Right Column: Main Chat Feed */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(0, 0, 0, 0.3)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '12px 20px',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            background: 'rgba(255, 255, 255, 0.02)'
          }}>
            <button 
              onClick={onClearChat}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.82rem', fontWeight: 500, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Trash2 size={15} /> Clear Chat
            </button>
          </div>

          <div 
            ref={scrollRef}
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '18px',
              minHeight: '300px',
              maxHeight: '480px'
            }}
          >
            {messages.map((msg, index) => {
              const isUser = msg.sender === 'user';
              return (
                <div 
                  key={index}
                  style={{
                    display: 'flex',
                    gap: '12px',
                    maxWidth: '95%',
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    flexDirection: isUser ? 'row-reverse' : 'row',
                    animation: 'fadeIn 0.3s ease'
                  }}
                >
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: isUser ? '#334155' : 'var(--success-green)',
                    boxShadow: isUser ? 'none' : '0 0 12px rgba(16, 185, 129, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    flexShrink: 0
                  }}>
                    {isUser ? <UserIcon size={16} /> : <Brain size={18} />}
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
                      {isUser ? 'You' : 'RepoMind'}
                    </div>

                    <div style={{
                      background: isUser ? 'rgba(139, 92, 246, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                      border: `1px solid ${isUser ? 'rgba(139, 92, 246, 0.35)' : 'var(--border-color)'}`,
                      padding: '14px 18px',
                      borderRadius: '12px',
                      fontSize: '0.9rem',
                      lineHeight: 1.6,
                      color: 'var(--text-primary)',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {msg.text}
                    </div>

                    {/* Citations Row Below AI Response */}
                    {!isUser && msg.citations && msg.citations.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '2px' }}>
                        {msg.citations.map((c, idx) => (
                          <span 
                            key={idx}
                            style={{
                              background: 'rgba(255, 255, 255, 0.05)',
                              border: '1px solid var(--border-color)',
                              padding: '4px 10px',
                              borderRadius: '6px',
                              fontSize: '0.75rem',
                              fontFamily: 'var(--font-code)',
                              color: '#94a3b8',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <FileCode size={12} color="#38bdf8" /> {c.file} ({c.range})
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {isWaiting && (
              <div style={{ display: 'flex', gap: '12px', maxWidth: '95%', animation: 'fadeIn 0.3s ease' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--success-green)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                  <Brain size={18} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>RepoMind</div>
                  <div style={{ background: 'rgba(255, 255, 255, 0.04)', border: '1px solid var(--border-color)', padding: '14px 18px', borderRadius: '12px', fontSize: '0.9rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Loader2 size={16} className="animate-spin" color="var(--accent-cyan)" />
                    <span>Analyzing repository context in hybrid vector memory...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Bottom Input Form */}
          <form 
            onSubmit={handleSend}
            style={{
              padding: '16px 20px',
              borderTop: '1px solid var(--border-color)',
              background: 'rgba(0, 0, 0, 0.25)',
              display: 'flex',
              gap: '12px',
              alignItems: 'center'
            }}
          >
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about this repository..."
              disabled={isWaiting}
              style={{
                flex: 1,
                background: 'rgba(0, 0, 0, 0.4)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '12px 16px',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-main)',
                fontSize: '0.9rem'
              }}
            />
            <button 
              type="submit"
              disabled={!input.trim() || isWaiting}
              style={{
                padding: '0 24px',
                height: '44px',
                borderRadius: '12px',
                background: 'var(--accent-gradient)',
                border: 'none',
                color: 'white',
                fontWeight: 600,
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: (!input.trim() || isWaiting) ? 'not-allowed' : 'pointer',
                opacity: (!input.trim() || isWaiting) ? 0.5 : 1,
                flexShrink: 0
              }}
            >
              <span>Send</span>
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
