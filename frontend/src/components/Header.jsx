import React from 'react';
import { Menu, Sun, Moon, HelpCircle, User } from 'lucide-react';

export default function Header({ isDarkTheme, onToggleTheme, onToggleSidebar }) {
  return (
    <header style={{
      height: '64px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(10, 13, 29, 0.6)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      zIndex: 4,
      flexShrink: 0
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button 
          onClick={onToggleSidebar}
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '6px' }}
        >
          <Menu size={20} />
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.82rem',
          fontWeight: 600,
          color: 'var(--text-primary)',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          padding: '4px 12px',
          borderRadius: '20px'
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: 'var(--success-green)',
            boxShadow: '0 0 10px var(--success-green)',
            animation: 'pulse 2s infinite'
          }} />
          System Online
        </div>

        <span style={{
          background: 'rgba(139, 92, 246, 0.2)',
          border: '1px solid rgba(139, 92, 246, 0.4)',
          color: '#c4b5fd',
          fontSize: '0.78rem',
          fontWeight: 700,
          padding: '4px 10px',
          borderRadius: '6px',
          fontFamily: 'var(--font-code)'
        }}>
          v1.0.0
        </span>

        <button 
          onClick={onToggleTheme}
          title="Toggle theme"
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '6px' }}
        >
          {isDarkTheme ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <button 
          onClick={() => alert('Welcome to RepoMind AI!\n\n1. Paste any GitHub repository URL in the top Analyzer card.\n2. Watch the 7-step timeline analyze and index the code.\n3. Ask questions in the interactive chat console below!')}
          title="Help & Info"
          style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: '6px' }}
        >
          <HelpCircle size={18} />
        </button>

        <div 
          onClick={() => alert('User Profile:\n\nActive Engine: Hybrid AI (Ollama / OpenAI / Local)\nWorkspace: c:\\Users\\hares\\repomind')}
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'var(--accent-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 700,
            fontSize: '0.85rem',
            cursor: 'pointer',
            boxShadow: '0 2px 10px rgba(139, 92, 246, 0.3)'
          }}
        >
          <User size={16} />
        </div>
      </div>
    </header>
  );
}
