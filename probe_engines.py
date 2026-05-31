import requests
from termcolor import colored
import os
import socket

# Tor configuration

ENGINES = {
    'Ahmia': 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q=test',
    'Torch_V1': 'http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P=test',
    'Torch_V2': 'http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion/search?q=test',
    'Haystak': 'http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/?q=test',
    'OnionLand': 'http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search?q=test',
    'TorDex': 'http://tordexu73joywapk2txdr54jed4imqledpcvcuf75qsas2gwdgksvnyd.onion/search?q=test',
    'DarknetSearch': 'http://darkent74yfc3qe7vhd2ms53ynr3l5hbjz4on2x76e7odjiyrjlirvid.onion/search?q=test',
    'Tor66': 'http://tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion/search?q=test',
    'OnionRealm': 'http://orealmvxooetglfeguv2vp65a3rig2baq2ljc7jxxs4hsqsrcemkxcad.onion/search?query=test&action=search',
    'Excavator': 'http://2fd6cemt4gmccflhm6imvdfvli3nf7zn6rfrwpsy7uhxrgbypvwf5fad.onion/search?query=test',
    'TthSearch': 'http://tth4he7kdfmfwq2k7yaj2ggjdva7rdpbch42q6xgoorbabjeklyfbmyd.onion/search?query=test',
    'Labyrinth': 'http://labyrinthkh3uokhu2a5nwi4e6kedmbkxar3w6vgm2ipdb7ms3zdzlad.onion/search?query=test&lang=english&sort-by=relevant&tab=all',
    'DeepSearch': 'http://dgwq7uzh5ro2f7p34begy4kmxue5gst7lk2spxda63zkrpuegtj4opyd.onion/search.php?q=test'
}

def get_tor_port():
    ports = [9150, 9050]
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                print(colored(f"[INFO] Tor service detected on port {port}", "green"))
                return port
        except:
            pass
    return None

def probe():
    print("Starting engine probe (SOCKS5h)...")
    
    tor_port = get_tor_port()
    if not tor_port:
        print(colored("[CRITICAL] Could not detect Tor (ports 9150 or 9050 closed).", "red"))
        print(colored("Please start Tor Browser and wait until it connects.", "yellow"))
        return

    tor_proxy = f'socks5h://127.0.0.1:{tor_port}'
    
    if not os.path.exists('debug_html'):
        os.makedirs('debug_html')

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}
    
    proxies = {
        'http': tor_proxy,
        'https': tor_proxy
    }

    for name, url in ENGINES.items():
        print(f"Testing {name}...")
        try:
            # Increased timeout because Tor can be slow
            r = requests.get(url, headers=headers, proxies=proxies, timeout=60)
            if r.status_code == 200:
                print(colored(f"  [OK] {name} responded. Saving HTML...", "green"))
                with open(f'debug_html/{name}.html', 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(r.text)
            else:
                print(colored(f"  [FAIL] {name} returned status {r.status_code}", "red"))
        except Exception as e:
            print(colored(f"  [ERROR] {name} unreachable: {e}", "red"))

if __name__ == "__main__":
    probe()
