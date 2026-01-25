import json
import os
import mysql.connector
from decimal import Decimal


MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "statsbb_user"
MYSQL_PASSWORD = "Statsbb!2026"
MYSQL_DB = "statsbb"

OUT_DIR = os.path.join(os.path.dirname(__file__), "site", "data")
os.makedirs(OUT_DIR, exist_ok=True)

def dump_json(filename, obj):
    path = os.path.join(OUT_DIR, filename)

    def json_default(x):
        if isinstance(x, Decimal):
            return float(x)
        return str(x)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, default=json_default)


def main():
    cnx = mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    cur = cnx.cursor(dictionary=True)

    # 1) players
    cur.execute("""
        SELECT player_id, full_name, slug, birth_date
        FROM players
        ORDER BY full_name
    """)
    players = cur.fetchall()
    # birth_date JSON-friendly
    for p in players:
        if p["birth_date"] is not None:
            p["birth_date"] = str(p["birth_date"])
    dump_json("players.json", players)

    # 2) stats_regular
    cur.execute("""
    SELECT
        p.slug,
        s.season_name,
        d.division_name,

        r.gp,
        r.pts,
        ROUND(r.pts / NULLIF(r.gp, 0), 1) AS ppg,

        r.reb,
        ROUND(r.reb / NULLIF(r.gp, 0), 1) AS rpg,

        r.ast,
        ROUND(r.ast / NULLIF(r.gp, 0), 1) AS apg,

        r.stl,
        ROUND(r.stl / NULLIF(r.gp, 0), 1) AS spg,

        r.blk,
        ROUND(r.blk / NULLIF(r.gp, 0), 1) AS bpg,

        r.min,
        r.twopm, r.twopa,
        r.threepm, r.threepa,
        r.ftm, r.fta,
        r.to, r.fls
    FROM stats_regular r
    JOIN players p ON p.player_id = r.player_id
    JOIN seasons s ON s.season_id = r.season_id
    LEFT JOIN divisions d ON d.division_id = r.division_id
    ORDER BY p.slug, s.season_id DESC
""")

    stats_regular = cur.fetchall()
    dump_json("stats_regular.json", stats_regular)

    # 3) stats_playoffs
    cur.execute("""
        SELECT
          p.slug,
          s.season_name,
          d.division_name,
          po.gp, po.pts, po.min,
          po.twopm, po.twopa, po.threepm, po.threepa,
          po.ftm, po.fta, po.reb, po.ast, po.stl, po.`to`, po.blk, po.fls
        FROM stats_playoffs po
        JOIN players p ON p.player_id = po.player_id
        JOIN seasons s ON s.season_id = po.season_id
        LEFT JOIN divisions d ON d.division_id = po.division_id
        ORDER BY p.slug, s.season_id DESC
    """)
    stats_playoffs = cur.fetchall()
    dump_json("stats_playoffs.json", stats_playoffs)

    cur.close()
    cnx.close()
    print("🎉 export done")

if __name__ == "__main__":
    main()
