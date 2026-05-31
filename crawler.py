#!/usr/bin/env python3
import pandas as pd
import requests
import socket
from bs4 import BeautifulSoup
from termcolor import colored
import time
import sys
import urllib.parse
import os
import random
import re
import logging
from datetime import datetime
import unicodedata
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

SESSIONS = {}

# --- CONFIG ---
SEARCH_ENGINES = {
    'Ahmia': {
        'url': 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}'
    },
    'Torch': {
        'url': 'http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P={query}'
    },
    'Haystak': {
        'url': 'http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/?q={query}'
    },
    'OnionLand': {
        'url': 'http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search?q={query}'
    },
    'TorDex': {
        'url': 'http://tordexu73joywapk2txdr54jed4imqledpcvcuf75qsas2gwdgksvnyd.onion/search?q={query}'
    },
    'DarknetSearch': {
        'url': 'http://darkent74yfc3qe7vhd2ms53ynr3l5hbjz4on2x76e7odjiyrjlirvid.onion/search?q={query}'
    },
    'Tor66': {
        'url': 'http://tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion/search?q={query}'
    },
    'OnionRealm': {
        'url': 'http://orealmvxooetglfeguv2vp65a3rig2baq2ljc7jxxs4hsqsrcemkxcad.onion/search?query={query}&action=search'
    },
    'Excavator': {
        'url': 'http://2fd6cemt4gmccflhm6imvdfvli3nf7zn6rfrwpsy7uhxrgbypvwf5fad.onion/search?query={query}'
    },
    'TthSearch': {
        'url': 'http://tth4he7kdfmfwq2k7yaj2ggjdva7rdpbch42q6xgoorbabjeklyfbmyd.onion/search?query={query}'
    },
    'Labyrinth': {
        'url': 'http://labyrinthkh3uokhu2a5nwi4e6kedmbkxar3w6vgm2ipdb7ms3zdzlad.onion/search?query={query}&lang=english&sort-by=relevant&tab=all'
    },
    'DeepSearch': {
        'url': 'http://dgwq7uzh5ro2f7p34begy4kmxue5gst7lk2spxda63zkrpuegtj4opyd.onion/search.php?q={query}'
    }
}
DEFAULT_SEARCH_ENGINES = [
    "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}",
    "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search?q={query}",
    "http://iy3544gmoeclh5de6gez2256v6pjh4omhpqdh2wpeeppjtvqmjhkfwad.onion/torgle/?query={query}",
    "http://amnesia7u5odx5xbwtpnqk3edybgud5bmiagu75bnqx2crntw5kry7ad.onion/search?query={query}",
    "http://kaizerwfvp5gxu6cppibp7jhcqptavq3iqef66wbxenh6a2fklibdvid.onion/search?q={query}",
    "http://anima4ffe27xmakwnseih3ic2y7y3l6e7fucwk4oerdn4odf7k74tbid.onion/search?q={query}",
    "http://tornadoxn3viscgz647shlysdy7ea5zqzwda7hierekeuokh5eh5b3qd.onion/search?q={query}",
    "http://tornetupfu7gcgidt33ftnungxzyfq2pygui5qdoyss34xbgx2qruzid.onion/search?q={query}",
    "http://torlbmqwtudkorme6prgfpmsnile7ug2zm4u3ejpcncxuhpu4k2j4kyd.onion/index.php?a=search&q={query}",
    "http://findtorroveq5wdnipkaojfpqulxnkhblymc7aramjzajcvpptd4rjqd.onion/search?q={query}",
    "http://2fd6cemt4gmccflhm6imvdfvli3nf7zn6rfrwpsy7uhxrgbypvwf5fad.onion/search?query={query}",
    "http://oniwayzz74cv2puhsgx4dpjwieww4wdphsydqvf5q7eyz4myjvyw26ad.onion/search.php?s={query}",
    "http://tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion/search?q={query}",
    "http://3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion/oss/index.php?search={query}",
    "http://torgolnpeouim56dykfob6jh5r2ps2j73enc42s2um4ufob3ny4fcdyd.onion/?q={query}",
    "http://searchgf7gdtauh7bhnbyed4ivxqmuoat3nm6zfrg3ymkq6mtnpye3ad.onion/search?q={query}"
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
]
ENRICH_FETCH_LIMIT = 15
LOGGER = None
LOG_FILE = None
KNOWLEDGE_FILE = 'engine_knowledge.json'
KNOWLEDGE_DB = 'knowledge.db'

def init_logger():
    global LOGGER, LOG_FILE
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs('logs', exist_ok=True)
    LOG_FILE = os.path.join('logs', f"scan_{ts}.log")
    LOGGER = logging.getLogger("crawler")
    LOGGER.setLevel(logging.DEBUG)
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(formatter)
    if not LOGGER.handlers:
        LOGGER.addHandler(fh)
    return LOGGER, LOG_FILE
def load_knowledge():
    try:
        if os.path.exists(KNOWLEDGE_FILE):
            with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {'engines': {}}
def save_knowledge(data):
    try:
        with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass
def record_engine_result(knowledge, name, host, success):
    eng = knowledge['engines'].setdefault(name, {'candidates': {}})
    cand = eng['candidates'].setdefault(host, {'success': 0, 'fail': 0, 'last': None})
    if success:
        cand['success'] += 1
    else:
        cand['fail'] += 1
    cand['last'] = datetime.now().isoformat()
    save_knowledge(knowledge)
def best_candidate_host(knowledge, name):
    eng = knowledge['engines'].get(name)
    if not eng:
        return None
    items = []
    for host, stats in eng.get('candidates', {}).items():
        score = stats.get('success', 0) - stats.get('fail', 0)
        items.append((score, host))
    if not items:
        return None
    items.sort(key=lambda x: x[0], reverse=True)
    return items[0][1]
def swap_host_in_url(url, new_host):
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme or 'http', new_host, parsed.path, parsed.params, parsed.query, parsed.fragment))
def extract_onion_hosts_from_html(html):
    hosts = set()
    for m in re.finditer(r'([a-z2-7]{16,56}\.onion)', html, re.IGNORECASE):
        hosts.add(m.group(1))
    return list(hosts)
def guess_search_template(host):
    bases = [
        "http://{host}/search?q={query}",
        "http://{host}/?q={query}",
        "http://{host}/search?query={query}",
        "http://{host}/cgi-bin/omega/omega?P={query}",
        "http://{host}/search.php?q={query}",
        "http://{host}/torgle/?query={query}",
        "http://{host}/oss/index.php?search={query}"
    ]
    out = []
    for b in bases:
        out.append(b.replace("{host}", host))
    return out
def discover_new_engines(proxies, max_results=25):
    sources = [
        "dark web search engines onion list",
        "onion search engine list",
        "tor search engine list",
        "darknet search engine index"
    ]
    discovered = []
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        for q in sources:
            r = requests.get('https://duckduckgo.com/html/', params={'q': q}, headers=headers, timeout=40)
            html = r.text if r and r.status_code == 200 else ""
            hosts = extract_onion_hosts_from_html(html)
            for h in hosts:
                if h not in discovered:
                    discovered.append(h)
                if len(discovered) >= max_results:
                    break
            if len(discovered) >= max_results:
                break
    except:
        pass
    endpoints = []
    for host in discovered:
        templates = guess_search_template(host)
        ok_endpoint = None
        for ep in templates:
            test = ep.format(query=urllib.parse.quote_plus("test"))
            resp = fetch_url(test, proxies, timeout=40, retries=1)
            if resp and resp.status_code == 200:
                ok_endpoint = ep
                try:
                    db_upsert_endpoint(host, ep, "engine", ok=True)
                except:
                    pass
                break
            else:
                try:
                    db_upsert_endpoint(host, ep, "engine", ok=False)
                except:
                    pass
        if ok_endpoint:
            endpoints.append(ok_endpoint)
    return endpoints
def adapt_engine(name, engine_config, proxies, knowledge, max_candidates=8):
    query = f"{name} onion"
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get('https://duckduckgo.com/html/', params={'q': query}, headers=headers, timeout=40)
        html = r.text if r and r.status_code == 200 else ""
    except:
        html = ""
    candidates = extract_onion_hosts_from_html(html)[:max_candidates]
    url_test = engine_config['url'].format(query='test')
    best = None
    for host in candidates:
        test_url = swap_host_in_url(url_test, host)
        resp = fetch_url(test_url, proxies, timeout=50, retries=1)
        ok = bool(resp and resp.status_code == 200)
        record_engine_result(knowledge, name, host, ok)
        if ok and best is None:
            best = host
    return best
def init_db():
    try:
        conn = sqlite3.connect(KNOWLEDGE_DB)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS engines (name TEXT, host TEXT, success INTEGER, fail INTEGER, last TEXT, UNIQUE(name, host))")
        cur.execute("CREATE TABLE IF NOT EXISTS links (url TEXT PRIMARY KEY, title TEXT, engine TEXT, term TEXT, status TEXT, score INTEGER, contexts TEXT, discovered_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS endpoints (source TEXT, endpoint TEXT, type TEXT, added_at TEXT, last_ok_at TEXT, ok_count INTEGER, fail_count INTEGER, UNIQUE(source, endpoint))")
        cur.execute("CREATE TABLE IF NOT EXISTS keywords (term TEXT, keyword TEXT, weight REAL, updated_at TEXT, UNIQUE(term, keyword))")
        conn.commit()
        conn.close()
    except:
        pass
def db_exec(query, params=()):
    try:
        conn = sqlite3.connect(KNOWLEDGE_DB)
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        conn.close()
    except:
        pass
def db_upsert_engine(name, host, success_inc=0, fail_inc=0, last_ts=None):
    ts = last_ts or datetime.now().isoformat()
    db_exec("INSERT INTO engines (name, host, success, fail, last) VALUES (?, ?, ?, ?, ?) ON CONFLICT(name, host) DO UPDATE SET success = success + ?, fail = fail + ?, last = ?", (name, host, success_inc, fail_inc, ts, success_inc, fail_inc, ts))
def db_upsert_link(url, title, engine, term, status, score, contexts):
    db_exec("INSERT OR REPLACE INTO links (url, title, engine, term, status, score, contexts, discovered_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (url, title, engine, term, status, score if isinstance(score, int) else 0, contexts or "", datetime.now().isoformat()))
def db_upsert_endpoint(source, endpoint, type_name, ok=False):
    ts = datetime.now().isoformat()
    if ok:
        db_exec("INSERT INTO endpoints (source, endpoint, type, added_at, last_ok_at, ok_count, fail_count) VALUES (?, ?, ?, ?, ?, 1, 0) ON CONFLICT(source, endpoint) DO UPDATE SET ok_count = ok_count + 1, last_ok_at = ?", (source, endpoint, type_name, ts, ts, ts))
    else:
        db_exec("INSERT INTO endpoints (source, endpoint, type, added_at, last_ok_at, ok_count, fail_count) VALUES (?, ?, ?, ?, NULL, 0, 1) ON CONFLICT(source, endpoint) DO UPDATE SET fail_count = fail_count + 1", (source, endpoint, type_name, ts))
def db_upsert_keyword(term, keyword, delta):
    ts = datetime.now().isoformat()
    db_exec("INSERT INTO keywords (term, keyword, weight, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(term, keyword) DO UPDATE SET weight = weight + ?, updated_at = ?", (term, keyword, float(delta), ts, float(delta), ts))
def get_top_keywords(term, limit=6):
    try:
        conn = sqlite3.connect(KNOWLEDGE_DB)
        cur = conn.cursor()
        cur.execute("SELECT keyword FROM keywords WHERE term = ? ORDER BY weight DESC LIMIT ?", (term, limit))
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except:
        return []
def tokenize_text(s):
    if not isinstance(s, str):
        return []
    s = normalize_text(s)
    toks = re.findall(r'[a-z0-9]{3,}', s)
    stop = set(['http','https','www','onion'])
    return [t for t in toks if t not in stop]
def update_keywords_for_term(term, text):
    toks = tokenize_text(text)
    if not toks:
        return
    freq = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    for k, v in freq.items():
        db_upsert_keyword(term, k, v)

def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s

def build_term_variants(term):
    t = normalize_text(term).strip()
    variants = set()
    variants.add(t)
    variants.add(t.replace(' ', '-'))
    variants.add(t.replace('-', ' '))
    if t.endswith('s'):
        variants.add(t[:-1])
    if t.endswith('es'):
        variants.add(t[:-2])
    tokens = [tok for tok in re.split(r'[\s\-_/]+', t) if tok]
    for tok in tokens:
        variants.add(tok)
    return list(variants)

def analyze_text_for_term(text, term_variants, max_contexts=8):
    txt = normalize_text(text)
    occurrences = 0
    contexts = []
    for v in term_variants:
        for m in re.finditer(re.escape(v), txt):
            occurrences += 1
            start = max(0, m.start() - 80)
            end = min(len(txt), m.end() + 80)
            contexts.append(txt[start:end])
            if len(contexts) >= max_contexts:
                break
        if len(contexts) >= max_contexts:
            break
    score = occurrences
    return occurrences, contexts, score

def analyze_page_for_term(soup, term):
    variants = build_term_variants(term)
    title = soup.title.get_text(strip=True) if soup.title else ""
    meta_desc = ""
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta and meta.get('content'):
        meta_desc = meta.get('content', '').strip()
    body_text = soup.get_text(separator=' ', strip=True)
    occ_title, ctx_title, _ = analyze_text_for_term(title, variants, max_contexts=2)
    occ_meta, ctx_meta, _ = analyze_text_for_term(meta_desc, variants, max_contexts=2)
    occ_body, ctx_body, _ = analyze_text_for_term(body_text, variants, max_contexts=8)
    total_occ = occ_title + occ_meta + occ_body
    score = total_occ + (2 if occ_title else 0) + (1 if occ_meta else 0)
    contexts = ctx_title + ctx_meta + ctx_body
    try:
        update_keywords_for_term(term, body_text)
    except:
        pass
    return {
        'Occurrences': total_occ,
        'Score': score,
        'Contexts': " | ".join(contexts[:8]),
        'ExtractedTitle': title,
        'ExtractedMetaDescription': meta_desc
    }
def extract_onion_links_from_html(html):
    found = set()
    for m in re.finditer(r'([a-z2-7]{16,56}\.onion[^\s\"\'<>]*)', html, re.IGNORECASE):
        found.add(m.group(1))
    return list(found)

def get_headers():
    ua = random.choice(USER_AGENTS)
    return {
        'User-Agent': ua,
        'Accept-Language': 'en-US,en;q=0.8,pt-BR;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
def get_session(proxies):
    key = json.dumps(proxies, sort_keys=True)
    sess = SESSIONS.get(key)
    if sess:
        return sess
    s = requests.Session()
    s.proxies = proxies
    SESSIONS[key] = s
    return s

def normalize_onion_url(href, base_url):
    if not href:
        return None
    if href.startswith('//'):
        href = 'http:' + href
    abs_url = urllib.parse.urljoin(base_url, href)
    parsed = urllib.parse.urlparse(abs_url)
    if '.onion' in abs_url and not parsed.scheme:
        abs_url = 'http://' + abs_url
    return abs_url
def extract_onion_from_href(href_value, base_url):
    if not href_value:
        return None
    full = normalize_onion_url(href_value, base_url)
    if not full:
        return None
    unquoted_full = urllib.parse.unquote_plus(full)
    if '.onion' in unquoted_full:
        parsed = urllib.parse.urlparse(unquoted_full)
        qs = urllib.parse.parse_qs(parsed.query)
        for key in ['u', 'url', 'target', 'redir', 'href', 'address', 'site', 'link']:
            if key in qs:
                try:
                    candidate = qs[key][0]
                    candidate = urllib.parse.unquote_plus(candidate)
                    if '.onion' in candidate:
                        if not urllib.parse.urlparse(candidate).scheme:
                            candidate = 'http://' + candidate
                        return candidate
                except:
                    pass
        m = re.search(r'([a-z2-7]{16,56}\.onion[^\s\"\'<>]*)', unquoted_full)
        if m:
            candidate = m.group(1)
            if not urllib.parse.urlparse(candidate).scheme:
                candidate = 'http://' + candidate
            return candidate
        return full
    return None

def fetch_url(url, proxies, timeout=60, retries=2):
    attempt = 0
    while attempt <= retries:
        try:
            headers = get_headers()
            if LOGGER:
                LOGGER.debug(f"Request: {url} attempt={attempt + 1} timeout={timeout}")
            session = get_session(proxies)
            resp = session.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                if LOGGER:
                    LOGGER.debug(f"Response 200: {url} size={len(resp.text)}")
                return resp
            if resp.status_code in (429, 503):
                delay = random.uniform(3, 7) * (attempt + 1)
                if LOGGER:
                    LOGGER.warning(f"Response {resp.status_code}: {url} waiting {delay:.1f}s")
                time.sleep(delay)
            else:
                if LOGGER:
                    LOGGER.error(f"Response {resp.status_code}: {url}")
                return None
        except requests.exceptions.Timeout:
            delay = random.uniform(2, 4) * (attempt + 1)
            if LOGGER:
                LOGGER.warning(f"Timeout: {url} waiting {delay:.1f}s")
            time.sleep(delay)
        except requests.exceptions.ConnectionError:
            delay = random.uniform(2, 4) * (attempt + 1)
            if LOGGER:
                LOGGER.warning(f"Connection failed: {url} waiting {delay:.1f}s")
            time.sleep(delay)
        attempt += 1
    if LOGGER:
        LOGGER.error(f"No response after {retries + 1} attempts: {url}")
    return None
def get_tor_port():
    """Auto-detect Tor port (9150 or 9050)."""
    ports = [9150, 9050]
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                return port
        except:
            pass
    return None

def check_tor_connection(proxies):
    try:
        print(colored("[INFO] Checking Tor connection...", "yellow"))
        r = requests.get('https://check.torproject.org/api/ip', proxies=proxies, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data.get('IsTor', False):
                print(colored(f"[SUCCESS] Connected to Tor. IP: {data.get('IP')}", "green"))
                return True
            else:
                print(colored(f"[WARNING] Not connected to Tor. IP: {data.get('IP')}", "red", attrs=['bold']))
                return False
    except Exception:
        pass
    try:
        test_url = SEARCH_ENGINES['Ahmia']['url'].format(query=urllib.parse.quote_plus("test"))
        r2 = requests.get(test_url, proxies=proxies, timeout=30, headers=get_headers())
        if r2.status_code in (200, 403, 429):
            print(colored("[INFO] SOCKS connection looks functional for .onion", "green"))
            return True
    except Exception as e2:
        print(colored(f"[ERROR] Failed to validate Tor connection: {e2}", "red"))
        return False
    return False

def parse_generic(soup, term, base_url):
    """Best-effort result extraction for simple engines."""
    results = []
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        resolved = extract_onion_from_href(href, base_url) if href else None
        if resolved and '.onion' in resolved:
            title = link.get_text(strip=True) or resolved
            snippet = ""
            parent = link.parent
            if parent:
                snippet = parent.get_text(strip=True)[:200]
            results.append({
                'Search Term': term,
                'Title': title,
                'URL': resolved,
                'Snippet': snippet,
                'Date': pd.Timestamp.now()
            })
    return results
def fetch_external_engine(endpoint, term, proxies):
    url = endpoint.format(query=urllib.parse.quote_plus(term))
    headers = get_headers()
    try:
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=50)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        found = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            resolved = extract_onion_from_href(href, url)
            if resolved and '.onion' in resolved:
                title = a.get_text(strip=True) or resolved
                found.append({
                    'Search Term': term,
                    'Title': title,
                    'URL': resolved,
                    'Snippet': '',
                    'Search Engine': urllib.parse.urlparse(url).netloc,
                    'Date': pd.Timestamp.now()
                })
        try:
            host = urllib.parse.urlparse(url).netloc
            db_upsert_endpoint(host, url, "engine", ok=True)
        except:
            pass
        return found
    except:
        try:
            host = urllib.parse.urlparse(url).netloc
            db_upsert_endpoint(host, url, "engine", ok=False)
        except:
            pass
        return []
def aggregate_external_engines(term, proxies, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(fetch_external_engine, ep, term, proxies) for ep in DEFAULT_SEARCH_ENGINES]
        for fut in as_completed(futures):
            try:
                items = fut.result()
                results.extend(items or [])
            except:
                pass
    seen = set()
    unique = []
    for r in results:
        url = r.get('URL')
        if not url:
            continue
        clean = url.rstrip('/')
        if clean in seen:
            continue
        seen.add(clean)
        unique.append(r)
    return unique

def perform_form_search(home_url, term, proxies, engine_name):
    try:
        if LOGGER:
            LOGGER.info(f"FormFallback start engine='{engine_name}' home='{home_url}'")
        resp = fetch_url(home_url, proxies, timeout=60, retries=1)
        if not resp or resp.status_code != 200:
            if LOGGER:
                LOGGER.warning(f"FormFallback noresp engine='{engine_name}' status='{resp.status_code if resp else 'none'}'")
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        forms = soup.find_all('form')
        if not forms:
            if LOGGER:
                LOGGER.info(f"FormFallback no_forms engine='{engine_name}'")
            return []
        target_names = set(['q','query','search','s','term','keyword'])
        chosen = None
        for f in forms:
            inputs = f.find_all('input')
            names = set([i.get('name','').lower() for i in inputs if i.get('name')])
            if names & target_names:
                chosen = f
                break
        if not chosen:
            chosen = forms[0]
        data = {}
        for i in chosen.find_all('input'):
            name = i.get('name')
            if not name:
                continue
            t = (i.get('type') or '').lower()
            if name.lower() in target_names or t in ('text','search'):
                data[name] = term
            elif t in ('hidden','submit','radio','checkbox'):
                val = i.get('value') or ''
                if t in ('radio','checkbox'):
                    if i.has_attr('checked'):
                        data[name] = val
                else:
                    data[name] = val
        action = chosen.get('action') or home_url
        method = (chosen.get('method') or 'get').lower()
        submit_url = urllib.parse.urljoin(home_url, action)
        headers = get_headers()
        r = None
        if method == 'post':
            r = requests.post(submit_url, data=data, headers=headers, proxies=proxies, timeout=60)
        else:
            r = requests.get(submit_url, params=data, headers=headers, proxies=proxies, timeout=60)
        if not r or r.status_code != 200:
            if LOGGER:
                LOGGER.warning(f"FormFallback submit_fail engine='{engine_name}' url='{submit_url}' status='{r.status_code if r else 'none'}'")
            return []
        rsoup = BeautifulSoup(r.text, 'html.parser')
        found = parse_generic(rsoup, term, submit_url)
        for x in found:
            x['Search Engine'] = engine_name
        if LOGGER:
            LOGGER.info(f"FormFallback ok engine='{engine_name}' url='{submit_url}' count={len(found)}")
        return found
    except:
        if LOGGER:
            LOGGER.exception(f"FormFallback error engine='{engine_name}'")
        return []

def find_next_page(soup, current_url):
    """Attempt to find the next results page."""
    link = soup.find('link', rel='next')
    if link and link.get('href'):
        return link.get('href')
    
    a_rel_next = soup.find('a', attrs={'rel': 'next'})
    if a_rel_next and a_rel_next.get('href'):
        return a_rel_next.get('href')
    
    next_regex = re.compile(r'(next|próxima|proxima|seguinte|older|following|more|siguiente|suivant|avançar|avancar|>>|›|»)', re.IGNORECASE)
    
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True).lower()
        if next_regex.search(text):
            return a['href']
        classes = a.get('class') or []
        if any('next' in str(c).lower() for c in classes):
            return a['href']
            
    def _extract_current_page(url, soup_obj):
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        for key in ['page', 'p', 'pg']:
            if key in qs:
                try:
                    return int(qs[key][0])
                except:
                    pass
        indicators = ['active', 'current', 'selected', 'page-current']
        for cls in indicators:
            el = soup_obj.find(class_=cls)
            if el:
                t = el.get_text(strip=True)
                if t.isdigit():
                    try:
                        return int(t)
                    except:
                        pass
        return None
    
    numeric_candidates = []
    for a in soup.find_all('a', href=True):
        t = a.get_text(strip=True)
        if not t:
            continue
        m = re.fullmatch(r'\d+', t)
        if m:
            try:
                n = int(t)
                numeric_candidates.append((n, a['href']))
            except:
                pass
    
    if numeric_candidates:
        current_page = _extract_current_page(current_url, soup)
        numeric_candidates.sort(key=lambda x: x[0])
        if current_page is not None:
            for n, href in numeric_candidates:
                if n > current_page:
                    return href
        else:
            for n, href in numeric_candidates:
                if n > 1:
                    return href
            return numeric_candidates[0][1]
    
    return None

def find_next_page_torch(soup, current_url):
    parsed = urllib.parse.urlparse(current_url)
    qs = urllib.parse.parse_qs(parsed.query)
    def _get_int(d, k, default):
        try:
            return int(d.get(k, [default])[0])
        except:
            return default
    current_top = _get_int(qs, 'TOPDOC', 0)
    current_page = _get_int(qs, '[', 1)  # '[=' vira chave '['
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True).lower()
        if 'omega' in href and ('TOPDOC=' in href or '%5B=' in href):
            if re.search(r'(next|próxima|proxima|>>|›|»)', text, re.IGNORECASE):
                return href
            try:
                hq = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                top = _get_int(hq, 'TOPDOC', -1)
                if top > current_top:
                    return href
            except:
                continue
    next_qs = {k: v[:] for k, v in qs.items()}
    next_qs['TOPDOC'] = [str(current_top + 10 if current_top >= 0 else 10)]
    next_qs['['] = [str(current_page + 1)]
    new_query = urllib.parse.urlencode(next_qs, doseq=True)
    next_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    return next_url

def parse_ahmia(soup, term, base_url):
    results = []
    items = soup.select('li.result') or soup.select('li[class*=\"result\"]') or soup.select('div.result') or soup.select('article.result') or soup.select('#results li') or soup.select('#results .result')
    if items:
        for item in items:
            link_tag = item.find('a', href=True)
            resolved_link = None
            link_title = None
            if link_tag:
                resolved_link = extract_onion_from_href(link_tag.get('href'), base_url)
                link_title = link_tag.get_text(strip=True)
            if not resolved_link:
                data_href = item.get('data-href') or item.get('data-url') or item.get('data-link')
                if data_href:
                    resolved_link = extract_onion_from_href(data_href, base_url)
            if not resolved_link:
                for a in item.find_all('a', href=True):
                    candidate = extract_onion_from_href(a.get('href'), base_url)
                    if candidate and '.onion' in candidate:
                        resolved_link = candidate
                        if not link_title:
                            link_title = a.get_text(strip=True)
                        break
            if not resolved_link or '.onion' not in resolved_link:
                continue
            snippet_tag = item.find('p') or item.find('div', class_=re.compile(r'(snippet|desc|text)', re.IGNORECASE))
            results.append({
                'Search Term': term,
                'Search Engine': 'Ahmia',
                'Title': (link_title or resolved_link),
                'URL': resolved_link,
                'Snippet': snippet_tag.get_text(strip=True)[:200] if snippet_tag else "",
                'Date': pd.Timestamp.now()
            })
    else:
        results = parse_generic(soup, term, base_url)
        for r in results:
            r['Search Engine'] = 'Ahmia'
    return results

def search_engine(name, engine_config, term, proxies):
    """Search a specific engine with basic pagination support."""
    results = []
    
    knowledge = load_knowledge()
    base_url = engine_config['url'].format(query=urllib.parse.quote_plus(term))
    override = best_candidate_host(knowledge, name)
    current_url = swap_host_in_url(base_url, override) if override else base_url
    
    # Safety limit to avoid infinite loops
    MAX_PAGES = 1 if name == 'Ahmia' else 3 
    pages_crawled = 0
    
    print(f"  > Searching for '{term}' on {name}...")
    if LOGGER:
        LOGGER.info(f"Search start term='{term}' engine='{name}' url='{current_url}'")
    
    while current_url and pages_crawled < MAX_PAGES:
        if pages_crawled > 0:
            print(f"    >> Fetching page {pages_crawled + 1}...")
        if LOGGER:
            LOGGER.info(f"Page {pages_crawled + 1} engine='{name}' url='{current_url}'")
            
        try:
            resp = fetch_url(current_url, proxies, timeout=60, retries=2)
            
            if resp and resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                record_engine_result(knowledge, name, urllib.parse.urlparse(current_url).netloc, True)
                try:
                    db_upsert_engine(name, urllib.parse.urlparse(current_url).netloc, success_inc=1)
                except:
                    pass
                
                page_results = []
                
                if name == 'Ahmia':
                    page_results = parse_ahmia(soup, term, current_url)
                else:
                    # Generic parser
                    generic_results = parse_generic(soup, term, current_url)
                    # Adiciona o nome do motor
                    for res in generic_results:
                        res['Search Engine'] = name
                    page_results.extend(generic_results)
                if pages_crawled == 0 and len(page_results) == 0:
                    try:
                        parsed = urllib.parse.urlparse(current_url)
                        home_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, '/', '', '', ''))
                        print(colored("    [?] Form-based fallback on the homepage", "yellow"))
                        if LOGGER:
                            LOGGER.info(f"Form fallback engine='{name}' home='{home_url}'")
                        form_results = perform_form_search(home_url, term, proxies, name)
                        page_results.extend(form_results or [])
                    except:
                        pass
                    
                results.extend(page_results)
                print(colored(f"    -> {len(page_results)} results on this page.", "cyan"))
                if LOGGER:
                    LOGGER.info(f"Results collected engine='{name}' page={pages_crawled + 1} count={len(page_results)}")
                
                try:
                    visited = set()
                    for r in page_results:
                        url = r.get('URL')
                        if not isinstance(url, str) or '.onion' not in url:
                            continue
                        if url in visited:
                            continue
                        visited.add(url)
                        if LOGGER:
                            LOGGER.debug(f"Analyzing term on url='{url}'")
                        page_resp = fetch_url(url, proxies, timeout=45, retries=1)
                        if page_resp and page_resp.status_code == 200:
                            page_soup = BeautifulSoup(page_resp.text, 'html.parser')
                            analysis = analyze_page_for_term(page_soup, term)
                            r.update(analysis)
                            r['Status'] = '200'
                            try:
                                db_upsert_link(
                                    url,
                                    r.get('Title') or "",
                                    name,
                                    term,
                                    r.get('Status'),
                                    r.get('Score'),
                                    r.get('Contexts'),
                                )
                            except:
                                pass
                            try:
                                extras = extract_onion_links_from_html(page_resp.text)
                                for ex in extras:
                                    ex_url = ex if urllib.parse.urlparse(ex).scheme else 'http://' + ex
                                    db_upsert_link(ex_url, "", "discovered", term, "new", 0, "")
                            except:
                                pass
                        else:
                            r['Status'] = str(page_resp.status_code) if page_resp else 'error'
                            try:
                                db_upsert_link(url, r.get('Title') or "", name, term, r.get('Status'), 0, "")
                            except:
                                pass
                except Exception as e:
                    if LOGGER:
                        LOGGER.exception("Failed to analyze result pages")
                
                # Try to find the next page
                if name == 'Torch':
                    next_link = find_next_page_torch(soup, current_url)
                elif name == 'Ahmia':
                    next_link = None
                else:
                    next_link = find_next_page(soup, current_url)
                if next_link:
                    # Resolve relative URL if needed
                    current_url = urllib.parse.urljoin(current_url, next_link)
                    pages_crawled += 1
                    
                    # Random pause to reduce rate limits and allow Tor circuits to stabilize
                    wait_time = random.uniform(5, 10)
                    print(colored(f"    ... Waiting {wait_time:.1f}s before next page ...", "yellow"))
                    if LOGGER:
                        LOGGER.info(f"Next page engine='{name}' wait={wait_time:.1f}s next='{current_url}'")
                    time.sleep(wait_time)
                else:
                    if LOGGER:
                        LOGGER.info(f"No next page engine='{name}'")
                    break # No more pages
                    
            else:
                print(colored(f"    [X] {name} returned status {resp.status_code if resp else 'no response'}", "red"))
                if LOGGER:
                    LOGGER.error(f"Engine request failed engine='{name}' status='{resp.status_code if resp else 'none'}'")
                record_engine_result(knowledge, name, urllib.parse.urlparse(current_url).netloc, False)
                try:
                    db_upsert_engine(name, urllib.parse.urlparse(current_url).netloc, fail_inc=1)
                except:
                    pass
                new_host = adapt_engine(name, engine_config, proxies, knowledge)
                if new_host:
                    current_url = swap_host_in_url(base_url, new_host)
                    print(colored(f"    [+] Adaptation: using host {new_host} for {name}", "yellow"))
                    if LOGGER:
                        LOGGER.info(f"Adaptation engine='{name}' host='{new_host}'")
                    time.sleep(random.uniform(3, 6))
                    continue
                break
                
        except requests.exceptions.Timeout:
            print(colored(f"    [X] Timeout while connecting to {name}", "red"))
            if LOGGER:
                LOGGER.error(f"Timeout engine='{name}'")
            record_engine_result(knowledge, name, urllib.parse.urlparse(current_url).netloc, False)
            try:
                db_upsert_engine(name, urllib.parse.urlparse(current_url).netloc, fail_inc=1)
            except:
                pass
            new_host = adapt_engine(name, engine_config, proxies, knowledge)
            if new_host:
                current_url = swap_host_in_url(base_url, new_host)
                print(colored(f"    [+] Adaptation: using host {new_host} for {name}", "yellow"))
                if LOGGER:
                    LOGGER.info(f"Adaptation engine='{name}' host='{new_host}'")
                time.sleep(random.uniform(3, 6))
                continue
            break
        except requests.exceptions.ConnectionError:
            print(colored(f"    [X] Connection failed for {name} (might be offline)", "red"))
            if LOGGER:
                LOGGER.error(f"Connection failed engine='{name}'")
            record_engine_result(knowledge, name, urllib.parse.urlparse(current_url).netloc, False)
            try:
                db_upsert_engine(name, urllib.parse.urlparse(current_url).netloc, fail_inc=1)
            except:
                pass
            new_host = adapt_engine(name, engine_config, proxies, knowledge)
            if new_host:
                current_url = swap_host_in_url(base_url, new_host)
                print(colored(f"    [+] Adaptation: using host {new_host} for {name}", "yellow"))
                if LOGGER:
                    LOGGER.info(f"Adaptation engine='{name}' host='{new_host}'")
                time.sleep(random.uniform(3, 6))
                continue
            break
        except Exception as e:
            print(colored(f"    [X] Unexpected error on {name}: {e}", "red"))
            if LOGGER:
                LOGGER.exception(f"Unexpected error engine='{name}'")
            break
        
    return results

def enrich_results(results, proxies, max_fetch=ENRICH_FETCH_LIMIT):
    visited = set()
    fetched = 0
    futures = []
    def worker(r):
        url = r.get('URL')
        if not isinstance(url, str) or '.onion' not in url:
            return r, None
        if url in visited:
            return r, None
        if LOGGER:
            LOGGER.debug(f"Enriching url='{url}'")
        resp = fetch_url(url, proxies, timeout=45, retries=1)
        visited.add(url)
        return r, resp
    pool_size = min(8, max_fetch)
    with ThreadPoolExecutor(max_workers=pool_size) as ex:
        for r in results:
            if fetched >= max_fetch:
                break
            futures.append(ex.submit(worker, r))
            fetched += 1
        for fut in as_completed(futures):
            r, resp = fut.result()
            if resp and resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                title = soup.title.get_text(strip=True) if soup.title else ""
                meta = soup.find('meta', attrs={'name': 'description'})
                meta_desc = meta.get('content', '').strip() if meta and meta.get('content') else ""
                text_snippet = soup.get_text(separator=' ', strip=True)[:500]
                if not r.get('Title'):
                    r['Title'] = title if title else r.get('Title', '')
                if not r.get('Snippet'):
                    r['Snippet'] = meta_desc if meta_desc else text_snippet
                r['Status'] = '200'
                if LOGGER:
                    LOGGER.debug(f"Enrichment OK url='{r.get('URL')}'")
            else:
                r['Status'] = str(resp.status_code) if resp else 'error'
                if LOGGER:
                    LOGGER.warning(f"Enrichment failed url='{r.get('URL')}' status='{r['Status']}'")

def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("-q", "--query", dest="query", type=str, default=None)
    p.add_argument("-t", "--threads", dest="threads", type=int, default=5)
    p.add_argument("-o", "--output", dest="output", type=str, default=None)
    p.add_argument("-p", "--port", dest="port", type=int, default=None)
    p.add_argument("-D", "--discover", dest="discover", action="store_true", default=False)
    return p
def generate_summary(findings, output_path=None):
    df = pd.DataFrame(findings) if findings else pd.DataFrame()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = output_path or f"summary_{ts}.md"
    try:
        lines = []
        lines.append(f"# Tor OSINT Summary {ts}")
        if not df.empty:
            lines.append(f"- Total links: {len(df)}")
            if 'Search Engine' in df.columns:
                counts = df['Search Engine'].value_counts()
                for k, v in counts.items():
                    lines.append(f"- {k}: {v}")
        with open(name, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except:
        pass
def main():
    print(colored("=== Tor Multi-Engine OSINT Crawler ===", "magenta", attrs=['bold']))
    parser = build_parser()
    args = None
    try:
        args = parser.parse_args()
    except SystemExit:
        args = argparse.Namespace(query=None, threads=5, output=None, port=None)
    init_logger()
    if LOGGER:
        LOGGER.info("Scan start")
    init_db()
    
    # 1. Configurar Tor
    override_port = None
    if args and args.port:
        override_port = int(args.port)
    tor_port = override_port or get_tor_port()
    if not tor_port:
        print(colored("\n[CRITICAL] Tor was not detected (ports 9150/9050 closed).", "red"))
        if LOGGER:
            LOGGER.error("Tor not detected")
        
        if sys.platform.startswith('linux'):
            print(colored(">>> On Kali Linux, run: sudo service tor start", "yellow", attrs=['bold']))
        else:
            print(colored(">>> Start Tor Browser and keep it open before running this script.", "yellow", attrs=['bold']))
        if LOGGER:
            LOGGER.info("Stopping due to missing Tor")
        return

    print(colored(f"[INFO] Tor detected on port {tor_port}.", "green"))
    tor_proxy = f'socks5h://127.0.0.1:{tor_port}'
    proxies = {'http': tor_proxy, 'https': tor_proxy}
    if LOGGER:
        LOGGER.info(f"Tor detected port={tor_port}")

    if not check_tor_connection(proxies):
        print(colored("[WARN] Could not confirm Tor connection. Continuing anyway.", "yellow"))
        if LOGGER:
            LOGGER.warning("Tor verification failed; continuing with configured proxies")

    # 1.1 Optional: auto-discover new engines
    try:
        if args and getattr(args, "discover", False):
            print(colored("[INFO] Auto-discovering new engines...", "cyan"))
            if LOGGER:
                LOGGER.info("Engine discovery start")
            new_eps = discover_new_engines(proxies)
            if new_eps:
                added = 0
                for ep in new_eps:
                    if ep not in DEFAULT_SEARCH_ENGINES:
                        DEFAULT_SEARCH_ENGINES.append(ep)
                        added += 1
                print(colored(f"[INFO] Added {added} new endpoints to the aggregator.", "green"))
                if LOGGER:
                    LOGGER.info(f"Discovery added count={added}")
            else:
                print(colored("[INFO] No new valid engines found right now.", "yellow"))
                if LOGGER:
                    LOGGER.info("Discovery yielded no results")
    except Exception as e:
        if LOGGER:
            LOGGER.exception("Engine discovery failed")
 
    # 2. Get query
    if args and args.query:
        termo_input = args.query
        try:
            extra = get_top_keywords(termo_input, limit=5)
            if extra:
                termo_input = termo_input + " " + " ".join(extra)
        except:
            pass
        terms = [termo_input]
        print(colored(f"\n[INFO] Searching for: {termo_input}", "cyan"))
        if LOGGER:
            LOGGER.info(f"Query received via args='{termo_input}'")
    else:
        print(colored("\n--- MANUAL SEARCH MODE ---", "cyan", attrs=['bold']))
        termo_input = input(colored("Enter a search query (legal OSINT only): ", "yellow")).strip()
        
        if not termo_input:
            print(colored("[!] No query provided. Exiting.", "red"))
            if LOGGER:
                LOGGER.info("No query provided")
            return
        terms = [termo_input]
        if LOGGER:
            LOGGER.info(f"Query provided='{termo_input}'")

    all_findings = []

    # 3. Search loop
    for term in terms:
        print(colored(f"\n[*] Starting search for: {term}", "yellow"))
        if LOGGER:
            LOGGER.info(f"Search start term='{term}'")
        
        for engine_name, config in SEARCH_ENGINES.items():
            findings = search_engine(engine_name, config, str(term), proxies)
            all_findings.extend(findings)
            # Small delay to avoid hammering circuits and rate limits
            time.sleep(random.uniform(2, 5)) 
            if LOGGER:
                LOGGER.info(f"Engine finished='{engine_name}' total={len(all_findings)}")
        try:
            ext = aggregate_external_engines(str(term), proxies, max_workers=(args.threads if args else 5))
            all_findings.extend(ext)
            if LOGGER:
                LOGGER.info(f"External aggregator added count={len(ext)}")
        except:
            if LOGGER:
                LOGGER.warning("External aggregator failed")

    # 4. Report
    if all_findings:
        output_file = 'search_results.xlsx'
        try:
            target_fetch = ENRICH_FETCH_LIMIT if not args else max(1, args.threads)
            enrich_results(all_findings, proxies, target_fetch)
        except Exception as e:
            print(colored(f"[WARN] Enrichment failed: {e}", "yellow"))
            if LOGGER:
                LOGGER.exception("Enrichment failed")
        new_results = pd.DataFrame(all_findings)
        
        # Load existing results if present
        if os.path.exists(output_file):
            try:
                existing_df = pd.read_excel(output_file)
                existing_df = existing_df.rename(
                    columns={
                        "Data": "Date",
                        "Termo Pesquisado": "Search Term",
                        "Motor de Busca": "Search Engine",
                        "Contextos": "Contexts",
                        "Título": "Title",
                        "Titulo": "Title",
                    },
                )
                print(colored(f"[INFO] Merging with {len(existing_df)} previous results...", "cyan"))
                df_results = pd.concat([existing_df, new_results], ignore_index=True)
                if LOGGER:
                    LOGGER.info(f"Merged with previous results count={len(existing_df)}")
            except Exception as e:
                print(colored(f"[WARN] Could not read existing file (it will be overwritten): {e}", "yellow"))
                df_results = new_results
                if LOGGER:
                    LOGGER.warning("Failed to read existing file; overwriting")
        else:
            df_results = new_results
        
        # Deduplicate by URL so the same link does not repeat across runs
        df_results.drop_duplicates(subset=['URL'], keep='last', inplace=True)
        
        try:
            df_results.to_excel(output_file, index=False)
            print(colored(f"\n[SUCCESS] Report updated: {output_file}", "green", attrs=['bold']))
            print(f"Total unique links (all runs): {len(df_results)}")
            print(f"New links in this run: {len(new_results)}")
            generate_summary(all_findings, args.output if args else None)
            if LOGGER:
                LOGGER.info(f"Report saved='{output_file}' total={len(df_results)} new={len(new_results)}")
        except PermissionError:
            print(colored(f"\n[CRITICAL] Permission denied when saving '{output_file}'.", "red", attrs=['bold']))
            print(colored(">>> Close the Excel file if it is open and try again.", "yellow"))
            if LOGGER:
                LOGGER.error("Permission denied while saving report")
        except Exception as e:
            print(colored(f"\n[ERROR] Failed to save report: {e}", "red"))
            if LOGGER:
                LOGGER.exception("Failed to save report")
    else:
        print(colored("\n[INFO] No new results found on the queried engines.", "yellow"))
        if LOGGER:
            LOGGER.info("No new results")
    if LOGGER:
        LOGGER.info("Scan end")

if __name__ == "__main__":
    main()
