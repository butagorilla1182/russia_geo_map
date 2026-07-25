import csv
import json

rows = list(
    csv.DictReader(
        open("russia_geo.csv", encoding="utf-8")
    )
)

markers = json.dumps(
    rows,
    ensure_ascii=False
)

parts = []

parts.append(
    '<html><head><meta charset="utf-8"><title>Russia GEO Map</title>'
)

parts.append(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
)

parts.append(
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
)

parts.append(
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
)

parts.append(
    '<style>'
    'body{margin:0;font-family:sans-serif}'
    '.bar{padding:12px;background:#f7f3ea}'
    '#map{height:78vh;width:100vw}'
    '</style></head><body>'
)

parts.append(
    f'<div class="bar">'
    f'<b>Russia GEO Map</b><br>'
    f'CelesTrak GEO TLEから抽出したRussia GEOの地図表示<br>'
    f'表示衛星数：{len(rows)} 機'
    f'</div>'
)

parts.append('<div id="map"></div>')
parts.append('<script>')

parts.append(
    'const data = ' + markers + ';'
)

parts.append(
    'const map = L.map("map").setView([0,140],2);'
)

parts.append(
    'L.tileLayer('
    '"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",'
    '{maxZoom:6, attribution:"OpenStreetMap"}'
    ').addTo(map);'
)

parts.append(
'''
function catOf(r) {

    const n = String(r.name || "").toUpperCase();

    if (n.includes("LUCH"))
        return [
            "#2b6cb0",
            "データ中継",
            "ISS・低軌道衛星・宇宙機との通信中継系"
        ];

    if (
        n.includes("EXPRESS") ||
        n.includes("EKSPRESS") ||
        n.includes("YAMAL")
    )
        return [
            "#3182ce",
            "通信",
            "ロシア系の静止通信衛星"
        ];

    if (n.includes("ELEKTRO"))
        return [
            "#2f855a",
            "気象・観測",
            "静止気象・地球観測系"
        ];

    if (
        n.includes("RADUGA") ||
        n.includes("GARPUN")
    )
        return [
            "#c53030",
            "軍事通信",
            "軍事通信・政府通信系の可能性"
        ];

    return [
        "#718096",
        "未整理",
        "用途未整理。公開情報または自分メモで追記"
    ];
}


function ageOf(epochIso) {

    const epoch = new Date(epochIso);

    if (Number.isNaN(epoch.getTime())) {
        return "不明";
    }

    let diff = Date.now() - epoch.getTime();
    const future = diff < 0;

    diff = Math.abs(diff);

    const totalMinutes =
        Math.floor(diff / 60000);

    const days =
        Math.floor(totalMinutes / 1440);

    const hours =
        Math.floor((totalMinutes % 1440) / 60);

    const minutes =
        totalMinutes % 60;

    let text = "";

    if (days > 0) {
        text += days + "日 ";
    }

    text += hours + "時間" + minutes + "分";

    return future ? "未来 " + text : text;
}


function freshnessOf(epochIso) {

    const epoch = new Date(epochIso);

    if (Number.isNaN(epoch.getTime())) {
        return {
            color: "#718096",
            icon: "⚪",
            text: "不明"
        };
    }

    const ageHours =
        (Date.now() - epoch.getTime()) / 3600000;

    if (ageHours < 24) {
        return {
            color: "#16a34a",
            icon: "🟢",
            text: "新鮮"
        };
    }

    if (ageHours < 72) {
        return {
            color: "#ca8a04",
            icon: "🟡",
            text: "やや古い"
        };
    }

    if (ageHours < 168) {
        return {
            color: "#ea580c",
            icon: "🟠",
            text: "古い"
        };
    }

    return {
        color: "#dc2626",
        icon: "🔴",
        text: "要注意"
    };
}


function popOf(r) {

    const c = catOf(r);
    const fresh = freshnessOf(r.epoch_iso);

    return (
        "<b>" + r.name + "</b><br>" +

        "<span style='" +
        "display:inline-block;" +
        "margin:4px 0;" +
        "padding:2px 8px;" +
        "border-radius:10px;" +
        "background:" + c[0] + ";" +
        "color:white;" +
        "font-size:12px;" +
        "'>" +
        c[1] +
        "</span><br>" +

        "<b>NORAD ID：</b>" +
        r.norad + "<br>" +

        "<b>緯度：</b>" +
        r.lat + "°<br>" +

        "<b>経度：</b>" +
        r.lon + "°<br>" +

        "<b>高度：</b>" +
        r.alt_km + " km<br>" +

        "<hr>" +

        "<b>TLEエポック：</b>" +
        r.epoch_day + "<br>" +

        "<b>エポック日時：</b>" +
        r.epoch_utc + "<br>" +

        "<b>経過時間：</b>" +
        ageOf(r.epoch_iso) + "<br>" +

        "<b>TLE鮮度：</b>" +
        "<span style='" +
        "font-weight:bold;" +
        "color:" + fresh.color + ";" +
        "'>" +
        fresh.icon + " " +
        fresh.text +
        "</span><br>" +

        "<hr>" +

        "<b>国：</b>ロシア<br>" +

        "<b>分類：</b>" +
        c[1] + "<br>" +

        "<b>任務メモ：</b>" +
        c[2]
    );
}


data.forEach(r => {

    const c = catOf(r);

    L.circleMarker(
        [
            parseFloat(r.lat),
            parseFloat(r.lon)
        ],
        {
            radius: 8,
            color: "#1a202c",
            weight: 1,
            fillColor: c[0],
            fillOpacity: 0.9
        }
    )
    .addTo(map)
    .bindPopup(popOf(r));
});


const legend =
    L.control({
        position: "bottomleft"
    });


legend.onAdd = function() {

    const div =
        L.DomUtil.create(
            "div",
            "info legend"
        );

    div.style.background = "white";
    div.style.padding = "10px";
    div.style.borderRadius = "8px";
    div.style.boxShadow =
        "0 1px 5px rgba(0,0,0,0.3)";
    div.style.fontSize = "13px";

    div.innerHTML =
        "<b>衛星カテゴリ</b><br>" +
        "<div>🔵 データ中継</div>" +
        "<div>🔷 通信</div>" +
        "<div>🔴 軍事通信</div>" +
        "<div>🟢 気象・観測</div>" +
        "<div>⚫ 未整理</div>";

    return div;
};


legend.addTo(map);
'''
)

parts.append('</script></body></html>')

open(
    "russia_map.html",
    "w",
    encoding="utf-8"
).write(
    "\n".join(parts)
)

print("saved russia_map.html")
print(f"count: {len(rows)}")