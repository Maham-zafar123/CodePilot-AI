import streamlit as st
from pathlib import Path
from datetime import datetime

from backend.github_loader import clone_repo
from backend.zip_loader import save_and_extract_zip
from backend.parser import collect_code_files, project_stats, folder_tree
from backend.vector_db import index_project
from backend.rag import ask_codebase
from backend.analyzer import summarize_project
from backend.security_scan import scan_security, security_score
from backend.bug_detector import scan_bugs, bug_score
from backend.docs_generator import generate_readme, generate_developer_guide
from backend.test_generator import generate_tests, generate_test_plan
from backend.diagram_generator import generate_mermaid_diagram, generate_static_mermaid
from backend.refactor import suggest_refactoring
from backend.langgraph_agent import run_engineer_review
from backend.report_generator import save_markdown_report, build_full_report


st.set_page_config(
    page_title="CodePilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------- Styling -----------------------------
st.markdown(
    """
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background: transparent !important;}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(124, 58, 237, 0.24), transparent 28%),
        radial-gradient(circle at 86% 6%, rgba(14, 165, 233, 0.18), transparent 26%),
        linear-gradient(135deg, #020617 0%, #07111f 50%, #050816 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 1480px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 22px;
    margin-bottom: 18px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 13px;
}

.logo {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    box-shadow: 0 0 35px rgba(124, 58, 237, 0.52);
    font-size: 32px;
}

.brand-title {
    font-size: 31px;
    font-weight: 950;
    letter-spacing: -1px;
    line-height: 1;
}

.brand-title span {
    background: linear-gradient(90deg, #a855f7, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-subtitle {
    color: #94a3b8;
    margin-top: 7px;
    font-size: 14px;
}

.nav-pills {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.nav-pill {
    padding: 11px 16px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    background: rgba(15, 23, 42, 0.68);
    color: #dbeafe;
    font-weight: 800;
    font-size: 14px;
}

.nav-pill.active {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    box-shadow: 0 0 28px rgba(124, 58, 237, 0.35);
}

.hero-shell {
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 26px;
    padding: 34px;
    background:
        radial-gradient(circle at 82% 18%, rgba(37, 99, 235, 0.30), transparent 30%),
        radial-gradient(circle at 30% 90%, rgba(168, 85, 247, 0.22), transparent 26%),
        rgba(15, 23, 42, 0.72);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.36);
    margin: 10px 0 18px 0;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(124, 58, 237, 0.14);
    color: #e9d5ff;
    border: 1px solid rgba(168, 85, 247, 0.58);
    font-weight: 900;
    font-size: 13px;
    margin-bottom: 16px;
}

.hero-title {
    font-size: 52px;
    line-height: 1.03;
    letter-spacing: -1.7px;
    font-weight: 950;
    margin-bottom: 18px;
}

.hero-title span {
    background: linear-gradient(90deg, #a855f7, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-text {
    color: #cbd5e1;
    font-size: 17px;
    line-height: 1.75;
    max-width: 680px;
}

.upload-card {
    border: 1px solid rgba(148, 163, 184, 0.20);
    border-radius: 22px;
    padding: 24px 24px 20px 24px;
    background: rgba(2, 6, 23, 0.44);
    min-height: 260px;
}

.upload-card.dashed {
    border: 1px dashed rgba(168, 85, 247, 0.72);
    background: rgba(88, 28, 135, 0.12);
}

.card-title {
    font-size: 25px;
    font-weight: 950;
    margin-bottom: 6px;
}

.card-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 16px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 14px;
    margin: 18px 0;
}

.stat-card {
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 20px;
    padding: 20px;
    background: rgba(15, 23, 42, 0.64);
    min-height: 150px;
}

.stat-icon {
    width: 54px;
    height: 54px;
    display: grid;
    place-items: center;
    border-radius: 16px;
    font-size: 27px;
    background: linear-gradient(135deg, rgba(124, 58, 237, .78), rgba(37, 99, 235, .56));
    margin-bottom: 14px;
}

.stat-label {color: #cbd5e1; font-size: 14px; font-weight: 700;}
.stat-value {font-size: 32px; font-weight: 950; margin: 3px 0;}
.stat-sub {color: #64748b; font-size: 13px;}

.section-card {
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 24px;
    padding: 24px;
    background: rgba(15, 23, 42, 0.58);
    margin-top: 18px;
}

.section-title {
    font-size: 28px;
    font-weight: 950;
    margin-bottom: 18px;
}

.section-title span {color: #a855f7;}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 14px;
}

.feature-card {
    min-height: 152px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 19px;
    padding: 18px;
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.64), rgba(15, 23, 42, 0.78));
    transition: 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-3px);
    border-color: rgba(168, 85, 247, 0.58);
    box-shadow: 0 14px 35px rgba(124, 58, 237, 0.18);
}

.feature-icon {
    width: 50px;
    height: 50px;
    display: grid;
    place-items: center;
    border-radius: 15px;
    font-size: 24px;
    background: linear-gradient(135deg, rgba(168, 85, 247, .75), rgba(14, 165, 233, .45));
    margin-bottom: 12px;
}

.feature-title {font-weight: 950; font-size: 16px; margin-bottom: 7px;}
.feature-desc {color: #aebed2; font-size: 13px; line-height: 1.55;}

.ready-banner {
    border: 1px solid rgba(168, 85, 247, 0.35);
    border-radius: 22px;
    padding: 20px 24px;
    background: linear-gradient(90deg, rgba(88, 28, 135, 0.22), rgba(14, 165, 233, 0.10));
    margin: 18px 0;
}

.ready-title {
    font-size: 22px;
    font-weight: 950;
    margin-bottom: 4px;
}

.ready-sub {
    color: #aebed2;
}

/* Streamlit widgets */
div.stButton > button {
    border-radius: 14px !important;
    border: 1px solid rgba(168, 85, 247, 0.55) !important;
    background: linear-gradient(135deg, #8b5cf6, #2563eb) !important;
    color: white !important;
    font-weight: 850 !important;
    min-height: 46px;
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.22);
}

div.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(255,255,255,0.45) !important;
}

[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.28);
    padding: 4px;
    border-radius: 18px;
}

[data-testid="stFileUploader"] section {
    border-radius: 18px !important;
    background: rgba(15, 23, 42, 0.62) !important;
    border: 1px dashed rgba(168, 85, 247, 0.70) !important;
    min-height: 92px;
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(2, 6, 23, 0.66) !important;
    color: white !important;
    border-radius: 14px !important;
    border: 1px solid rgba(148, 163, 184, 0.24) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(2, 6, 23, 0.35);
    padding: 8px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.16);
}

.stTabs [data-baseweb="tab"] {
    height: 46px;
    border-radius: 14px;
    color: #cbd5e1;
    font-weight: 850;
    padding: 0 16px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(124, 58, 237, .95), rgba(37, 99, 235, .75));
    color: white !important;
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.50);
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

@media (max-width: 1100px) {
    .feature-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
    .stats-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
    .hero-title {font-size: 38px;}
    .topbar {display: block;}
    .nav-pills {justify-content: flex-start; margin-top: 16px;}
}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------- State -----------------------------
DEFAULT_STATE = {
    "project_path": None,
    "files": [],
    "project_name": "project",
    "loaded": False,
    "last_analysis": "--",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ----------------------------- Helpers -----------------------------
def load_codebase(uploaded_zip, repo_url):
    if uploaded_zip:
        path = save_and_extract_zip(uploaded_zip)
    elif repo_url.strip():
        path = clone_repo(repo_url.strip())
    else:
        st.warning("Upload a ZIP project or enter a GitHub repository URL.")
        return

    files = collect_code_files(path)

    st.session_state.project_path = path
    st.session_state.files = files
    st.session_state.project_name = Path(path).name.replace("-", "_").replace(" ", "_")
    st.session_state.loaded = True
    st.session_state.last_analysis = datetime.now().strftime("%I:%M %p")

    with st.spinner("Indexing code with embeddings..."):
        chunks = index_project(st.session_state.project_name, files)

    st.success(f"Loaded {len(files)} files and indexed {chunks} chunks.")


def topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="logo">🚀</div>
                <div>
                    <div class="brand-title">CodePilot <span>AI</span></div>
                    <div class="brand-subtitle">AI Codebase Engineer</div>
                </div>
            </div>
            <div class="nav-pills">
                <div class="nav-pill active">⌂ Home</div>
                <div class="nav-pill">💬 Chat</div>
                <div class="nav-pill">🐞 Bugs</div>
                <div class="nav-pill">🔒 Security</div>
                <div class="nav-pill">📝 Docs</div>
                <div class="nav-pill">🧪 Tests</div>
                <div class="nav-pill">📊 Diagram</div>
                <div class="nav-pill">🔄 Refactor</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_cards():
    """Render feature cards using native Streamlit columns.
    This avoids the raw HTML showing as text issue."""
    features = [
        ("💬", "Chat with Codebase", "Ask questions about your codebase and get context-aware answers."),
        ("🔒", "Security Scanner", "Detect hardcoded secrets, API keys, vulnerabilities and risky patterns."),
        ("🐞", "Bug & Quality Detector", "Find bugs, code smells, anti-patterns and quality issues."),
        ("🧪", "Unit Test Generator", "Generate unit tests with edge cases, mocks and framework support."),
        ("📋", "Test Plan Generator", "Create complete test scenarios and a testing strategy."),
        ("📝", "Documentation Generator", "Generate README, API docs, installation guide and developer docs."),
        ("📊", "Architecture Diagram", "Generate static and AI-powered Mermaid architecture diagrams."),
        ("🔄", "Refactoring Assistant", "Improve structure, readability and maintainability."),
        ("📘", "Developer Guide", "Create onboarding notes and a technical guide for developers."),
        ("🤖", "Full Engineer Review", "Run a complete engineering review with actionable insights."),
    ]

    st.markdown(
        '<div class="section-card"><div class="section-title">Powerful <span>AI Engineering</span> Features</div>',
        unsafe_allow_html=True,
    )

    for i in range(0, len(features), 5):
        cols = st.columns(5)
        for col, (icon, title, desc) in zip(cols, features[i:i + 5]):
            with col:
                st.markdown(
                    f"""
                    <div class="feature-card">
                        <div class="feature-icon">{icon}</div>
                        <div class="feature-title">{title}</div>
                        <div class="feature-desc">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown('</div>', unsafe_allow_html=True)


def stats_cards(stats=None, security=0, quality=0):
    if stats is None:
        total_files = 0
        total_lines = 0
        languages = 0
    else:
        total_files = stats["total_files"]
        total_lines = stats["total_lines"]
        languages = len(stats["languages"])

    html = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">📁</div>
            <div class="stat-label">Files</div>
            <div class="stat-value">{total_files}</div>
            <div class="stat-sub">Total files</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">&lt;/&gt;</div>
            <div class="stat-label">Lines of Code</div>
            <div class="stat-value">{total_lines}</div>
            <div class="stat-sub">Total lines</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-label">Languages</div>
            <div class="stat-value">{languages}</div>
            <div class="stat-sub">Detected</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🛡️</div>
            <div class="stat-label">Security Score</div>
            <div class="stat-value">{security}<span style="font-size:16px;color:#94a3b8;"> / 100</span></div>
            <div class="stat-sub">Overall score</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⚙️</div>
            <div class="stat-label">Quality Score</div>
            <div class="stat-value">{quality}<span style="font-size:16px;color:#94a3b8;"> / 100</span></div>
            <div class="stat-sub">Overall score</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def mini_features_row():
    st.markdown(
        """
        <div class="ready-banner">
            <div class="ready-title">One Platform. Complete Codebase Intelligence.</div>
            <div class="ready-sub">Upload your project once, then use AI to understand, review, document, test and improve it.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------- Header + Hero -----------------------------
topbar()

files = st.session_state.files
project_path = st.session_state.project_path
project_name = st.session_state.project_name

# Use one clean shell for the hero. Widgets are placed in normal Streamlit columns
# so no empty HTML containers appear.
st.markdown('<div class="hero-shell">', unsafe_allow_html=True)
hero_left, hero_upload, hero_repo = st.columns([1.25, 1.0, 1.0], gap="large")

with hero_left:
    st.markdown(
        """
        <div class="badge">AI-POWERED CODE ENGINEERING</div>
        <div class="hero-title">Understand. Improve. Ship.<br><span>With AI.</span></div>
        <div class="hero-text">
            Upload your codebase and let CodePilot AI analyze your project, find issues,
            generate documentation, tests, diagrams and give you a complete engineering review.
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_upload:
    st.markdown("### 📤 Upload ZIP Project")
    st.caption("Upload your complete project as a ZIP file.")
    uploaded_zip = st.file_uploader(
        "Upload ZIP project",
        type=["zip"],
        label_visibility="collapsed",
    )
    st.caption("Supported: .py, .js, .ts, .java, .cpp, .html, .css, .md")

with hero_repo:
    st.markdown("### GitHub Repository")
    st.caption("Paste a public GitHub repository URL.")
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repo",
        label_visibility="collapsed",
    )
    load_clicked = st.button("🚀 Load Codebase", type="primary", use_container_width=True)

    if load_clicked:
        try:
            load_codebase(uploaded_zip, repo_url)
        except Exception as e:
            st.error(f"Failed to load project: {e}")

st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------- Empty State -----------------------------
if not files:
    stats_cards()
    feature_cards()
    mini_features_row()
    st.stop()


# ----------------------------- Loaded Project State -----------------------------
stats = project_stats(files)
security_findings = scan_security(files)
bug_findings = scan_bugs(files)
sec_score = security_score(security_findings)
qual_score = bug_score(bug_findings)

stats_cards(stats, sec_score, qual_score)

st.markdown(
    f"""
    <div class="ready-banner">
        <div class="ready-title">Loaded Project: <span style="color:#a855f7;">{project_name}</span></div>
        <div class="ready-sub">Your codebase is indexed and ready. Use the tools below to chat, scan, document, test and review your project.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


tabs = st.tabs(
    [
        "🧠 Overview",
        "💬 Chat",
        "🐞 Bugs",
        "🔒 Security",
        "📝 Docs",
        "🧪 Tests",
        "📊 Diagram",
        "🔄 Refactor",
        "🤖 Full Review",
        "🗂️ Files",
    ]
)


with tabs[0]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("AI Project Understanding")
    st.write("Generate project purpose, tech stack, entry points, folder explanations, architecture and onboarding notes.")
    if st.button("Analyze Project", use_container_width=True):
        with st.spinner("Analyzing project..."):
            result = summarize_project(project_path, files)
            st.markdown(result)
            path = save_markdown_report(project_name, "Project Analysis", result)
            st.success(f"Saved report: {path}")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[1]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Chat with Codebase")
    question = st.text_input("Ask anything about the uploaded code", placeholder="Example: Which file is the entry point?")

    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("Explain this project", use_container_width=True):
            question = "Explain this project"
    with q2:
        if st.button("Find security risks", use_container_width=True):
            question = "Find security risks in this project"
    with q3:
        if st.button("Suggest improvements", use_container_width=True):
            question = "How can I improve this codebase?"

    if st.button("Ask CodePilot", type="primary", use_container_width=True) and question.strip():
        with st.spinner("Searching relevant code and generating answer..."):
            st.markdown(ask_codebase(project_name, question.strip()))
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[2]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Bug Detection & Code Quality")
    st.metric("Quality Score", qual_score)
    if bug_findings:
        st.dataframe(bug_findings, use_container_width=True)
    else:
        st.success("No obvious bugs found by the static scanner.")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[3]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Security Scanner")
    st.metric("Security Score", sec_score)
    if security_findings:
        st.dataframe(security_findings, use_container_width=True)
    else:
        st.success("No obvious security issues found by the rule scanner.")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[4]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Documentation Generator")
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Generate README", use_container_width=True):
            with st.spinner("Generating README..."):
                readme, path = generate_readme(project_name, project_path, files)
                st.markdown(readme)
                st.success(f"Saved: {path}")

    with c2:
        if st.button("Generate Developer Guide", use_container_width=True):
            with st.spinner("Generating developer guide..."):
                guide, path = generate_developer_guide(project_name, project_path, files)
                st.markdown(guide)
                st.success(f"Saved: {path}")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[5]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Unit Test Generator")
    framework = st.selectbox("Framework", ["pytest", "unittest", "jest", "mocha"])
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Generate Tests", use_container_width=True):
            with st.spinner("Generating tests..."):
                tests = generate_tests(files, framework)
                st.markdown(tests)
                path = save_markdown_report(project_name, "Generated Tests", tests)
                st.success(f"Saved: {path}")

    with c2:
        if st.button("Generate Test Plan", use_container_width=True):
            with st.spinner("Generating test plan..."):
                plan = generate_test_plan(files)
                st.markdown(plan)
                path = save_markdown_report(project_name, "Test Plan", plan)
                st.success(f"Saved: {path}")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[6]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Architecture Diagram")
    st.write("Static diagram works without API key. AI diagram gives a cleaner architecture explanation when Gemini is configured.")
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Generate Static Diagram", use_container_width=True):
            st.markdown(generate_static_mermaid(files))

    with c2:
        if st.button("Generate AI Mermaid Diagram", use_container_width=True):
            with st.spinner("Generating diagram..."):
                diagram = generate_mermaid_diagram(files)
                st.markdown(diagram)
                path = save_markdown_report(project_name, "Architecture Diagram", diagram)
                st.success(f"Saved: {path}")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[7]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Refactoring Suggestions")
    if st.button("Suggest Refactoring", use_container_width=True):
        with st.spinner("Reviewing code quality..."):
            result = suggest_refactoring(files)
            st.markdown(result)
            path = save_markdown_report(project_name, "Refactoring Suggestions", result)
            st.success(f"Saved: {path}")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[8]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Full AI Engineer Review")
    st.write("Runs overview, security, bug detection, diagram, and refactoring together, then saves one complete report.")
    if st.button("Run Full Engineer Review", type="primary", use_container_width=True):
        with st.spinner("Running full review..."):
            review = run_engineer_review(project_name, project_path, files)
            report = build_full_report(review)
            st.markdown(report)
            path = save_markdown_report(project_name, "Full Engineering Review", report)
            st.success(f"Saved full report: {path}")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[9]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("File Explorer")
    st.code(folder_tree(project_path), language="text")

    selected = st.selectbox("Open file", [f["path"] for f in files])
    file_obj = next(f for f in files if f["path"] == selected)

    st.caption(f"{file_obj['lines']} lines")
    st.code(file_obj["content"][:20000], language=file_obj["extension"].replace(".", ""))
    st.markdown("</div>", unsafe_allow_html=True)
