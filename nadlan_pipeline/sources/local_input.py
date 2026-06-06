# -*- coding: utf-8 -*-
"""
sources/local_input.py - קליטת נתונים רשמיים שמעדכנים ידנית מקובץ.

הרעיון: במקום סקרייפר שביר, מורידים את האקסל הרשמי מרשות המסים (nadlan.gov.il)
ומעדכנים קובץ אחד פשוט. הצינור קורא אותו ומזין את השדות - נתונים אמיתיים,
בלי scraping ובלי סיכון משפטי.

הקובץ: nadlan_pipeline/input/market_data.csv
עמודות: city,price24,price18,unsold24,rent2025
שדה ריק = לא נוגעים בו (נשאר הקיים).

אם הקובץ לא קיים - נוצר אוטומטית מה-seed (מלא מראש בערכים הנוכחיים),
כך שצריך רק לעדכן מספרים, לא להקליד מאפס.
"""
import csv
import os
import config

INPUT_DIR = os.path.join(config.ROOT, "input")
MARKET_CSV = os.path.join(INPUT_DIR, "market_data.csv")
FIELDS = ["price24", "price18", "unsold24", "rent2025"]
RELIABILITY = "high"   # מקור רשמי (רשות המסים) = אמינות גבוהה


def _num(v):
    try:
        return int(float(str(v).replace(",", "").strip()))
    except (TypeError, ValueError):
        return None


def ensure_template(cities):
    """יוצר את market_data.csv מה-seed אם אינו קיים (מלא מראש)."""
    if os.path.exists(MARKET_CSV):
        return False
    os.makedirs(INPUT_DIR, exist_ok=True)
    with open(MARKET_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city"] + FIELDS)
        for c in cities:
            w.writerow([c["n"]] + [c.get(fld, "") for fld in FIELDS])
    return True


def read_market_data():
    """קורא את הקובץ ומחזיר {city: {field: (value, reliability)}}."""
    out = {}
    if not os.path.exists(MARKET_CSV):
        return out
    with open(MARKET_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            city = (row.get("city") or "").strip()
            if not city:
                continue
            upd = {}
            for fld in FIELDS:
                val = _num(row.get(fld))
                if val is not None:
                    upd[fld] = (val, RELIABILITY)
            if upd:
                out[city] = upd
    return out


if __name__ == "__main__":
    import json
    cities = json.load(open(config.SEED_JSON, encoding="utf-8"))
    created = ensure_template(cities)
    print("template created" if created else "template exists")
    print("rows read:", len(read_market_data()))
