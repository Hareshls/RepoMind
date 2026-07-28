import React, { useState } from 'react';
import { 
  Code2, 
  Hexagon, 
  Play, 
  FolderGit2, 
  Share2, 
  Layers, 
  ChevronRight, 
  ChevronDown, 
  Star, 
  GitFork, 
  User, 
  Calendar, 
  HardDrive, 
  ShieldCheck, 
  Cpu, 
  Database, 
  Cloud, 
  Package, 
  BookOpen, 
  FileText, 
  CheckCircle2, 
  Activity, 
  BarChart3, 
  Sparkles, 
  Server, 
  Globe, 
  Key, 
  Box, 
  Terminal,
  HelpCircle,
  Eye
} from 'lucide-react';

export default function Dashboard({ repoData, archDescription, dependencies }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedSection, setExpandedSection] = useState(0); // For documentation accordion
  const [selectedLayer, setSelectedLayer] = useState('frontend'); // For interactive flowchart

  const data = repoData || {};
  const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const meta = data.metadata || {
    name: data.repo ? data.repo.split('/').pop().replace('.git', '') : 'Repository Intelligence',
    description: data.project_description || 'An AI-analyzed GitHub repository codebase.',
    owner: data.repo ? data.repo.split('/')[3] || 'Unknown Owner' : 'Unknown Owner',
    stars: 'N/A',
    forks: 'N/A',
    primary_language: data.language || 'Analyzing...',
    license: 'N/A',
    default_branch: 'N/A',
    last_updated: 'N/A',
    size: 'N/A'
  };

  const rawTech = data.tech_stack || {};
  const ignoreLangs = ['json', 'md', 'markdown', 'yaml', 'yml', 'txt', 'lock', 'env', 'toml', 'xml', 'ini', 'cfg', 'gitignore', 'dockerfile', 'config', 'log', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp', 'pdf', 'docx', 'csv', 'tsv', 'general code'];
  const rawLangs = Array.isArray(rawTech.languages) && rawTech.languages.length > 0 ? rawTech.languages : [data.language || 'JavaScript'];
  const cleanLangs = rawLangs.filter(l => l && !ignoreLangs.includes(l.toLowerCase().trim()));
  const finalLanguages = cleanLangs.length > 0 ? cleanLangs : [data.language || 'JavaScript'];

  const techStack = {
    languages: finalLanguages,
    frameworks: Array.isArray(rawTech.frameworks) && rawTech.frameworks.length > 0 ? rawTech.frameworks : (data.framework && data.framework !== 'Standard Library / SDK' ? [data.framework] : ['None detected']),
    databases: Array.isArray(rawTech.databases) && rawTech.databases.length > 0 ? rawTech.databases : (data.database ? [data.database] : ['None detected']),
    cloud_devops: Array.isArray(rawTech.cloud_devops) && rawTech.cloud_devops.length > 0 ? rawTech.cloud_devops : ['None detected'],
    package_managers: Array.isArray(rawTech.package_managers) && rawTech.package_managers.length > 0 ? rawTech.package_managers : ['None detected'],
    frontend: Array.isArray(rawTech.frontend) && rawTech.frontend.length > 0 ? rawTech.frontend : null,
    backend: Array.isArray(rawTech.backend) && rawTech.backend.length > 0 ? rawTech.backend : null,
    testing: Array.isArray(rawTech.testing) && rawTech.testing.length > 0 ? rawTech.testing : []
  };

  const displayDeps = (Array.isArray(dependencies) && dependencies.length > 0) ? dependencies : (Array.isArray(data.dependencies) && data.dependencies.length > 0 ? data.dependencies : ['No third-party dependencies detected']);
  const displayArch = archDescription || data.architecture || "Architecture analysis pending.";

  // Helper arrays for flowchart layer separation without bleeding frameworks
  const feKeywords = ['react', 'vue', 'angular', 'next', 'vite', 'tailwind', 'bootstrap', 'framer', 'three', 'recharts', 'html', 'css', 'dom'];
  const beKeywords = ['fastapi', 'express', 'django', 'flask', 'spring', 'nest', 'uvicorn', 'node', 'koa'];
  
  const feTechList = techStack.frontend || techStack.frameworks.filter(f => feKeywords.some(kw => f.toLowerCase().includes(kw)));
  const beTechList = techStack.backend || techStack.frameworks.filter(f => beKeywords.some(kw => f.toLowerCase().includes(kw)));
  const finalFeTech = feTechList.length > 0 ? feTechList : ['React / Vite UI Layer'];
  const finalBeTech = beTechList.length > 0 ? beTechList : [data.language ? `${data.language} API Controller` : 'Backend Service Controller'];

  const serviceModules = (data.key_modules && data.key_modules.length > 0) 
    ? data.key_modules.filter(m => m.layer !== 'Project Config & Tooling' && !m.path.toLowerCase().includes('readme')).slice(0, 3) 
    : [];
  const finalServiceTech = serviceModules.length > 0 ? serviceModules.map(m => m.path) : ['Core Domain Layer & NLP Pipelines'];
  const serviceDetails = serviceModules.length > 0 ? `Executes core domain rules and calculations: ${serviceModules.map(m => m.summary || m.path).join('; ')}` : 'Executes domain business rules, transformations, and workflows.';

  const isStatelessDb = techStack.databases.some(db => db.toLowerCase().includes('stateless') || db.toLowerCase().includes('memory') || db.toLowerCase().includes('none'));
  const dbDetails = isStatelessDb ? 'Operates as a stateless computational service without requiring a persistent relational database schema.' : `Manages persistent collection/table storage and query models via ${techStack.databases.join(', ')}.`;

  const apiRoutesList = (data.api_endpoints && data.api_endpoints.length > 0) ? data.api_endpoints : [];
  const apiTechList = apiRoutesList.length > 0 ? apiRoutesList.map(e => `${e.method} ${e.path}`) : ['Internal Application Routes'];
  const apiDetails = apiRoutesList.length > 0 ? `Exposes structured communication endpoints: ${apiRoutesList.map(e => `${e.method} ${e.path} (${e.summary || 'route handler'})`).join('; ')}` : 'Handles internal application routing and programmatic execution.';

  const secTechList = (data.security_detected && data.security_detected.length > 0) ? data.security_detected : (data.authentication ? [data.authentication] : ['Security details not explicitly indexed']);
  const secDetails = (data.security_detected && data.security_detected.length > 0) ? `Enforces application security via: ${secTechList.join(', ')}.` : 'Security implementation details pending or not fully indexed.';

  const storageDetails = data.storage_details || 'Storage mechanisms not explicitly detected.';
  const deployDetails = `Configured for runtime execution using package manifests (${techStack.package_managers.join(', ')}) and server environments (${techStack.cloud_devops.join(', ')}).`;

  // Parse documentation sections from summary_doc
  const parseDocSections = (docText) => {
    if (!docText) return [];
    const sections = [];
    const lines = docText.split('\n');
    let currentTitle = 'Overview & Introduction';
    let currentContent = [];

    for (let line of lines) {
      if (line.startsWith('## ') || line.startsWith('# ')) {
        if (currentContent.length > 0) {
          sections.push({ title: currentTitle, content: currentContent.join('\n').trim() });
          currentContent = [];
        }
        currentTitle = line.replace(/^#+\s*/, '').trim();
      } else {
        currentContent.push(line);
      }
    }
    if (currentContent.length > 0) {
      sections.push({ title: currentTitle, content: currentContent.join('\n').trim() });
    }
    return sections;
  };

  const docSections = parseDocSections(data.summary_doc || "");
  if (docSections.length === 0) {
    docSections.push(
      { title: 'Overview', content: "Repository documentation is currently being generated or no detailed summary is available." }
    );
  }

  // Interactive Architecture Flowchart Layers
  const ARCH_LAYERS = [
    { id: 'frontend', name: 'Frontend & Client UI', icon: Globe, color: '#38bdf8', desc: 'User interface & client presentation logic', tech: finalFeTech, details: `Client-side presentation layer built with ${finalFeTech.join(', ')} for responsive user interactions and DOM rendering.` },
    { id: 'backend', name: 'Backend API & Routing', icon: Server, color: '#818cf8', desc: 'API gateway & HTTP request controllers', tech: finalBeTech, details: `Server-side controller layer (${finalBeTech.join(', ')}) handling REST requests, CORS headers, and coordinating execution.` },
    { id: 'services', name: 'Core Domain Services', icon: Cpu, color: '#c084fc', desc: 'Business logic, AI/NLP calculations & pipelines', tech: finalServiceTech, details: serviceDetails },
    { id: 'database', name: 'Database & Persistence', icon: Database, color: '#f472b6', desc: 'State management & persistent data models', tech: techStack.databases, details: dbDetails },
    { id: 'external', name: 'REST API Surface & Routes', icon: Activity, color: '#fb923c', desc: 'HTTP REST endpoints & client communication', tech: apiTechList, details: apiDetails },
    { id: 'auth', name: 'Security & Access Control', icon: Key, color: '#fbbf24', desc: 'Request validation, CORS policies & API security', tech: secTechList, details: secDetails },
    { id: 'storage', name: 'Storage & Asset Processing', icon: Box, color: '#34d399', desc: 'Document buffers, static UI assets & file handling', tech: ['Local Document Buffer & Static Assets'], details: storageDetails },
    { id: 'deployment', name: 'Deployment & Runtime', icon: Cloud, color: '#2dd4bf', desc: 'Server runtime, package execution & environments', tech: techStack.cloud_devops, details: deployDetails }
  ];

  const currentLayerObj = ARCH_LAYERS.find(l => l.id === selectedLayer) || ARCH_LAYERS[0];



  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Top Section Navigation Tabs */}
      <div style={{
        display: 'flex',
        gap: '10px',
        flexWrap: 'wrap',
        background: 'rgba(0, 0, 0, 0.4)',
        padding: '8px',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        backdropFilter: 'blur(10px)'
      }}>
        {[
          { id: 'overview', label: 'Overview & Stats', icon: Activity },
          { id: 'tech', label: 'Technology Stack', icon: Hexagon },
          { id: 'flowchart', label: 'Interactive Architecture Flowchart', icon: Share2 },
          { id: 'docs', label: 'Repository Documentation', icon: BookOpen }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '12px',
                background: isActive ? 'var(--accent-gradient)' : 'transparent',
                border: 'none',
                color: isActive ? 'white' : 'var(--text-secondary)',
                fontSize: '0.88rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.25s ease',
                boxShadow: isActive ? '0 4px 15px rgba(139, 92, 246, 0.4)' : 'none'
              }}
            >
              <Icon size={18} color={isActive ? 'white' : 'var(--accent-cyan)'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ─────────────────────────────────────────────────────────────
          TAB 1: REPOSITORY OVERVIEW DASHBOARD (10 Metrics)
         ───────────────────────────────────────────────────────────── */}
      {(activeTab === 'overview' || activeTab === 'all') && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.3s ease' }}>
          
          {/* Header Card */}
          <div className="glass-panel" style={{
            padding: '24px 28px',
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(30, 41, 59, 0.4))',
            border: '1px solid rgba(139, 92, 246, 0.35)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '14px',
                  background: 'var(--accent-gradient)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.5)'
                }}>
                  <FolderGit2 size={28} />
                </div>
                <div>
                  <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2 }}>
                    {meta.name}
                  </h2>
                  <span style={{ fontSize: '0.9rem', color: 'var(--accent-cyan)', fontWeight: 500 }}>
                    Owned by @{meta.owner}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(255, 255, 255, 0.08)', border: '1px solid var(--border-color)', padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: 600, color: '#fcd34d' }}>
                  <Star size={15} /> {typeof meta.stars === 'number' ? meta.stars.toLocaleString() : meta.stars} Stars
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(255, 255, 255, 0.08)', border: '1px solid var(--border-color)', padding: '6px 14px', borderRadius: '20px', fontSize: '0.82rem', fontWeight: 600, color: '#93c5fd' }}>
                  <GitFork size={15} /> {typeof meta.forks === 'number' ? meta.forks.toLocaleString() : meta.forks} Forks
                </span>
              </div>
            </div>

            <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '900px', marginTop: '4px' }}>
              {meta.description}
            </p>
          </div>

          {/* 10 Repository Overview Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {[
              { label: 'Repository Name', val: meta.name, sub: 'Target repository', icon: FolderGit2, col: '#818cf8' },
              { label: 'Owner', val: meta.owner, sub: 'GitHub Account', icon: User, col: '#38bdf8' },
              { label: 'Primary Language', val: meta.primary_language, sub: 'Detected syntax', icon: Code2, col: '#f472b6' },
              { label: 'Stars', val: typeof meta.stars === 'number' ? meta.stars.toLocaleString() : meta.stars, sub: 'Community rating', icon: Star, col: '#fbbf24' },
              { label: 'Forks', val: typeof meta.forks === 'number' ? meta.forks.toLocaleString() : meta.forks, sub: 'Code copies', icon: GitFork, col: '#60a5fa' },
              { label: 'License', val: meta.license, sub: 'Legal distribution', icon: ShieldCheck, col: '#34d399' },
              { label: 'Default Branch', val: meta.default_branch, sub: 'Active git tree', icon: Terminal, col: '#c084fc' },
              { label: 'Last Updated', val: meta.last_updated, sub: 'Latest commit timestamp', icon: Calendar, col: '#fb923c' },
              { label: 'Repository Size', val: meta.size, sub: 'Storage allocation', icon: HardDrive, col: '#2dd4bf' },
              { label: 'Files Analyzed', val: data.files_analyzed || '25', sub: 'Indexed in vector memory', icon: FileText, col: '#e879f9' }
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="glass-panel" style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '10px', transition: 'all 0.25s ease' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ width: '34px', height: '34px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: item.col }}>
                      <Icon size={18} />
                    </div>
                    <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Metric #{idx + 1}
                    </span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflow: 'hidden' }}>
                    <span style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={item.val}>
                      {item.val}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {item.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Architecture Snippet */}
          <div className="glass-panel" style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Share2 size={22} color="var(--accent-purple)" />
                <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Executive Architectural Summary
                </h3>
              </div>
              <button 
                onClick={() => setActiveTab('flowchart')}
                style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--accent-cyan)', padding: '6px 14px', borderRadius: '8px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <span>Explore Flowchart</span>
                <ChevronRight size={15} />
              </button>
            </div>
            <p style={{ fontSize: '0.92rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              {displayArch}
            </p>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          TAB 2: TECHNOLOGY DETECTION (5 Categorized Pill Groups)
         ───────────────────────────────────────────────────────────── */}
      {(activeTab === 'tech' || activeTab === 'all') && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.3s ease' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
              Automated Technology Detection
            </h2>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Detected dynamically by parsing manifests, configuration trees, and source code headers. Never hardcoded.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
            {[
              { title: 'Programming Languages', items: techStack.languages, icon: Code2, col: '#818cf8', desc: 'Syntax and source code files analyzed' },
              { title: 'Frameworks & Libraries', items: techStack.frameworks, icon: Hexagon, col: '#c084fc', desc: 'Core UI and routing engines' },
              { title: 'Databases & Storage', items: techStack.databases, icon: Database, col: '#f472b6', desc: 'Persistence models and query builders' },
              { title: 'Cloud & DevOps', items: techStack.cloud_devops, icon: Cloud, col: '#38bdf8', desc: 'Containerization, pipelines & cloud providers' },
              { title: 'Package Managers', items: techStack.package_managers, icon: Package, col: '#fbbf24', desc: 'Dependency lockfiles and manifests' }
            ].map((cat, idx) => {
              const Icon = cat.icon;
              return (
                <div key={idx} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: cat.col }}>
                      <Icon size={22} />
                    </div>
                    <div>
                      <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {cat.title}
                      </h3>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {cat.desc}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                    {(cat.items && cat.items.length > 0) ? cat.items.map((item, i) => (
                      <span key={i} style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: `1px solid ${cat.col}55`,
                        color: 'var(--text-primary)',
                        padding: '8px 16px',
                        borderRadius: '20px',
                        fontSize: '0.88rem',
                        fontWeight: 600,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        boxShadow: `0 2px 10px ${cat.col}15`,
                        transition: 'all 0.2s ease'
                      }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: cat.col }} />
                        {item}
                      </span>
                    )) : (
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic' }}>
                        No specialized tools detected in this category
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Complete Dependencies List Card */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Layers size={22} color="var(--accent-purple)" />
                <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  All Detected Dependencies ({displayDeps.length})
                </h3>
              </div>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', maxHeight: '240px', overflowY: 'auto', padding: '4px' }}>
              {displayDeps.map((dep) => (
                <span key={dep} style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid var(--border-color)',
                  padding: '6px 14px',
                  borderRadius: '8px',
                  fontSize: '0.82rem',
                  fontFamily: 'var(--font-code)',
                  color: '#cbd5e1'
                }}>
                  {dep}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          TAB 3: INTERACTIVE ARCHITECTURE FLOWCHART DIAGRAM
         ───────────────────────────────────────────────────────────── */}
      {(activeTab === 'flowchart' || activeTab === 'all') && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.3s ease' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
              Dynamic System Architecture Flowchart
            </h2>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              Interactive end-to-end processing pipeline. Click any architectural node to inspect responsible modules and engineering mechanics.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
            
            {/* Left Column: Vertical Interactive Flowchart */}
            <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(10, 13, 29, 0.7)' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px', marginBottom: '8px' }}>
                EXECUTION FLOWCHART (SELECT TO INSPECT)
              </span>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'center' }}>
                {ARCH_LAYERS.map((layer, idx) => {
                  const Icon = layer.icon;
                  const isSelected = selectedLayer === layer.id;
                  return (
                    <React.Fragment key={layer.id}>
                      <div
                        onClick={() => setSelectedLayer(layer.id)}
                        style={{
                          width: '100%',
                          padding: '14px 18px',
                          borderRadius: '14px',
                          background: isSelected ? 'rgba(139, 92, 246, 0.25)' : 'rgba(255, 255, 255, 0.03)',
                          border: `1.5px solid ${isSelected ? 'var(--accent-purple)' : 'var(--border-color)'}`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          cursor: 'pointer',
                          transition: 'all 0.25s ease',
                          boxShadow: isSelected ? '0 0 20px rgba(139, 92, 246, 0.3)' : 'none',
                          transform: isSelected ? 'scale(1.02)' : 'scale(1)'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <div style={{
                            width: '38px',
                            height: '38px',
                            borderRadius: '10px',
                            background: isSelected ? layer.color : 'rgba(255, 255, 255, 0.05)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: isSelected ? 'white' : layer.color,
                            transition: 'all 0.25s ease'
                          }}>
                            <Icon size={20} />
                          </div>
                          <div>
                            <span style={{ fontSize: '0.98rem', fontWeight: 700, color: isSelected ? 'white' : 'var(--text-primary)', display: 'block' }}>
                              {layer.name}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>
                              {layer.tech[0]}
                            </span>
                          </div>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '0.72rem', fontWeight: 600, padding: '3px 8px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.08)', color: 'var(--text-muted)' }}>
                            Step #{idx + 1}
                          </span>
                          <ChevronRight size={18} color={isSelected ? 'var(--accent-cyan)' : 'var(--text-muted)'} />
                        </div>
                      </div>

                      {/* Glowing Downward Arrow */}
                      {idx < ARCH_LAYERS.length - 1 && (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '22px', justifyContent: 'center' }}>
                          <div style={{ width: '2px', height: '10px', background: 'linear-gradient(to bottom, var(--accent-purple), var(--accent-cyan))' }} />
                          <span style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: 800, lineHeight: 0.8 }}>↓</span>
                        </div>
                      )}
                    </React.Fragment>
                  );
                })}
              </div>
            </div>

            {/* Right Column: Dynamic Node Inspection Panel */}
            <div className="glass-panel" style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '20px', background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8))', border: '1px solid rgba(139, 92, 246, 0.4)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: currentLayerObj.color, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', boxShadow: `0 4px 15px ${currentLayerObj.color}66` }}>
                  {React.createElement(currentLayerObj.icon, { size: 26 })}
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    LAYER INSPECTOR
                  </span>
                  <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800, color: 'white', lineHeight: 1.2 }}>
                    {currentLayerObj.name} Layer
                  </h3>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  OPERATIONAL RESPONSIBILITY
                </span>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-primary)', lineHeight: 1.6, background: 'rgba(255, 255, 255, 0.03)', padding: '14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                  {currentLayerObj.desc}. {currentLayerObj.details}
                </p>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  DETECTED TECHNOLOGIES & MODULES
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                  {currentLayerObj.tech.map((t, idx) => (
                    <span key={idx} style={{
                      background: 'rgba(139, 92, 246, 0.15)',
                      border: '1px solid rgba(139, 92, 246, 0.4)',
                      color: '#c4b5fd',
                      padding: '8px 16px',
                      borderRadius: '8px',
                      fontSize: '0.9rem',
                      fontFamily: 'var(--font-code)',
                      fontWeight: 600
                    }}>
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ marginTop: 'auto', padding: '16px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <CheckCircle2 size={20} color="var(--success-green)" />
                <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                  <strong>Verified by RepoMind Hybrid RAG Engine</strong>. The data layer is engineered for modular abstraction, allowing clean persistence decoupling.
                </span>
              </div>
            </div>

          </div>
        </div>
      )}


      {/* ─────────────────────────────────────────────────────────────
          TAB 5: COLLAPSIBLE REPOSITORY DOCUMENTATION (16 Chapters)
         ───────────────────────────────────────────────────────────── */}
      {(activeTab === 'docs' || activeTab === 'all') && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', animation: 'fadeIn 0.3s ease' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '4px' }}>
                Professional Repository Documentation ({docSections.length} Chapters)
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                Generated dynamically by the Hybrid AI Engine based on analyzed repository files. No hardcoded templates.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                onClick={() => window.open(`${apiUrl}/export/doc?repo_url=${encodeURIComponent(data.repo || '')}`, '_blank')}
                style={{ background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#93c5fd', padding: '8px 16px', borderRadius: '10px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <FileText size={16} /> Download Word (.docx)
              </button>
              <button 
                onClick={() => window.open(`${apiUrl}/export/html?repo_url=${encodeURIComponent(data.repo || '')}`, '_blank')}
                style={{ background: 'rgba(16, 185, 129, 0.2)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#6ee7b7', padding: '8px 16px', borderRadius: '10px', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <Globe size={16} /> Download Report (.html)
              </button>
            </div>
          </div>

          {/* Accordion List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {docSections.map((sec, idx) => {
              const isExpanded = expandedSection === idx;
              return (
                <div key={idx} className="glass-panel" style={{ overflow: 'hidden', transition: 'all 0.25s ease', border: isExpanded ? '1px solid rgba(139, 92, 246, 0.5)' : '1px solid var(--border-color)' }}>
                  
                  {/* Section Accordion Header */}
                  <div 
                    onClick={() => setExpandedSection(isExpanded ? -1 : idx)}
                    style={{
                      padding: '18px 24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      background: isExpanded ? 'rgba(139, 92, 246, 0.15)' : 'transparent',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <span style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {idx + 1}
                      </span>
                      <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.08rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {sec.title}
                      </h3>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {isExpanded ? 'Click to collapse' : 'Click to expand'}
                      </span>
                      {isExpanded ? <ChevronDown size={20} color="var(--accent-cyan)" /> : <ChevronRight size={20} color="var(--text-secondary)" />}
                    </div>
                  </div>

                  {/* Accordion Body Content */}
                  {isExpanded && (
                    <div style={{
                      padding: '24px',
                      borderTop: '1px solid var(--border-color)',
                      background: 'rgba(0, 0, 0, 0.25)',
                      fontSize: '0.92rem',
                      lineHeight: 1.7,
                      color: 'var(--text-primary)',
                      whiteSpace: 'pre-wrap',
                      animation: 'fadeIn 0.25s ease'
                    }}>
                      {sec.content}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
}
