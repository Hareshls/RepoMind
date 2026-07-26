import React, { useState } from 'react';
import { 
  GitBranch as Github, 
  Rocket, 
  Download, 
  Folder, 
  ListTodo, 
  FileText, 
  Brain, 
  Database, 
  CheckCircle, 
  Loader2 
} from 'lucide-react';

const STEPS = [
  { id: 0, label: 'Cloning', sub: 'Repository cloned', icon: Download },
  { id: 1, label: 'Exploring', sub: 'Files discovered', icon: Folder },
  { id: 2, label: 'Planning', sub: 'Important files selected', icon: ListTodo },
  { id: 3, label: 'Reading', sub: 'Source code read', icon: FileText },
  { id: 4, label: 'Building Knowledge', sub: 'Extracting information', icon: Brain },
  { id: 5, label: 'Indexing Memory', sub: 'Vector memory created', icon: Database },
  { id: 6, label: 'Completed', sub: 'Ready to chat', icon: CheckCircle }
];

export default function Analyzer({ onAnalyze, isAnalyzing, currentStep }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim() || isAnalyzing) return;
    onAnalyze(url.trim());
    setUrl('');
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
          Analyze New Repository
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Enter a GitHub repository URL to begin analysis
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
        <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
          <div style={{ position: 'absolute', left: '16px', color: 'var(--text-secondary)', display: 'flex' }}>
            <Github size={20} />
          </div>
          <input 
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/openai/openai-python"
            disabled={isAnalyzing}
            style={{
              width: '100%',
              padding: '14px 16px 14px 48px',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              color: 'var(--text-primary)',
              fontFamily: 'var(--font-main)',
              fontSize: '0.95rem'
            }}
          />
        </div>

        <button 
          type="submit"
          disabled={!url.trim() || isAnalyzing}
          style={{
            padding: '0 24px',
            background: 'var(--accent-gradient)',
            border: 'none',
            borderRadius: '12px',
            color: 'white',
            fontWeight: 600,
            fontSize: '0.95rem',
            cursor: (!url.trim() || isAnalyzing) ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 4px 15px rgba(139, 92, 246, 0.35)',
            opacity: (!url.trim() || isAnalyzing) ? 0.6 : 1,
            whiteSpace: 'nowrap'
          }}
        >
          {isAnalyzing ? <Loader2 size={18} className="animate-spin" /> : <Rocket size={18} />}
          <span>Analyze Repository</span>
        </button>
      </form>

      {/* 7-Step Horizontal Stepper Timeline */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        marginTop: '10px',
        padding: '10px 0',
        position: 'relative',
        overflowX: 'auto'
      }}>
        {STEPS.map((step, idx) => {
          const IconComp = step.icon;
          const isDone = currentStep > idx || currentStep === 6;
          const isActive = currentStep === idx && currentStep !== 6;

          return (
            <div 
              key={step.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                position: 'relative',
                zIndex: 2,
                flex: 1,
                minWidth: '90px',
                textAlign: 'center'
              }}
            >
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: isDone ? 'var(--success-green)' : (isActive ? 'var(--accent-purple)' : 'rgba(255, 255, 255, 0.05)'),
                border: `2px solid ${isDone ? '#6ee7b7' : (isActive ? '#c4b5fd' : 'rgba(255, 255, 255, 0.1)')}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: (isDone || isActive) ? 'white' : 'var(--text-muted)',
                transition: 'all 0.4s ease',
                marginBottom: '10px',
                boxShadow: isDone ? '0 0 15px rgba(16, 185, 129, 0.5)' : (isActive ? '0 0 20px rgba(139, 92, 246, 0.6)' : 'none'),
                transform: isActive ? 'scale(1.08)' : 'scale(1)'
              }}>
                <IconComp size={20} />
              </div>

              <span style={{
                fontSize: '0.85rem',
                fontWeight: 600,
                color: (isDone || isActive) ? 'var(--text-primary)' : 'var(--text-secondary)',
                marginBottom: '2px'
              }}>
                {step.label}
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                {step.sub}
              </span>

              {/* Connecting Line */}
              {idx < STEPS.length - 1 && (
                <div style={{
                  position: 'absolute',
                  top: '22px',
                  left: 'calc(50% + 22px)',
                  width: 'calc(100% - 44px)',
                  height: '3px',
                  background: isDone ? 'var(--accent-gradient)' : 'rgba(255, 255, 255, 0.08)',
                  zIndex: -1,
                  boxShadow: isDone ? '0 0 10px rgba(139, 92, 246, 0.4)' : 'none',
                  transition: 'background 0.4s ease'
                }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
