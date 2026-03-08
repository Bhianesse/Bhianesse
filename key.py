import requests

PROXY_URL = "https://api.codetabs.com/v1/proxy?quest=https://colatv88xd.cc/api/matches"
OUTPUT_FILE = "uwir.php"

DONATE_URL = "https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php"
DONATE_TITLE = "💖 Dukung Server → https://trakteer.id/mybhianesse0 💖"
DONATE_GROUP = "💖 DONASI SERVER 💖"
GOOGLE_LOGO = "https://www.google.com/s2/favicons?sz=256&domain=google.com"


def fetch_and_save():

    print("Fetching API...")

    r = requests.get(PROXY_URL, timeout=30)
    r.raise_for_status()

    data = r.json()

    # pastikan events list
    if isinstance(data, list):
        events = data
    elif isinstance(data, dict):
        events = data.get("data") or data.get("matches") or []
    else:
        events = []

    print("Events:", len(events))

    m3u = ["#EXTM3U"]

    # channel donasi
    m3u.append(
        f'#EXTINF:-1 tvg-logo="{GOOGLE_LOGO}" group-title="{DONATE_GROUP}",{DONATE_TITLE}'
    )
    m3u.append(DONATE_URL)

    used = set()

    for event in events:

        # skip jika bukan dictionary
        if not isinstance(event, dict):
            continue

        title = event.get("title") or event.get("name") or "Live Event"
        league = event.get("league") or event.get("category") or "Sports"

        sources = event.get("sources") or event.get("streams") or []

        # jika sources string
        if isinstance(sources, str):
            sources = [sources]

        if not isinstance(sources, list):
            continue

        for s in sources:

            url = None

            # jika string langsung url
            if isinstance(s, str):
                url = s

            # jika dictionary
            elif isinstance(s, dict):

                if "url" in s:
                    url = s["url"]

                elif "link" in s:
                    url = s["link"]

                else:
                    sid = s.get("id")
                    src = s.get("source")

                    if sid and src:
                        url = f"https://video-home.colatv88xd.cc/{src}/{sid}/playlist.m3u8"

            if not url:
                continue

            if url in used:
                continue

            used.add(url)

            m3u.append(
                f'#EXTINF:-1 tvg-logo="{GOOGLE_LOGO}" group-title="{league}",{title}'
            )
            m3u.append(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

    print("Channels:", len(used))


if __name__ == "__main__":
    fetch_and_save()
