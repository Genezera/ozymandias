# OZYMANDIAS // DARKWEB OSINT CONSOLE

> *"My name is Ozymandias, King of Kings; Look on my Works, ye Mighty, and despair!"*

**Ozymandias** is an advanced OSINT intelligence platform engineered for discovery, collection, enrichment, and analysis across the Onion Network.

Operating through multiple search engines and adaptive crawling mechanisms, Ozymandias continuously gathers intelligence, validates endpoints, enriches content, and maintains a persistent knowledge base of responsive services. The entire operation is orchestrated through a real-time HUD interface featuring telemetry, analytics, diagnostics, and consolidated reporting.

---

## ⚡ Features

* Multi-engine Onion search aggregation
* Adaptive crawler with resilient extraction mechanisms
* Automatic `.onion` search engine discovery
* Endpoint validation through Tor SOCKS proxies
* Persistent intelligence database (`knowledge.db`)
* Parallel enrichment and relevance ranking
* Streamlit-powered tactical HUD dashboard
* Real-time logs and telemetry monitoring
* Excel and Markdown reporting
* Automatic engine learning and endpoint reputation tracking

---

## 🛠 Requirements

* Python 3.10+
* Tor Browser (Windows) or Tor Service (Linux)
* pip

### Windows

```bash
pip install -r requirements.txt
```

Keep Tor Browser running (SOCKS5 port 9150).

### Kali Linux / Debian

```bash
chmod +x setup_kali.sh
./setup_kali.sh

source venv/bin/activate
```

---

## 🚀 Launching the Dashboard

```bash
python -m streamlit run dashboard.py
```

Configure:

* SOCKS Port (9150 Windows / 9050 Linux)
* Search query
* Thread count
* Discovery mode

Available modules:

* HUD
* Scanner
* Data Explorer
* Logs
* Search Engine Probe
* Reports

---

## 💻 Command Line Interface

```bash
python crawler.py -q "keyword" -t 8 -p 9150 -o report.md -D
```

### Parameters

| Parameter | Description             |
| --------- | ----------------------- |
| `-q`      | Search keyword          |
| `-t`      | Enrichment threads      |
| `-p`      | SOCKS proxy port        |
| `-o`      | Markdown report output  |
| `-D`      | Enable engine discovery |

Running without `-q` starts interactive mode.

---

## 🔍 Discovery Engine

Ozymandias can autonomously discover and integrate new Onion search engines.

Capabilities include:

* Harvesting public Onion sources
* Endpoint validation via `socks5h`
* Dynamic search template generation
* Success/failure tracking per engine
* Automatic integration of valid endpoints

All intelligence is persisted in the local knowledge base for future operations.

---

## 📊 Data Storage

| Component      | Description                           |
| -------------- | ------------------------------------- |
| `results`      | Search results with URL deduplication |
| `knowledge.db` | Engine intelligence database          |
| `logs`         | Timestamped operation logs            |
| `debug_html`   | Raw HTML engine captures              |
| `summary_*.md` | Search operation reports              |

---

## 🏗 Architecture

### Core Components

* `crawler.py` → Search engine, enrichment pipeline, discovery framework, CLI
* `dashboard.py` → Tactical HUD and operational interface
* `probe_engines.py` → Engine diagnostics and HTML capture
* `setup_kali.sh` → Environment provisioning
* `knowledge.db` → Persistent intelligence memory

---

## 🎛 Dashboard Modules

### 🧭 HUD

Operational metrics, engine performance, keyword analytics, historical trends.

### 🛰 Scanner

Live logs, auto-refresh monitoring, rapid access to operational artifacts.

### 📂 Data Explorer

Keyword filtering, engine analysis, Excel exports.

### 📝 Log Center

Log inspection, cleanup, auto-refresh diagnostics.

### 🧪 Engine Probe

Endpoint validation and HTML debugging.

### 📄 Reports

Markdown report generation and review.

---

## ⚙ Operational Recommendations

* Warm up Tor circuits before large operations.
* Use moderate thread counts to maintain stability.
* Prefer `socks5h` routing.
* Employ randomized delays between requests.
* Enable Discovery Mode when endpoint availability degrades.

---

## 🛡 Resilience & Recovery

* URL deduplication
* Automatic parser fallback mechanisms
* Persistent endpoint reputation tracking
* SQLite-backed intelligence storage
* Graceful handling of timeouts and service failures
* Continuous operation despite partial engine outages

---

## 🔬 Diagnostics

### Engine Probe

```bash
python probe_engines.py
```

Generates HTML captures for engine analysis.

### Logs

Review operational logs directly from the dashboard or inspect files under:

```text
logs/varredura_YYYYmmdd_HHMMSS.log
```

---

## ⚠ Disclaimer

This project is intended exclusively for:

* Security research
* Academic studies
* OSINT investigations
* Educational purposes

Users are solely responsible for ensuring compliance with applicable laws and regulations in their jurisdiction.

The authors do not endorse or support illegal activities of any kind.
