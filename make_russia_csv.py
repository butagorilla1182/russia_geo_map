import csv
from pathlib import Path
from datetime import datetime, timedelta, timezone

from skyfield.api import load, EarthSatellite, wgs84

tle_path = Path("geo.tle")
out_csv = Path("russia_geo.csv")
out_tle = Path("russia_clean.tle")

KEYWORDS = [
    "EXPRESS",
    "EKSPRESS",
    "YAMAL",
    "LUCH",
    "ELEKTRO",
    "BLAGOVEST",
    "OLYMP",
    "GORIZONT",
    "RADUGA",
    "EKRAN",
    "GARPUN",
]


def parse_tle_epoch(line1):
    # TLE 1行目 columns 19-32: YYDDD.DDDDDDDD
    raw = line1[18:32].strip()

    yy = int(raw[:2])
    day = float(raw[2:])

    # TLEの2桁年
    year = 2000 + yy if yy < 57 else 1900 + yy

    epoch_dt = (
        datetime(year, 1, 1, tzinfo=timezone.utc)
        + timedelta(days=day - 1)
    )

    return {
        "epoch_raw": raw,
        "epoch_day": f"{year}年{int(day):03d}日目",
        "epoch_utc": epoch_dt.strftime("%Y/%m/%d %H:%M:%S UTC"),
        "epoch_iso": epoch_dt.isoformat().replace("+00:00", "Z"),
    }


ts = load.timescale()
t = ts.now()

lines = [
    line.strip()
    for line in tle_path.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()
    if line.strip()
]

rows = []
tle_out = []

i = 0

while i < len(lines) - 2:
    name = lines[i]
    line1 = lines[i + 1]
    line2 = lines[i + 2]

    if line1.startswith("1 ") and line2.startswith("2 "):

        upper_name = name.upper()

        if any(k in upper_name for k in KEYWORDS):
            try:
                sat = EarthSatellite(
                    line1,
                    line2,
                    name,
                    ts
                )

                geocentric = sat.at(t)
                subpoint = wgs84.subpoint(geocentric)

                lat = subpoint.latitude.degrees
                lon = subpoint.longitude.degrees
                alt_km = subpoint.elevation.km
                norad = line1[2:7].strip()

                epoch = parse_tle_epoch(line1)

                rows.append({
                    "name": name,
                    "norad": norad,
                    "lat": round(lat, 4),
                    "lon": round(lon, 4),
                    "alt_km": round(alt_km, 1),

                    "epoch_raw": epoch["epoch_raw"],
                    "epoch_day": epoch["epoch_day"],
                    "epoch_utc": epoch["epoch_utc"],
                    "epoch_iso": epoch["epoch_iso"],
                })

                tle_out.extend([
                    name,
                    line1,
                    line2
                ])

            except Exception as e:
                print("skip", name, e)

        i += 3

    else:
        i += 1


rows.sort(
    key=lambda r: r["lon"]
)


with out_csv.open(
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "name",
            "norad",
            "lat",
            "lon",
            "alt_km",
            "epoch_raw",
            "epoch_day",
            "epoch_utc",
            "epoch_iso",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)


out_tle.write_text(
    "\n".join(tle_out) + "\n",
    encoding="utf-8"
)


print(
    "created",
    out_csv,
    "with",
    len(rows),
    "satellites"
)

for r in rows:
    print(
        r["name"],
        r["norad"],
        r["lon"],
        r["epoch_day"],
        r["epoch_utc"],
    )