import re,json,sys,os,datetime as dt
"""S keys may be day numbers (YEAR/MONTH args apply) or "YYYY-MM-DD" strings.
Build per-showing .ics files and one subscribable feed from the F and S data in fox/index.html.
Usage: python3 tools/make_ics.py fox/index.html fox/ics fox/fox.ics YEAR MONTH [fox|tiff]
For tiff, each F entry carries its own ticket URL at index 7."""
html,outdir,feed,year,month=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5])
VENUES={"fox":dict(name="the Fox",loc="Fox Theatre, 2236 Queen St E, Toronto, ON M4E 1G2",cal="Fox Theatre screenings",prod="Fox Theatre Calendar",uid="fox-calendar"),
        "tiff":dict(name="TIFF Lightbox",loc="TIFF Lightbox, 350 King St W, Toronto, ON M5V 3X5",cal="TIFF Lightbox screenings",prod="TIFF Lightbox Calendar",uid="tiff-calendar")}
V=VENUES[sys.argv[6] if len(sys.argv)>6 else "fox"]
link=lambda slug,f:(f[7] if len(f)>7 and f[7] else "https://www.foxtheatre.ca/movies/"+slug+"/")
h=open(html,encoding="utf8").read()
F=json.loads(re.search(r'const F=(\{.*?\n\});',h,re.S).group(1))
S=json.loads(re.search(r'const S=(\{.*?\n\});',h,re.S).group(1))
os.makedirs(outdir,exist_ok=True)
for f in os.listdir(outdir): os.remove(os.path.join(outdir,f))
TZ="""BEGIN:VTIMEZONE\r\nTZID:America/Toronto\r\nBEGIN:STANDARD\r\nDTSTART:19701101T020000\r\nRRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\r\nTZOFFSETFROM:-0400\r\nTZOFFSETTO:-0500\r\nTZNAME:EST\r\nEND:STANDARD\r\nBEGIN:DAYLIGHT\r\nDTSTART:19700308T020000\r\nRRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\r\nTZOFFSETFROM:-0500\r\nTZOFFSETTO:-0400\r\nTZNAME:EDT\r\nEND:DAYLIGHT\r\nEND:VTIMEZONE\r\n"""
esc=lambda s:s.replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
def fold(line):
    b=line.encode("utf8"); parts=[]
    while len(b)>73:
        cut=73
        while (b[cut]&0xC0)==0x80: cut-=1
        parts.append(b[:cut]); b=b[cut:]
    parts.append(b); return "\r\n ".join(p.decode("utf8") for p in parts)
stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); n=0
events=[]
for day,arr in S.items():
    for x in arr:
        t,slug=x.split(" ")[:2]; f=F[slug]
        hh,mm=map(int,t.split(":")); start=(dt.datetime.strptime(day,"%Y-%m-%d").replace(hour=hh,minute=mm) if "-" in day else dt.datetime(year,month,int(day),hh,mm))
        end=start+dt.timedelta(minutes=f[2] or 120)
        desc=[]
        if len(f)>5 and f[5]: desc.append("Directed by "+f[5])
        meta=" · ".join(str(v) for v in [f[1], f"{f[2]} min" if f[2] else None] if v)
        if meta: desc.append(meta)
        if len(f)>6 and f[6]: desc.append(f[6])
        if f[4]: desc.append(f[4])
        desc.append("Tickets: "+link(slug,f))
        name=f"{start:%Y%m%d-%H%M}-{slug}.ics"
        lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//"+V["prod"]+"//EN","CALSCALE:GREGORIAN","METHOD:PUBLISH"]
        body="\r\n".join(lines)+"\r\n"+TZ
        ev=["BEGIN:VEVENT",f"UID:{start:%Y%m%dT%H%M}-{slug}@"+V["uid"],f"DTSTAMP:{stamp}",
            f"DTSTART;TZID=America/Toronto:{start:%Y%m%dT%H%M%S}",f"DTEND;TZID=America/Toronto:{end:%Y%m%dT%H%M%S}",
            "SUMMARY:"+esc(f[0]+" at "+V["name"]),"LOCATION:"+esc(V["loc"]),
            "DESCRIPTION:"+esc("\n".join(desc)),"URL:"+link(slug,f),"END:VEVENT","END:VCALENDAR"]
        evtxt="\r\n".join(fold(l) for l in ev[:-1])+"\r\n"; events.append(evtxt)
        body+=evtxt+"END:VCALENDAR\r\n"
        open(os.path.join(outdir,name),"w",encoding="utf8",newline="").write(body); n+=1
hdr="BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//"+V["prod"]+"//EN\r\nCALSCALE:GREGORIAN\r\nMETHOD:PUBLISH\r\nX-WR-CALNAME:"+V["cal"]+"\r\nX-WR-TIMEZONE:America/Toronto\r\nREFRESH-INTERVAL;VALUE=DURATION:P1D\r\nX-PUBLISHED-TTL:P1D\r\n"
open(feed,"w",encoding="utf8",newline="").write(hdr+TZ+"".join(events)+"END:VCALENDAR\r\n")
print(n)
