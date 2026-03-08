import requests
from datetime import datetime, timezone

PROXY_URL = "https://api.codetabs.com/v1/proxy?quest=https://colatv88xd.cc/api/matches"
OUTPUT_FILE = "uwir.php"

DONATE_URL = "https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php"
DONATE_TITLE = "💖 Dukung Server Dengan Donasi → https://trakteer.id/mybhianesse0 💖"
DONATE_GROUP = "💖 DONASI SERVER 💖"
GOOGLE_LOGO = "https://www.google.com/s2/favicons?sz=256&domain=google.com"


def format_countdown(start_time):
    try:
        start = datetime.fromtimestamp(int(start_time), tz=timezone.utc)
        now = datetime.now(timezone.utc)

        diff = start - now

        if diff.total_seconds() <= 0:
            return "LIVE 🔴"

        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60

        return f"Starts in {hours:02d}h {minutes:02d}m {seconds:02d}s"

    except:
        return "LIVE"


def format_vs(title):
    return (
        title.replace(" vs ", " ⚔ vs ⚔ ")
        .replace(" VS ", " ⚔ vs ⚔ ")
        .replace(" Vs ", " ⚔ vs ⚔ ")
    )


def fetch_and_save():

    print("🔄 Fetching data from proxy...")

    r = requests.get(PROXY_URL, timeout=30)
    r.raise_for_status()

    data = r.json()

    # auto detect event list
    if isinstance(data, dict):
        if "data" in data:
            events = data["data"]
        elif "matches" in data:
            events = data["matches"]
        else:
            events = list(data.values())
    else:
        events = data

    print(f"✅ Got {len(events)} events")

    now = datetime.utcnow()
    time_string = now.strftime("%H:%M:%S %A %d %B %Y")

    m3u = ["#EXTM3U"]

    # ======================
    # DONASI CHANNEL PALING ATAS
    # ======================

    m3u.append(
        f'#EXTINF:-1 tvg-name="{DONATE_TITLE}" tvg-logo="{GOOGLE_LOGO}" group-title="{DONATE_GROUP}",{DONATE_TITLE}'
    )
    m3u.append(DONATE_URL)

    used_urls = set()

    for event in events:

        if not isinstance(event, dict):
            continue

        title = event.get("title") or event.get("name") or "Live Event"
        title = format_vs(title)

        league = (
            event.get("league")
            or event.get("league_name")
            or event.get("competition")
            or "Sports"
        )

        start_time = (
            event.get("start")
            or event.get("start_time")
            or event.get("time")
        )

        countdown = format_countdown(start_time)

        streams = event.get("streams") or event.get("sources") or []

        title_final = f"😈 {title} | {countdown} 😈"
        group_name = f"😈 {league} {time_string} 😈"

        for stream in streams:

            if isinstance(stream, str):
                url = stream
            else:
                url = stream.get("url") or stream.get("link")

            if not url:
                continue

            if url in used_urls:
                continue

            used_urls.add(url)

            m3u.append(
                f'#EXTINF:-1 tvg-name="{title_final}" tvg-logo="{GOOGLE_LOGO}" group-title="{group_name}",{title_final}'
            )
            m3u.append(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    print(f"💾 Saved playlist → {OUTPUT_FILE}")
    print(f"📺 Unique streams: {len(used_urls)}")


if __name__ == "__main__":
    fetch_and_save()
