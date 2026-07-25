import csv
import json


with open("russia_geo.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


markers = json.dumps(
    rows,
    ensure_ascii=False
)


parts = []

parts.append(
    '<html><head><meta charset="utf-8">'
    '<title>Russia GEO Map</title>'
)

parts.append(
    '<meta name="viewport" '
    'content="width=device-width, initial-scale=1.0">'
)

parts.append(
    '<link rel="stylesheet" '
    'href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">'
)

parts.append(
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
)


parts.append(
r'''
<style>

body {
    margin: 0;
    font-family: sans-serif;
}

.bar {
    padding: 12px;
    background: #f7f3ea;
}

.search-box {
    display: flex;
    gap: 7px;
    margin-top: 10px;
}

#satSearch {
    flex: 1;
    min-width: 0;
    padding: 10px;
    font-size: 16px;
    border: 1px solid #999;
    border-radius: 8px;
}

#searchButton {
    padding: 10px 15px;
    border: 0;
    border-radius: 8px;
    background: #2378d3;
    color: white;
    font-size: 15px;
    font-weight: bold;
}

#searchResult {
    min-height: 20px;
    margin-top: 6px;
    font-size: 13px;
}


/* 地図を広く */
#map {
    height: 82vh;
    width: 100%;
}


/* 詳細窓だけスクロール */
.leaflet-popup {
    max-width: 92vw;
}

.leaflet-popup-content-wrapper {
    max-width: 420px;
}

.leaflet-popup-content {
    max-height: 300px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
    margin: 12px 18px;
}

.leaflet-popup-content::-webkit-scrollbar {
    width: 5px;
}

.leaflet-popup-content::-webkit-scrollbar-thumb {
    background: #999;
    border-radius: 5px;
}

</style>
</head>
<body>
'''
)


parts.append(
    f'''
<div class="bar">

    <b>Russia GEO Map</b><br>

    CelesTrak GEO + GPZから抽出した
    ロシア・旧ソ連系GEO衛星<br>

    表示衛星数：{len(rows)} 機

    <div class="search-box">

        <input
            id="satSearch"
            type="text"
            placeholder="衛星名 または NORAD ID"
            autocomplete="off"
        >

        <button id="searchButton">
            🔍 検索
        </button>

    </div>

    <div id="searchResult"></div>

</div>
'''
)


parts.append(
    '<div id="map"></div>'
)

parts.append(
    '<script>'
)

parts.append(
    'const data = ' + markers + ';'
)


parts.append(
r'''

const map =
    L.map("map").setView(
        [0, 60],
        2
    );


L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 6,
        attribution: "OpenStreetMap"
    }
).addTo(map);



/* =========================================================
   発射場コード → 日本語
   ========================================================= */

const LAUNCH_SITES = {

    /* ロシア */
    "DLS":
        "ドンバロフスキー発射場",

    "KYMSC":
        "カプースチン・ヤール",

    "PLMSC":
        "プレセツク宇宙基地",

    "SVOBO":
        "スヴォボードヌイ宇宙基地",

    "VOSTO":
        "ボストーチヌイ宇宙基地",


    /* カザフスタン */
    "TYMSC":
        "バイコヌール宇宙基地",


    /* その他、ロシア衛星でも使用例あり */
    "FRGUI":
        "ギアナ宇宙センター",

    "SEAL":
        "シーローンチ海上発射施設",

    "SUBL":
        "潜水艦発射",

    "UNK":
        "不明"
};



function launchSiteName(code) {

    if (!code) {
        return "不明";
    }

    const key =
        String(code)
            .trim()
            .toUpperCase();

    const name =
        LAUNCH_SITES[key];

    if (name) {

        return (
            name +
            "（" +
            key +
            "）"
        );
    }

    /*
     * 未登録コードでも
     * 元の略号は残す
     */
    return key;
}



/* =========================================================
   衛星カテゴリ
   ========================================================= */

function catOf(r) {

    const n =
        String(
            r.name || ""
        ).toUpperCase();

    const lat =
        Math.abs(
            parseFloat(
                r.lat || "0"
            )
        );


    /* GEOから南北に大きく外れている */
    if (lat > 3) {

        return [
            "#dd6b20",
            "移動中・傾斜大",
            "GEO付近だが南北方向の変動が大きい衛星"
        ];
    }


    if (n.includes("LUCH")) {

        return [
            "#2b6cb0",
            "データ中継",
            "LUCH系データ中継衛星"
        ];
    }


    if (
        n.includes("EXPRESS") ||
        n.includes("EKSPRESS") ||
        n.includes("YAMAL")
    ) {

        return [
            "#c53030",
            "通信",
            "ロシア系通信衛星"
        ];
    }


    if (n.includes("ELEKTRO")) {

        return [
            "#2f855a",
            "気象・観測",
            "気象・地球観測系衛星"
        ];
    }


    if (
        n.includes("RADUGA") ||
        n.includes("GARPUN") ||
        n.includes("BLAGOVEST") ||
        n.includes("OLYMP")
    ) {

        return [
            "#6b46c1",
            "軍事・政府系通信",
            "軍事・政府系通信衛星"
        ];
    }


    if (
        n.includes("GORIZONT") ||
        n.includes("EKRAN")
    ) {

        return [
            "#718096",
            "旧世代通信",
            "旧ソ連・ロシアの旧世代通信衛星"
        ];
    }


    return [
        "#4a5568",
        "未整理",
        "用途未整理"
    ];
}



/* =========================================================
   打上げ日
   ========================================================= */

function formatLaunchDate(date) {

    if (!date) {
        return "不明";
    }

    return date.replaceAll(
        "-",
        "/"
    );
}



function launchAgeOf(date) {

    if (!date) {
        return "不明";
    }

    const launch =
        new Date(
            date +
            "T00:00:00Z"
        );


    if (
        Number.isNaN(
            launch.getTime()
        )
    ) {
        return "不明";
    }


    const diff =
        Date.now() -
        launch.getTime();


    if (diff < 0) {
        return "未打上げ";
    }


    const days =
        Math.floor(
            diff / 86400000
        );


    if (days < 365) {

        return (
            days +
            "日"
        );
    }


    const years =
        Math.floor(
            days / 365.2425
        );


    const remainDays =
        Math.floor(
            days -
            years * 365.2425
        );


    return (
        years +
        "年 " +
        remainDays +
        "日"
    );
}



/* =========================================================
   TLE経過時間
   ========================================================= */

function ageOf(epochIso) {

    const epoch =
        new Date(
            epochIso
        );


    if (
        Number.isNaN(
            epoch.getTime()
        )
    ) {
        return "不明";
    }


    let diff =
        Date.now() -
        epoch.getTime();


    const future =
        diff < 0;


    diff =
        Math.abs(diff);


    const totalMinutes =
        Math.floor(
            diff / 60000
        );


    const days =
        Math.floor(
            totalMinutes / 1440
        );


    const hours =
        Math.floor(
            (totalMinutes % 1440) / 60
        );


    const minutes =
        totalMinutes % 60;


    let text = "";


    if (days > 0) {

        text +=
            days +
            "日 ";
    }


    text +=
        hours +
        "時間" +
        minutes +
        "分";


    return future
        ? "未来 " + text
        : text;
}



/* =========================================================
   TLE鮮度
   ========================================================= */

function freshnessOf(epochIso) {

    const epoch =
        new Date(
            epochIso
        );


    if (
        Number.isNaN(
            epoch.getTime()
        )
    ) {

        return {
            color: "#718096",
            icon: "⚪",
            text: "不明"
        };
    }


    const ageHours =
        (
            Date.now() -
            epoch.getTime()
        ) / 3600000;


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



/* =========================================================
   ポップアップ
   ========================================================= */

function popOf(r) {

    const c =
        catOf(r);

    const fresh =
        freshnessOf(
            r.epoch_iso
        );


    return (

        "<b>" +
        r.name +
        "</b><br>" +


        "<span style='" +
        "display:inline-block;" +
        "margin:4px 0;" +
        "padding:2px 8px;" +
        "border-radius:10px;" +
        "background:" +
        c[0] +
        ";" +
        "color:white;" +
        "font-size:12px;" +
        "'>" +

        c[1] +

        "</span><br>" +


        "<b>NORAD ID：</b>" +
        r.norad +
        "<br>" +


        "<b>緯度：</b>" +
        r.lat +
        "°<br>" +


        "<b>経度：</b>" +
        r.lon +
        "°<br>" +


        "<b>高度：</b>" +
        r.alt_km +
        " km<br>" +


        "<hr>" +


        "🚀 <b>打上げ日：</b>" +

        formatLaunchDate(
            r.launch_date
        ) +

        "<br>" +


        "📍 <b>打上げ場所：</b>" +

        launchSiteName(
            r.launch_site
        ) +

        "<br>" +


        "🛰 <b>打上げから：</b>" +

        launchAgeOf(
            r.launch_date
        ) +

        "<br>" +


        "<hr>" +


        "<b>TLEエポック：</b>" +
        r.epoch_day +
        "<br>" +


        "<b>エポック日時：</b>" +
        r.epoch_utc +
        "<br>" +


        "<b>経過時間：</b>" +

        ageOf(
            r.epoch_iso
        ) +

        "<br>" +


        "<b>TLE鮮度：</b>" +

        "<span style='" +
        "font-weight:bold;" +
        "color:" +
        fresh.color +
        ";" +
        "'>" +

        fresh.icon +
        " " +
        fresh.text +

        "</span><br>" +


        "<hr>" +


        "<b>分類：</b>" +
        c[1] +
        "<br>" +


        "<b>任務メモ：</b>" +
        c[2]
    );
}



/* =========================================================
   マーカー生成
   ========================================================= */

const satelliteMarkers = [];


data.forEach(r => {

    const c =
        catOf(r);


    const marker =
        L.circleMarker(

            [
                parseFloat(
                    r.lat
                ),

                parseFloat(
                    r.lon
                )
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

        .bindPopup(
            popOf(r),
            {
                maxWidth: 420
            }
        );


    satelliteMarkers.push({

        data: r,
        marker: marker
    });
});



/* =========================================================
   検索文字列の正規化

   EXPRESS-AMU1
   express amu1
   ExpressAmu1

   全部同じ扱い
   ========================================================= */

function normalizeSearch(value) {

    return String(
        value || ""
    )

    .toUpperCase()

    .replace(
        /[^A-Z0-9]/g,
        ""
    );
}



/* =========================================================
   検索
   ========================================================= */

function searchSatellite() {

    const input =
        document.getElementById(
            "satSearch"
        );


    const result =
        document.getElementById(
            "searchResult"
        );


    const query =
        normalizeSearch(
            input.value.trim()
        );


    if (!query) {

        result.textContent =
            "衛星名かNORAD IDを入力してください";

        return;
    }


    /*
     * 完全一致
     */
    let found =
        satelliteMarkers.find(
            item => {

                const name =
                    normalizeSearch(
                        item.data.name
                    );

                const norad =
                    normalizeSearch(
                        item.data.norad
                    );

                return (
                    name === query ||
                    norad === query
                );
            }
        );


    /*
     * 部分一致
     */
    if (!found) {

        found =
            satelliteMarkers.find(
                item => {

                    const name =
                        normalizeSearch(
                            item.data.name
                        );

                    const norad =
                        normalizeSearch(
                            item.data.norad
                        );

                    return (
                        name.includes(query) ||
                        norad.includes(query)
                    );
                }
            );
    }


    if (!found) {

        result.textContent =
            "❌ 該当する衛星がありません";

        return;
    }


    const r =
        found.data;

    const marker =
        found.marker;


    map.setView(

        [
            parseFloat(
                r.lat
            ),

            parseFloat(
                r.lon
            )
        ],

        5,

        {
            animate: true
        }
    );


    marker.openPopup();


    /*
     * 検索したマーカーを
     * 一時的に大きくする
     */
    marker.setRadius(
        14
    );


    setTimeout(

        function() {

            marker.setRadius(
                8
            );
        },

        2500
    );


    result.textContent =
        "✅ " +
        r.name +
        " / NORAD " +
        r.norad;
}



/* 検索ボタン */

document
    .getElementById(
        "searchButton"
    )
    .addEventListener(
        "click",
        searchSatellite
    );



/* Enterでも検索 */

document
    .getElementById(
        "satSearch"
    )
    .addEventListener(

        "keydown",

        function(event) {

            if (
                event.key ===
                "Enter"
            ) {

                event.preventDefault();

                searchSatellite();
            }
        }
    );



/* =========================================================
   衛星カテゴリ
   ========================================================= */

const legend =
    L.control({
        position:
            "bottomleft"
    });


legend.onAdd =
    function() {

        const div =
            L.DomUtil.create(
                "div",
                "info legend"
            );


        div.id =
            "satLegend";


        div.style.background =
            "white";

        div.style.padding =
            "10px";

        div.style.borderRadius =
            "8px";

        div.style.boxShadow =
            "0 1px 5px rgba(0,0,0,0.3)";

        div.style.fontSize =
            "13px";


        div.innerHTML =

            "<b>衛星カテゴリ</b><br>" +

            "<div>🔵 データ中継</div>" +

            "<div>🔴 通信</div>" +

            "<div>🟢 気象・観測</div>" +

            "<div>🟣 軍事・政府系通信</div>" +

            "<div>⚫ 旧世代・未整理</div>" +

            "<div>🟠 移動中・傾斜大</div>";


        return div;
    };


legend.addTo(map);



/* =========================================================
   詳細表示中はカテゴリを消す
   ========================================================= */

map.on(
    "popupopen",

    function() {

        const legendBox =
            document.getElementById(
                "satLegend"
            );


        if (legendBox) {

            legendBox.style.display =
                "none";
        }
    }
);



/* 詳細を閉じたらカテゴリ復活 */

map.on(
    "popupclose",

    function() {

        const legendBox =
            document.getElementById(
                "satLegend"
            );


        if (legendBox) {

            legendBox.style.display =
                "block";
        }
    }
);

'''
)


parts.append(
    '</script></body></html>'
)


with open(
    "russia_map.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(parts)
    )


print(
    "saved russia_map.html"
)

print(
    f"count: {len(rows)}"
)