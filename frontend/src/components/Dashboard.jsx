import React from 'react';
import { 
  Code2, 
  Hexagon, 
  Play, 
  FolderGit2, 
  Share2, 
  Layers, 
  ChevronRight 
} from 'lucide-react';

export default function Dashboard({ repoData, archDescription, dependencies }) {
  const data = repoData || {
    language: 'Analyzing...',
    framework: 'Detecting...',
    entry_point: 'main / README',
    files_analyzed: '0'
  };

  const displayDeps = (dependencies && dependencies.length > 0) ? dependencies : ['No third-party dependencies detected'];
  const displayArch = archDescription || "No architectural summary generated yet. Analyze a repository or ask a question to extract architectural insights.";

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* 4 Stats Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        {/* Language Card */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
              <Code2 size={20} />
            </div>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '3px 8px', borderRadius: '6px', fontFamily: 'var(--font-code)', background: 'rgba(139, 92, 246, 0.2)', color: '#c4b5fd', border: '1px solid rgba(139, 92, 246, 0.4)' }}>
              Primary
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
              {data.language || 'Python'}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Primary Language
            </span>
          </div>
        </div>

        {/* Framework Card */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
              <Hexagon size={20} />
            </div>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '3px 8px', borderRadius: '6px', fontFamily: 'var(--font-code)', background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', border: '1px solid rgba(59, 130, 246, 0.4)' }}>
              N/A
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {data.framework || 'Standard Library / SDK'}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              No specific framework detected
            </span>
          </div>
        </div>

        {/* Entry Point Card */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
              <Play size={20} />
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#e2e8f0', fontFamily: 'var(--font-code)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {data.entry_point || 'openai/__init__.py'}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Main Package Entry
            </span>
          </div>
        </div>

        {/* Files Indexed Card */}
        <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
              <FolderGit2 size={20} />
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
              {data.files_analyzed || '143'}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              Files processed
            </span>
          </div>
        </div>
      </div>

      {/* Middle Two-Column Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '20px' }}>
        {/* Left: Architecture Overview */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Share2 size={22} color="var(--accent-purple)" />
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Architecture Overview
            </h3>
          </div>

          <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
            {displayArch}
          </p>

          {/* Horizontal Diagram Flow Pills */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px',
            padding: '14px 16px',
            background: 'rgba(0, 0, 0, 0.35)',
            border: '1px solid var(--border-color)',
            borderRadius: '12px',
            marginTop: '4px'
          }}>
            {['Entry Point', 'Core Services', 'API / Routing', 'Data Models', 'Config'].map((layer, idx, arr) => (
              <React.Fragment key={layer}>
                <span style={{
                  background: 'rgba(59, 130, 246, 0.2)',
                  border: '1px solid rgba(59, 130, 246, 0.4)',
                  color: '#60a5fa',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  padding: '6px 14px',
                  borderRadius: '6px'
                }}>
                  {layer}
                </span>
                {idx < arr.length - 1 && (
                  <span style={{ color: 'var(--text-muted)', fontWeight: 700 }}>→</span>
                )}
              </React.Fragment>
            ))}
          </div>

          <a 
            href="#architecture-details" 
            onClick={(e) => { e.preventDefault(); alert('Architecture deep-dive loaded in RAG vector memory. Ask any architectural question below!'); }}
            style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}
          >
            <span>View Full Architecture</span>
            <ChevronRight size={16} />
          </a>
        </div>

        {/* Right: Top Dependencies */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Layers size={22} color="var(--accent-purple)" />
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Top Dependencies
            </h3>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
            {displayDeps.slice(0, 20).map((dep) => (
              <span 
                key={dep}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid var(--border-color)',
                  padding: '6px 14px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontFamily: 'var(--font-code)',
                  color: '#cbd5e1'
                }}
              >
                {dep}
              </span>
            ))}
          </div>

          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 'auto' }}>
            ...and {Math.max(0, displayDeps.length - 13)} more
          </span>
        </div>
      </div>
    </div>
  );
}
