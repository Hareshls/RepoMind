import docx
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from pathlib import Path
from typing import Dict, Any

def sanitize_xml(text: Any) -> str:
    """Remove NULL bytes and XML-incompatible control characters."""
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

def infer_project_purpose(repo_name: str, knowledge: Dict[str, Any]) -> str:
    """Intelligently infer and explain what the project is about based on domain keywords and architecture."""
    name_lower = repo_name.lower()
    arch_str = str(knowledge.get("architecture", "")).lower()
    deps_str = " ".join([str(d).lower() for d in knowledge.get("dependencies", [])])
    mods_str = " ".join([str(m.get("path", "")).lower() for m in knowledge.get("key_modules", [])])
    combined = f"{name_lower} {arch_str} {deps_str} {mods_str}"

    if any(k in combined for k in ["resume", "cv", "job", "hiring", "recruitment", "applicant", "match", "career", "interview", "candidate"]):
        domain_desc = (
            f"The {repo_name} repository is an intelligent AI-powered HR and recruiting automation platform. "
            f"The project is specifically designed to analyze, parse, and evaluate applicant resumes against job descriptions and role requirements. "
            f"By leveraging automated data extraction and semantic matching algorithms, it streamlines candidate evaluation, highlights key qualifications, "
            f"and accelerates the hiring and recruitment workflow."
        )
    elif any(k in combined for k in ["rag", "retrieval", "document-ai", "embedding", "vector", "llm"]):
        domain_desc = (
            f"The {repo_name} repository is an advanced Retrieval-Augmented Generation (RAG) and Document Intelligence platform. "
            f"The project is engineered to ingest, parse, and analyze unstructured document data, compute semantic vector embeddings, and enable "
            f"natural-language question answering and automated knowledge retrieval using AI language models."
        )
    elif any(k in combined for k in ["fitness", "workout", "health", "monitor", "gym", "exercise"]):
        domain_desc = (
            f"The {repo_name} repository is a specialized health and fitness tracking platform. The project is designed to log daily workout routines, "
            f"monitor exercise metrics (sets, repetitions, and weights), handle user authentication securely via JWT, and generate personalized "
            f"fitness recommendations and training feedback using backend AI controllers."
        )
    elif any(k in combined for k in ["ecommerce", "shop", "store", "cart", "order", "product"]):
        domain_desc = (
            f"The {repo_name} repository is a full-stack e-commerce and digital storefront platform designed to manage product catalogs, "
            f"shopping carts, checkout workflows, and user orders with secure transactional guardrails."
        )
    elif any(k in combined for k in ["chat", "bot", "assistant", "message", "conversation"]):
        domain_desc = (
            f"The {repo_name} repository is an interactive conversational AI chatbot and virtual assistant platform built for real-time messaging, "
            f"intent recognition, and contextual dialogue management."
        )
    elif any(k in combined for k in ["sdk", "client", "library", "wrapper", "api-client", "openai"]):
        domain_desc = (
            f"The {repo_name} repository is a dedicated developer SDK and API Client Library. The project provides programmatic access to external services "
            f"and cloud APIs, handling request serialization, authentication headers, error handling, and response formatting."
        )
    elif any(k in combined for k in ["docker", "k8s", "kubernetes", "terraform", "deploy", "pipeline", "ci", "cd", "infra", "devops"]):
        domain_desc = (
            f"The {repo_name} repository is a DevOps automation and cloud infrastructure management project. It focuses on containerization, "
            f"continuous integration/continuous deployment (CI/CD) pipelines, and infrastructure-as-code orchestration for reliable software delivery."
        )
    elif any(k in combined for k in ["data", "analytics", "ml", "model", "train", "predict", "pytorch", "tensorflow", "pandas"]):
        domain_desc = (
            f"The {repo_name} repository is a data analytics and machine learning suite. The project is engineered to ingest dataset pipelines, "
            f"train predictive models, perform statistical evaluation, and generate actionable insights from complex data structures."
        )
    else:
        domain_desc = (
            f"The {repo_name} repository is a specialized software solution built to automate domain-specific tasks and data workflows. "
            f"The project focuses on organizing its feature capabilities into modular services, enabling users to reliably execute operations, "
            f"process structured inputs, and integrate with surrounding software ecosystems."
        )
    
    return domain_desc

def set_cell_background(cell, fill_color):
    """Set background color of a Word table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding margins for a cell in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def style_table(table, col_widths, header_bg="2C3E50", alt_bg="F8F9FA"):
    """Apply professional styling to a Word table."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        for j, cell in enumerate(row.cells):
            cell.width = Inches(col_widths[j])
            set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
            if i == 0:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.name = "Calibri"
                        run.font.size = Pt(10.5)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, alt_bg)
                else:
                    set_cell_background(cell, "FFFFFF")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(10)

def generate_docx(knowledge: Dict[str, Any]) -> Path:
    """Generate a dynamic Microsoft Word (.docx) documentation report for any repository."""
    repo_url = sanitize_xml(knowledge.get("repo_url", "Repository"))
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    language = sanitize_xml(knowledge.get("language", "Unknown Language"))
    framework = sanitize_xml(knowledge.get("framework", "General Purpose Architecture"))
    entry_point = sanitize_xml(knowledge.get("entry_point", "README.md"))
    architecture = sanitize_xml(knowledge.get("architecture", "Decoupled software architecture with modular separation."))
    dependencies = [sanitize_xml(d) for d in knowledge.get("dependencies", [])]
    key_modules = knowledge.get("key_modules", [])

    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run(f"{repo_name.upper()} REPOSITORY")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(44, 62, 80)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run(f"Technical Specification & Architecture Documentation ({framework})\n")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = RGBColor(127, 140, 141)
    
    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary", level=1)
    h1.style.font.name = "Calibri"
    h1.style.font.color.rgb = RGBColor(44, 62, 80)
    
    exec_text = infer_project_purpose(repo_name, knowledge)
    for para_str in exec_text.split("\n\n"):
        p_exec = doc.add_paragraph(sanitize_xml(para_str))
        p_exec.style.font.name = "Calibri"
        p_exec.style.font.size = Pt(11)

    # Section 2: Tech Stack & System Metrics (DataFrame Table)
    h2 = doc.add_heading("2. System Specifications & Tech Stack (Data Frame)", level=1)
    h2.style.font.name = "Calibri"
    h2.style.font.color.rgb = RGBColor(44, 62, 80)
    
    table_specs = doc.add_table(rows=1, cols=3)
    hdr_cells = table_specs.rows[0].cells
    hdr_cells[0].text = "Specification Parameter"
    hdr_cells[1].text = "Detected Value"
    hdr_cells[2].text = "Architectural Role & Significance"
    
    specs_data = [
        ("Repository Name", repo_name, "Target project workspace analyzed by RepoMind intelligence engine."),
        ("Primary Language", language, "Core runtime language used throughout source code implementations."),
        ("Detected Framework", framework, "Primary application framework governing system layout and lifecycle."),
        ("Primary Entry Point", entry_point, "Main execution bootstrapper or primary application initialization script."),
        ("Total Dependencies", f"{len(dependencies)} libraries detected", "External packages and third-party libraries imported by the project.")
    ]
    
    for cat, val, purp in specs_data:
        row_cells = table_specs.add_row().cells
        row_cells[0].text = sanitize_xml(cat)
        row_cells[1].text = sanitize_xml(val)
        row_cells[2].text = sanitize_xml(purp)
        
    style_table(table_specs, [1.8, 2.0, 2.7])
    doc.add_paragraph("\n")

    # Section 3: Architecture Overview
    h3 = doc.add_heading("3. Architecture Overview", level=1)
    h3.style.font.name = "Calibri"
    h3.style.font.color.rgb = RGBColor(44, 62, 80)
    
    p_arch = doc.add_paragraph(f"Architecture Summary: {architecture}\n\n"
                               "The codebase separates structural responsibilities across isolated modules and component directories, "
                               "ensuring maintainability, scalability, and clean data propagation across system boundaries.")
    p_arch.style.font.name = "Calibri"
    p_arch.style.font.size = Pt(11)

    # Section 4: Module Inventory DataFrame
    if key_modules:
        h4 = doc.add_heading("4. Repository Module Inventory (Data Frame)", level=1)
        h4.style.font.name = "Calibri"
        h4.style.font.color.rgb = RGBColor(44, 62, 80)
        
        table_mods = doc.add_table(rows=1, cols=3)
        hdr_mods = table_mods.rows[0].cells
        hdr_mods[0].text = "Module / File Path"
        hdr_mods[1].text = "Layer Classification"
        hdr_mods[2].text = "Functional Summary"
        
        for mod in key_modules[:15]:
            path_str = sanitize_xml(mod.get("path", "Unknown Module"))
            sum_str = sanitize_xml(mod.get("summary", "Primary codebase module."))
            
            # Simple heuristic classification
            if any(w in path_str.lower() for w in ["route", "controller", "api", "endpoint"]):
                layer = "API / Routing"
            elif any(w in path_str.lower() for w in ["model", "schema", "db", "sql", "mongo"]):
                layer = "Data Model"
            elif any(w in path_str.lower() for w in ["component", "view", "jsx", "tsx", "html", "css"]):
                layer = "Presentation UI"
            elif any(w in path_str.lower() for w in ["config", "json", "env", "lock", "vite", "package"]):
                layer = "Configuration"
            else:
                layer = "Core Service / Logic"

            row_cells = table_mods.add_row().cells
            row_cells[0].text = path_str
            row_cells[1].text = layer
            row_cells[2].text = sum_str
            
        style_table(table_mods, [2.2, 1.5, 2.8])
        doc.add_paragraph("\n")

    # Section 5: Dependencies
    if dependencies:
        h5 = doc.add_heading("5. Core Project Dependencies", level=1)
        h5.style.font.name = "Calibri"
        h5.style.font.color.rgb = RGBColor(44, 62, 80)
        
        dep_str = ", ".join(f"{d}" for d in dependencies[:30])
        p_dep = doc.add_paragraph(f"The repository relies on the following third-party dependencies and packages:\n\n{dep_str}")
        p_dep.style.font.name = "Calibri"
        p_dep.style.font.size = Pt(11)

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    out_path = export_dir / f"{repo_name}_Documentation.docx"
    doc.save(out_path)
    return out_path

def generate_html(knowledge: Dict[str, Any]) -> Path:
    """Generate a dynamic Word-styled HTML documentation report for any repository."""
    repo_url = sanitize_xml(knowledge.get("repo_url", "Repository"))
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    language = sanitize_xml(knowledge.get("language", "Unknown Language"))
    framework = sanitize_xml(knowledge.get("framework", "General Purpose Architecture"))
    entry_point = sanitize_xml(knowledge.get("entry_point", "README.md"))
    architecture = sanitize_xml(knowledge.get("architecture", "Decoupled software architecture with modular separation."))
    dependencies = [sanitize_xml(d) for d in knowledge.get("dependencies", [])]
    key_modules = knowledge.get("key_modules", [])

    exec_text = infer_project_purpose(repo_name, knowledge)
    exec_html = "".join(f"<p>{sanitize_xml(p)}</p>" for p in exec_text.split("\n\n"))

    rows_html = ""
    for mod in key_modules[:15]:
        path_str = sanitize_xml(mod.get("path", "Unknown Module"))
        sum_str = sanitize_xml(mod.get("summary", "Primary codebase module."))
        if any(w in path_str.lower() for w in ["route", "controller", "api", "endpoint"]):
            layer = "API / Routing"
        elif any(w in path_str.lower() for w in ["model", "schema", "db", "sql", "mongo"]):
            layer = "Data Model"
        elif any(w in path_str.lower() for w in ["component", "view", "jsx", "tsx", "html", "css"]):
            layer = "Presentation UI"
        elif any(w in path_str.lower() for w in ["config", "json", "env", "lock", "vite", "package"]):
            layer = "Configuration"
        else:
            layer = "Core Service / Logic"
        rows_html += f"<tr><td><span class=\"badge\">{path_str}</span></td><td>{layer}</td><td>{sum_str}</td></tr>\n"

    dep_badges = " ".join(f"<span class=\"badge\" style=\"background: #f1f5f9; color: #0f172a; margin: 3px; display: inline-block;\">{d}</span>" for d in dependencies[:30])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{repo_name} - Technical & Architecture Specification</title>
    <style>
        body {{
            background-color: #ffffff;
            color: #1a1a1a;
            font-family: 'Calibri', 'Arial', sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 50px 60px;
            box-shadow: 0 0 25px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
            line-height: 1.6;
        }}
        h1 {{
            color: #2c3e50;
            font-size: 24px;
            border-bottom: 2px solid #34495e;
            padding-bottom: 8px;
            margin-top: 35px;
        }}
        .doc-title {{
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .doc-sub {{
            text-align: center;
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 40px;
        }}
        p, li {{ font-size: 15px; color: #333333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 14px; }}
        th, td {{ border: 1px solid #dcdcdc; padding: 12px 15px; text-align: left; }}
        th {{ background-color: #2c3e50; color: #ffffff; font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #f1f3f5; }}
        .badge {{ background-color: #e8f4f8; color: #2980b9; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="doc-title">{repo_name} Repository</div>
    <div class="doc-sub">Technical Specification & Architecture Documentation ({framework})</div>

    <h1>1. Executive Summary</h1>
    {exec_html}

    <h1>2. System Specifications & Tech Stack (Data Frame)</h1>
    <table>
        <thead>
            <tr><th style="width: 28%;">Specification Parameter</th><th style="width: 32%;">Detected Value</th><th>Architectural Role & Significance</th></tr>
        </thead>
        <tbody>
            <tr><td><strong>Repository Name</strong></td><td>{repo_name}</td><td>Target project workspace analyzed by RepoMind intelligence engine.</td></tr>
            <tr><td><strong>Primary Language</strong></td><td>{language}</td><td>Core runtime language used throughout source code implementations.</td></tr>
            <tr><td><strong>Detected Framework</strong></td><td>{framework}</td><td>Primary application framework governing system layout and lifecycle.</td></tr>
            <tr><td><strong>Primary Entry Point</strong></td><td><span class="badge">{entry_point}</span></td><td>Main execution bootstrapper or primary application initialization script.</td></tr>
            <tr><td><strong>Total Dependencies</strong></td><td>{len(dependencies)} libraries detected</td><td>External packages and third-party libraries imported by the project.</td></tr>
        </tbody>
    </table>

    <h1>3. Architecture Overview</h1>
    <p><strong>Architecture Summary</strong>: {architecture}</p>
    <p>The codebase separates structural responsibilities across isolated modules and component directories, ensuring maintainability, scalability, and clean data propagation across system boundaries.</p>

    <h1>4. Repository Module Inventory (Data Frame)</h1>
    <table>
        <thead>
            <tr><th style="width: 38%;">Module / File Path</th><th style="width: 22%;">Layer Classification</th><th>Functional Summary</th></tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <h1>5. Core Project Dependencies</h1>
    <div style="margin-top: 15px;">{dep_badges}</div>
</body>
</html>"""
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    out_path = export_dir / f"{repo_name}_Documentation.html"
    out_path.write_text(html_content, encoding="utf-8")
    return out_path
