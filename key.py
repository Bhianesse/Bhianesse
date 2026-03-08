import requests
from datetime import datetime, timezone, timedelta

PROXY_URL = "https://api.codetabs.com/v1/proxy?quest=https://colatv88xd.cc/api/matches"
OUTPUT_FILE = "uwir.php"

DONATE_URL = "https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php"
DONATE_TITLE = "😈 💖 Dukung Server → https://trakteer.id/mybhianesse0 💖 😈"
DONATE_GROUP = "😈 DONASI SERVER 😈"

FALLBACK_LOGO = "https://www.google.com/s2/favicons?sz=256&domain=google.com"

WIB = timezone(timedelta(hours=7))


def log(msg):
    print(f"[LOG] {msg}")


def search(obj, keys):

    if isinstance(obj, dict):

        for k in keys:
            if k in obj and obj[k]:
                return obj[k]

        for v in obj.values():
            r = search(v, keys)
            if r:
                return r

    elif isinstance(obj, list):

        for i in obj:
            r = search(i, keys)
            if r:
                return r

    return None


def extract_streams(obj):

    streams = []

    image_ext = (
        ".png", ".jpg", ".jpeg", ".webp",
        ".gif", ".svg", ".ico"
    )

    if isinstance(obj, dict):

        for v in obj.values():

            if isinstance(v, str):

                if (
                    v.startswith("http")
                    and not v.lower().endswith(image_ext)
                ):
                    streams.append(v)

            elif isinstance(v, (dict, list)):
                streams += extract_streams(v)

    elif isinstance(obj, list):

        for i in obj:
            streams += extract_streams(i)

    return streams


def flag_emoji(code):

    try:
        return ''.join(chr(127397 + ord(c)) for c in code.upper())
    except:
        return ""


def countdown(ts):

    try:

        start = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        now = datetime.now(timezone.utc)

        diff = start - now

        if diff.total_seconds() <= 0:
            return "LIVE 🔴"

        total = int(diff.total_seconds())

        h = total // 3600
        m = (total % 3600) // 60

        return f"{h}h {m}m"

    except:
        return ""


def kickoff_wib(ts):

    try:

        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        dt = dt.astimezone(WIB)

        return dt.strftime("%H:%M WIB")

    except:
        return ""


def date_wib(ts):

    try:

        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        dt = dt.astimezone(WIB)

        return dt.strftime("%d %b")

    except:
        return ""


def stream_quality(url):

    url = url.lower()

    if "1080" in url:
        return "1080p"

    if "720" in url:
        return "720p"

    if "480" in url:
        return "480p"

    if "360" in url:
        return "360p"

    return ""


def fetch():

    log("Fetching match data...")

    r = requests.get(PROXY_URL, timeout=30)
    r.raise_for_status()

    data = r.json()

    log(f"API fetched: {len(data)} entries")

    return data


def build():

    data = fetch()

    log("Building playlist...")

    m3u = ["#EXTM3U"]

    m3u.append(
        f'#EXTINF:-1 tvg-logo="{FALLBACK_LOGO}" group-title="{DONATE_GROUP}",{DONATE_TITLE}'
    )
    m3u.append(DONATE_URL)

    used = set()

    match_count = 0
    stream_count = 0

    for e in data.values():

        if not isinstance(e, dict):
            continue

        match_count += 1

        home = search(e,[
            "homeTeamName","home_name","home","team_home","homeName"
        ])

        away = search(e,[
            "awayTeamName","away_name","away","team_away","awayName"
        ])

        league = search(e,[
            "competitionName","league","competition","tournament","leagueName"
        ])

        logo = search(e,[
            "competitionLogo",
            "leagueLogo",
            "homeTeamLogo",
            "awayTeamLogo",
            "logo"
        ])

        home_country = search(e,[
            "homeTeamCountry","home_country"
        ])

        away_country = search(e,[
            "awayTeamCountry","away_country"
        ])

        start = search(e,[
            "matchTime","startTime","time","match_time","start"
        ])

        if not home:
            home = "Team A"

        if not away:
            away = "Team B"

        if not league:
            league = "Football"

        if not logo:
            logo = FALLBACK_LOGO

        flag_home = flag_emoji(home_country) if home_country else ""
        flag_away = flag_emoji(away_country) if away_country else ""

        match_title = f"{flag_home} {home} ⚔ {away} {flag_away}"

        live_tag = countdown(start)

        kickoff = kickoff_wib(start)

        title = f"😈 {match_title} | {kickoff} | {live_tag} 😈"

        group = f"😈 {league} | {date_wib(start)} 😈"

        streams = extract_streams(e)

        for s in streams:

            if s in used:
                continue

            used.add(s)
            stream_count += 1

            quality = stream_quality(s)

            name = title

            if quality:
                name += f" | {quality}"

            m3u.append(
                f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{name}'
            )

            m3u.append(s)

    log(f"Matches processed: {match_count}")
    log(f"Streams added: {stream_count}")

    log("Writing playlist...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    log("Playlist completed.")


if __name__ == "__main__":
    build()
