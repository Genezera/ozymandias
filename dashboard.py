import streamlit as st
import pandas as pd
import plotly.express as px
import os
import subprocess
import time
import socket
from datetime import datetime
import sys
import glob
import pathlib
import shutil

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Ozymandias // Tor OSINT Console",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ADVANCED CSS STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&display=swap');
:root {
  --bg: #0a0a0f;
  --panel: #0f1119;
  --accent: #00FF41;
  --accent2: #FF0055;
  --text: #e6f3e6;
}
.stApp {
  background: radial-gradient(1200px 600px at 80% -20%, rgba(0,255,65,0.08), transparent), 
              radial-gradient(800px 400px at 10% -10%, rgba(255,0,85,0.05), transparent), 
              var(--bg);
}
[data-testid="stSidebar"] {
  background: var(--panel);
  border-right: 1px solid rgba(0,255,65,0.2);
  box-shadow: 0 0 24px rgba(0,255,65,0.08) inset;
}
h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: var(--text); letter-spacing: 1px; }
.stMarkdown, .stText, .stPlotlyChart { font-family: 'Share Tech Mono', monospace; color: var(--text); }
.stButton>button {
  background: linear-gradient(90deg, rgba(0,255,65,0.12), rgba(255,0,85,0.12));
  border: 1px solid rgba(0,255,65,0.5);
  color: var(--text);
  text-transform: uppercase;
}
.stButton>button:hover {
  filter: brightness(1.2);
  box-shadow: 0 0 18px rgba(0,255,65,0.25), 0 0 8px rgba(255,0,85,0.25);
}
.stTabs [data-baseweb="tab-list"] { gap: 24px; }
.stTabs [data-baseweb="tab"] {
  height: 56px;
  background: linear-gradient(180deg, rgba(15,17,25,0.9), rgba(10,10,15,0.9));
  border-radius: 6px 6px 0 0;
  color: var(--text);
}
.stTabs [aria-selected="true"] {
  border-bottom: 3px solid var(--accent);
  color: var(--accent);
  text-shadow: 0 0 12px rgba(0,255,65,0.4);
}
.metric-box {
  background: rgba(15,17,25,0.9);
  border: 1px solid rgba(0,255,65,0.2);
  border-radius: 10px;
  padding: 14px;
}
</style>
""", unsafe_allow_html=True)

# --- HELPERS ---

def check_tor_port():
    ports = [9150, 9050]
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                s.close()
                return port
        except:
            pass
    return None

def load_data(file_path):
    if not os.path.exists(file_path):
        return None, "File not found."
    
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            return pd.DataFrame(), "File is empty."
        
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            
        return df, None
    except Exception as e:
        return None, str(e)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Data": "Date",
        "Termo Pesquisado": "Search Term",
        "Motor de Busca": "Search Engine",
        "Contextos": "Contexts",
        "Título": "Title",
        "Titulo": "Title",
    }
    renamed = {k: v for k, v in mapping.items() if k in df.columns}
    if renamed:
        df = df.rename(columns=renamed)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def list_logs():
    os.makedirs("logs", exist_ok=True)
    files = sorted(set(glob.glob("logs/scan_*.log") + glob.glob("logs/varredura_*.log")))
    return files
def read_log_tail(path, max_chars=8000):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read()
        return data[-max_chars:]
    except:
        return ""
def start_crawler(term, tor_port, mode="console", manual_port=None, threads=6, output_md=None, auto_discover=False):
    if (not tor_port and not manual_port) or not term:
        return False, "Invalid Tor status or search term."
    try:
        py = sys.executable or ("python" if os.name == 'nt' else "python3")
        args = [py, "crawler.py", "-q", term]
        port_to_use = manual_port or tor_port
        if port_to_use:
            args += ["-p", str(port_to_use)]
        if threads and isinstance(threads, int):
            args += ["-t", str(threads)]
        if output_md:
            args += ["-o", output_md]
        if auto_discover:
            args += ["-D"]
        if os.name == 'nt':
            if mode == "console":
                subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            if mode == "console":
                term_escaped = term.replace("'", "'\\''")
                port_flag = f" -p {port_to_use}" if port_to_use else ""
                cmd = f"{py} crawler.py -q '{term_escaped}'{port_flag} -t {threads}" + (f" -o {output_md}" if output_md else "")
                cmd = cmd + "; exec bash"
                terminal_cmds = [
                    ["x-terminal-emulator", "-e", "bash", "-lc", cmd],
                    ["gnome-terminal", "--", "bash", "-lc", cmd],
                    ["konsole", "-e", "bash", "-lc", cmd],
                    ["xterm", "-e", f"bash -lc \"{cmd}\""],
                ]
                launched = False
                for tc in terminal_cmds:
                    if shutil.which(tc[0]):
                        subprocess.Popen(tc)
                        launched = True
                        break
                if not launched:
                    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            else:
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return True, None
    except Exception as e:
        return False, str(e)
def run_probe():
    try:
        py = sys.executable or ("python" if os.name == 'nt' else "python3")
        if os.name == 'nt':
            subprocess.Popen([py, "probe_engines.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            cmd = f"{py} probe_engines.py; exec bash"
            terminal_cmds = [
                ["x-terminal-emulator", "-e", "bash", "-lc", cmd],
                ["gnome-terminal", "--", "bash", "-lc", cmd],
                ["konsole", "-e", "bash", "-lc", cmd],
                ["xterm", "-e", f"bash -lc \"{cmd}\""],
            ]
            launched = False
            for tc in terminal_cmds:
                if shutil.which(tc[0]):
                    subprocess.Popen(tc)
                    launched = True
                    break
            if not launched:
                subprocess.Popen([py, "probe_engines.py"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return True, None
    except Exception as e:
        return False, str(e)
def summarize_probe():
    os.makedirs("debug_html", exist_ok=True)
    files = sorted(glob.glob("debug_html/*.html"))
    names = [pathlib.Path(f).stem for f in files]
    return names

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00FF41;font-family:Orbitron;'>Ozymandias</h2>", unsafe_allow_html=True)
    tor_port = check_tor_port()
    st.subheader("📡 Network Status")
    if tor_port:
        st.success(f"TOR CONNECTED (Port {tor_port})")
    else:
        st.error("TOR DISCONNECTED")
        st.warning("Start Tor Browser or the Tor service.")
    st.markdown("---")
    st.subheader("🚀 Run Scanner")
    search_term = st.text_input("Query", placeholder='e.g. "example keyword"')
    manual_port_override = st.checkbox("Set SOCKS port manually", value=False, key="override_port")
    if manual_port_override:
        manual_port_str = st.text_input("SOCKS port (override)", value=str(tor_port) if tor_port else "")
        manual_port = int(manual_port_str) if manual_port_str.strip().isdigit() else None
        st.caption("Manual override for SOCKS port. If unchecked, auto-detection is used.")
    else:
        manual_port = None
    threads = st.slider("Threads", min_value=1, max_value=16, value=6)
    auto_discover = st.checkbox("Auto-discover new engines", value=True)
    run_mode = st.radio(
        "Run mode (Windows)",
        ["External console", "Background"],
        index=0 if os.name == "nt" else 0,
    )
    if st.button("Start scanner", key="btn_start_scanner"):
        if not tor_port and not manual_port:
            st.error("Connect to Tor first.")
        elif not search_term:
            st.warning("Type a query first.")
        else:
            ok, err = start_crawler(
                search_term,
                tor_port,
                mode="console" if run_mode == "External console" else "background",
                manual_port=manual_port,
                threads=threads,
                output_md=None,
                auto_discover=auto_discover,
            )
            if ok:
                st.success("Scanner started.")
            else:
                st.error(f"Failed to start: {err}")
    st.markdown("---")
    if st.button("Probe engines", key="btn_probe_sidebar"):
        ok, err = run_probe()
        if ok:
            st.info("Probe started.")
        else:
            st.error(f"Probe failed: {err}")
    st.caption(f"Build 3.1 | OS: {os.name.upper()}")

# --- MAIN AREA ---
st.markdown(
    "<h1 style='font-family:Orbitron;'>Ozymandias // Tor OSINT Console</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='border:1px solid rgba(0,255,65,0.3);padding:8px;border-radius:6px;'>"
    "OSINT research dashboard for Tor (.onion) discovery, enrichment, and reporting."
    "</div>",
    unsafe_allow_html=True,
)

# Load data
RESULTS_FILE = "search_results.xlsx"
df, error_msg = load_data(RESULTS_FILE)
if df is not None and not df.empty:
    df = normalize_columns(df)

# Tabs layout
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧭 HUD", "🛰️ Scanner", "📂 Data", "📝 Logs", "🧪 Engines"])

# --- TAB 1: OVERVIEW ---
with tab1:
    if df is not None and not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        total_links = len(df)
        unique_domains = (
            df["URL"]
            .apply(
                lambda x: x.split(".onion")[0] + ".onion"
                if isinstance(x, str) and ".onion" in x
                else "Other",
            )
            .nunique()
        )
        top_engine = df["Search Engine"].mode()[0] if "Search Engine" in df.columns else "N/A"
        last_update = (
            df["Date"].max().strftime("%Y-%m-%d %H:%M") if "Date" in df.columns else "N/A"
        )
        col1.metric("Total Links", total_links, delta_color="off")
        col2.metric("Unique Domains", unique_domains, delta_color="off")
        col3.metric("Top Engine", top_engine, delta_color="off")
        col4.metric("Last Capture", last_update, delta_color="off")
        st.markdown("---")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("📈 Links by Search Term")
            if "Search Term" in df.columns:
                term_counts = df["Search Term"].value_counts().reset_index()
                term_counts.columns = ["Term", "Count"]
                fig_bar = px.bar(
                    term_counts,
                    x="Term",
                    y="Count",
                    text="Count",
                    color="Count",
                    color_continuous_scale=px.colors.sequential.Greens,
                    template="plotly_dark",
                )
                fig_bar.update_traces(textposition='outside')
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)
            st.subheader("⏱️ Captures by Day")
            if "Date" in df.columns:
                df_time = df.copy()
                df_time["Day"] = df_time["Date"].dt.date
                time_counts = df_time.groupby("Day").size().reset_index(name="Captures")
                fig_time = px.line(
                    time_counts,
                    x="Day",
                    y="Captures",
                    markers=True,
                    template="plotly_dark",
                    color_discrete_sequence=["#00FF41"],
                )
                fig_time.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_time, use_container_width=True)
        with c2:
            st.subheader("🎯 Links by Engine")
            if "Search Engine" in df.columns:
                engine_counts = df["Search Engine"].value_counts().reset_index()
                engine_counts.columns = ["Engine", "Links"]
                fig_eng = px.bar(
                    engine_counts,
                    x="Engine",
                    y="Links",
                    text="Links",
                    template="plotly_dark",
                    color="Links",
                    color_continuous_scale=px.colors.sequential.Greens_r,
                )
                fig_eng.update_traces(textposition='outside')
                fig_eng.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_eng, use_container_width=True)
    elif df is not None and df.empty:
        st.info("The database exists but is empty. Run a scan to collect data.")
    else:
        st.warning(f"Data file not found or not accessible. ({error_msg})")
        st.markdown("👉 Start the crawler from the sidebar to generate the first report.")

# --- ABA 2: EXPLORADOR DE DADOS ---
with tab2:
    st.subheader("🛰️ Scanner")
    logs = list_logs()
    if logs:
        selected_log = st.selectbox("Select active log", logs, index=len(logs)-1)
        col_l1, col_l2 = st.columns([3,1])
        with col_l1:
            st.code(read_log_tail(selected_log, 12000), language="text")
        with col_l2:
            auto_refresh = st.checkbox("Auto-Refresh 10s", key="auto_refresh_scanner")
            if auto_refresh:
                time.sleep(10)
                st.rerun()
            if st.button("Open logs folder", key="btn_open_logs_scanner"):
                path = os.path.abspath("logs")
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    opener = shutil.which("xdg-open") or shutil.which("gnome-open")
                    if opener:
                        subprocess.Popen([opener, path])
    else:
        st.info("No logs yet. Start the scanner.")
with tab3:
    st.subheader("📂 Data Explorer")
    if df is not None and not df.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            search_query = st.text_input("Filter by keyword (URL, Title, Snippet, Contexts):")
        with col_f2:
            if "Search Engine" in df.columns:
                all_engines = ["All"] + list(df["Search Engine"].unique())
                engine_filter = st.selectbox("Filter by engine:", all_engines)
            else:
                engine_filter = "All"
        df_filtered = df.copy()
        if search_query:
            df_filtered = df_filtered[
                df_filtered.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
            ]
        if engine_filter != "All":
            df_filtered = df_filtered[df_filtered["Search Engine"] == engine_filter]
        st.markdown(f"Showing {len(df_filtered)} results")
        st.dataframe(
            df_filtered,
            column_config={
                "URL": st.column_config.LinkColumn("Onion link", display_text="Open"),
                "Snippet": st.column_config.TextColumn("Snippet", width="large"),
                "Contexts": st.column_config.TextColumn("Contexts", width="large"),
                "Date": st.column_config.DatetimeColumn("Date", format="YYYY-MM-DD HH:mm"),
            },
            use_container_width=True,
            height=600
        )
        with open(RESULTS_FILE, "rb") as f:
            st.download_button(
                label="📥 Download (Excel)",
                data=f.read(),
                file_name=f"ozymandias_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download-btn'
            )
    else:
        st.info("No data available yet.")

# --- ABA 3: FERRAMENTAS ---
with tab4:
    st.subheader("📝 Execution Logs")
    logs = list_logs()
    if logs:
        selected_log = st.selectbox("Select log", logs, index=len(logs)-1)
        col_l1, col_l2 = st.columns([3,1])
        with col_l1:
            st.code(read_log_tail(selected_log, 12000), language="text")
        with col_l2:
            auto_refresh = st.checkbox("Auto-Refresh 10s", key="auto_refresh_logs")
            if st.button("Open logs folder", key="btn_open_logs_logs"):
                path = os.path.abspath("logs")
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    opener = shutil.which("xdg-open") or shutil.which("gnome-open")
                    if opener:
                        subprocess.Popen([opener, path])
            if auto_refresh:
                time.sleep(10)
                st.rerun()
    else:
        st.info("No logs available.")
    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Clear logs", key="btn_clear_logs"):
            try:
                for f in logs:
                    os.remove(f)
                st.success("Logs deleted.")
            except Exception as e:
                st.error(f"Failed: {e}")
    with col_b2:
        if st.button("Clear report", key="btn_clear_report"):
            try:
                if os.path.exists(RESULTS_FILE):
                    os.remove(RESULTS_FILE)
                st.success("Report deleted.")
            except Exception as e:
                st.error(f"Failed: {e}")
with tab5:
    st.subheader("🧪 Engine Probe")
    col_p1, col_p2 = st.columns([2,1])
    with col_p1:
        names = summarize_probe()
        if names:
            df_probe = pd.DataFrame({"Engine": names, "Status": ["OK"]*len(names)})
            st.dataframe(df_probe, use_container_width=True, height=400)
        else:
            st.info("No probe results found.")
    with col_p2:
        if st.button("Open debug_html folder", key="btn_open_debug_html"):
            path = os.path.abspath("debug_html")
            if os.name == 'nt':
                os.startfile(path)
            else:
                opener = shutil.which("xdg-open") or shutil.which("gnome-open")
                if opener:
                    subprocess.Popen([opener, path])
