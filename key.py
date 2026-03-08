import requests
from datetime import datetime, timezone

PROXY_URL = "https://api.codetabs.com/v1/proxy?quest=https://colatv88xd.cc/api/matches"
OUTPUT_FILE = "uwir.php"

DONATE_URL = "https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php"
DONATE_TITLE = "😈 💖 Dukung Server → https://trakteer.id/mybhianesse0 💖 😈"
DONATE_GROUP = "😈 💖 DONASI SERVER 💖 😈"

FALLBACK_LOGO = "https://www.google.com/s2/favicons?sz=256&domain=google.com"

STREAM_HINTS = [".m3u8",".flv",".php",".ts","/live/","/stream/"]


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

    streams=[]

    if isinstance(obj,dict):

        for v in obj.values():

            if isinstance(v,str):

                if v.startswith("http") and any(h in v for h in STREAM_HINTS):
                    streams.append(v)

            elif isinstance(v,(dict,list)):
                streams+=extract_streams(v)

    elif isinstance(obj,list):

        for i in obj:
            streams+=extract_streams(i)

    return streams


def countdown(ts):

    try:

        start=datetime.fromtimestamp(int(ts),tz=timezone.utc)
        now=datetime.now(timezone.utc)

        diff=start-now

        if diff.total_seconds()<=0:
            return "LIVE 🔴"

        h=diff.seconds//3600
        m=(diff.seconds%3600)//60

        return f"{h:02d}h {m:02d}m"

    except:
        return "LIVE"


def format_time(ts):

    try:
        dt=datetime.fromtimestamp(int(ts),tz=timezone.utc)
        return dt.strftime("%A %d-%m-%Y %H:%M:%S")
    except:
        return ""


def fetch():

    r=requests.get(PROXY_URL,timeout=30)
    r.raise_for_status()

    return r.json()


def build():

    data=fetch()

    m3u=["#EXTM3U"]

    m3u.append(
        f'#EXTINF:-1 tvg-logo="{FALLBACK_LOGO}" group-title="{DONATE_GROUP}",{DONATE_TITLE}'
    )
    m3u.append(DONATE_URL)

    used=set()

    for e in data.values():

        if not isinstance(e,dict):
            continue

        home=search(e,[
            "homeTeamName","home_name","home","team_home","homeName"
        ])

        away=search(e,[
            "awayTeamName","away_name","away","team_away","awayName"
        ])

        league=search(e,[
            "competitionName","league","competition","tournament","leagueName"
        ])

        logo=search(e,[
            "competitionLogo","homeTeamLogo","awayTeamLogo","logo"
        ])

        start=search(e,[
            "matchTime","startTime","time","match_time","start"
        ])

        if not home:
            home="Team A"

        if not away:
            away="Team B"

        if not league:
            league="Football"

        if not logo:
            logo=FALLBACK_LOGO

        title=f"😈 {home} ⚔ {away} | {countdown(start)} 😈"

        group=f"😈 {league} | {format_time(start)} 😈"

        streams=extract_streams(e)

        for s in streams:

            if s in used:
                continue

            used.add(s)

            m3u.append(
                f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group}",{title}'
            )

            m3u.append(s)

    with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
        f.write("\n".join(m3u))


if __name__=="__main__":
    build()
