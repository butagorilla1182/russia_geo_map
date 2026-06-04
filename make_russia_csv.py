import csv
from pathlib import Path
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

ts = load.timescale()
t = ts.now()

lines = [line.strip() for line in tle_path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]

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
                sat = EarthSatellite(line1, line2, name, ts)
                geocentric = sat.at(t)
                subpoint = wgs84.subpoint(geocentric)
                lat = subpoint.latitude.degrees
                lon = subpoint.longitude.degrees
                alt_km = subpoint.elevation.km
                norad = line1[2:7].strip()

                rows.append({
                    "name": name,
                    "norad": norad,
                    "lat": round(lat, 4),
                    "lon": round(lon, 4),
                    "alt_km": round(alt_km, 1),
                })
                tle_out.extend([name, line1, line2])
            except Exception as e:
                print("skip", name, e)
        i += 3
    else:
        i += 1

rows.sort(key=lambda r: r["lon"])

with out_csv.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "norad", "lat", "lon", "alt_km"])
    writer.writeheader()
    writer.writerows(rows)

out_tle.write_text("\n".join(tle_out) + "\n", encoding="utf-8")

print("created", out_csv, "with", len(rows), "satellites")
for r in rows:
    print(r["name"], r["norad"], r["lon"])
