import requests
from datetime import datetime, timezone

PROXY_URL = "https://api.codetabs.com/v1/proxy?quest=https://colatv88xd.cc/api/matches"
OUTPUT_FILE = "uwir.php"

DONATE_URL = "https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php"
DONATE_TITLE = "😈 💖 Dukung Server → https://trakteer.id/mybhianesse0 💖 😈"
DONATE_GROUP = "😈 💖 DONASI SERVER 💖 😈"

FALLBACK_LOGO = "https://www.google.com/s2/favicons?sz=256&domain=google.com"

STREAM_HINTS = [
    ".m3u8",
    ".flv",
    ".php",
    ".ts",
    "/stream/",
    "/live/",
]


def flag_emoji(code):
    try:
        return ''.join(chr(127397 + ord(c)) for c in code.upper())
    except:
        return ""


def format_time_full(ts):
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.strftime("%A %d-%m-%Y %H:%M:%S")
    except:
        return datetime.now().strftime("%A %d-%m-%Y %H:%M:%S")


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
    if not url.lower().startswith("http"):
        return False

    for hint in STREAM_HINTS:
        if hint in url.lower():
            return True

    return False


def extract_streams(obj):
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


def get_logo(event):

    for key in [
        "homeTeamLogo",
        "awayTeamLogo",
        "competitionLogo",
        "logo",
    ]:
        if key in event and event[key]:
            return event[key]

    return FALLBACK_LOGO


def fetch_and_save():

    r = requests.get(PROXY_URL, timeout=30)
    r.raise_for_status()

    data = r.json()

    m3u = ["#EXTM3U"]

    m3u.append(
        f'#EXTINF:-1 tvg-logo="{FALLBACK_LOGO}" group-title="{DONATE_GROUP}",{DONATE_TITLE}'
    )
    m3u.append(DONATE_URL)

    used = set()

    for key, e in data.items():

        if not isinstance(e, dict):
            continue

        home = e.get("homeTeamName", "Home")
        away = e.get("awayTeamName", "Away")

        home_country = e.get("homeTeamCountry", "")
        away_country = e.get("awayTeamCountry", "")

        league = e.get("competitionName", "Sports")

        start = e.get("matchTime")

        countdown = format_countdown(start)
        time_full = format_time_full(start)

        flag_home = flag_emoji(home_country)
        flag_away = flag_emoji(away_country)

        match_title = f"{flag_home} {home} ⚔ {away} {flag_away}"

        title_final = f"😈 {match_title} | {countdown} 😈"
        group_title = f"😈 {league} | {time_full} 😈"

        logo = get_logo(e)

        streams = extract_streams(e)

        for url in streams:

            if url in used:
                continue

            used.add(url)

            m3u.append(
                f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title}",{title_final}'
            )
            m3u.append(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))


if __name__ == "__main__":
    fetch_and_save()
