import requests
from datetime import datetime, timezone

PROXY_URL = "https://api.codetabs.com/v1/proxy?quest=https://colatv88xd.cc/api/matches"
OUTPUT_FILE = "uwir.php"

DONATE_URL = "https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php"
DONATE_TITLE = "💖 Dukung Server → https://trakteer.id/mybhianesse0 💖"
DONATE_GROUP = "💖 DONASI SERVER 💖"
GOOGLE_LOGO = "https://www.google.com/s2/favicons?sz=256&domain=google.com"


STREAM_HINTS = [
    ".m3u8",
    ".flv",
    ".php",
    ".ts",
    "/stream/",
    "/live/",
]


def format_vs(home, away):
    return f"{home} ⚔ vs ⚔ {away}"


def format_countdown(ts):
    try:
        start = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        now = datetime.now(timezone.utc)

        diff = start - now

        if diff.total_seconds() <= 0:
            return "LIVE 🔴"

        h = diff.seconds // 3600
        m = (diff.seconds % 3600) // 60

        return f"Starts in {h:02d}h {m:02d}m"

    except:
        return "LIVE"


def is_stream(url):
    """cek apakah url kemungkinan stream"""
    u = url.lower()

    if not u.startswith("http"):
        return False

    for hint in STREAM_HINTS:
        if hint in u:
            return True

    return False


def extract_streams(obj):
    """scan semua struktur api untuk menemukan stream"""
    streams = []

    if isinstance(obj, dict):
        for v in obj.values():

            if isinstance(v, str) and is_stream(v):
                streams.append(v)

            elif isinstance(v, (dict, list)):
                streams.extend(extract_streams(v))

    elif isinstance(obj, list):
        for i in obj:
            streams.extend(extract_streams(i))

    return streams


def fetch_and_save():

    print("🔄 Fetching API")

    r = requests.get(PROXY_URL, timeout=30)
    r.raise_for_status()

    data = r.json()

    print("Total events:", len(data))

    m3u = ["#EXTM3U"]

    m3u.append(
        f'#EXTINF:-1 tvg-logo="{GOOGLE_LOGO}" group-title="{DONATE_GROUP}",{DONATE_TITLE}'
    )
    m3u.append(DONATE_URL)

    used = set()

    for key, e in data.items():

        if not isinstance(e, dict):
            continue

        home = e.get("homeTeamName", "Home")
        away = e.get("awayTeamName", "Away")

        league = e.get("competitionName", "Sports")

        start = e.get("matchTime")

        title = format_vs(home, away)
        countdown = format_countdown(start)

        title_final = f"😈 {title} | {countdown}"

        streams = extract_streams(e)

        for url in streams:

            if url in used:
                continue

            used.add(url)

            m3u.append(
                f'#EXTINF:-1 tvg-logo="{GOOGLE_LOGO}" group-title="{league}",{title_final}'
            )
            m3u.append(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    print("✅ Saved:", OUTPUT_FILE)
    print("📺 Total Streams:", len(used))


if __name__ == "__main__":
    fetch_and_save()
