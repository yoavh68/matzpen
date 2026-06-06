# -*- coding: utf-8 -*-
"""
sources/iplan.py — תב"ע ממנהל התכנון (XPLAN / ArcGIS REST)

מטרה: לסכם יחידות דיור (יח"ד) בתוכניות לכל עיר -> tbaUnits.

⚠️ מודול זה הוא "ניחוש מושכל" עד שכלי האבחון (diagnose.py) יחשוף את שמות
   השדות האמיתיים בשכבת XPLAN. אחרי האבחון מעדכנים את FIELD_CITY / FIELD_UNITS
   / FIELD_STATUS למטה לשמות האמיתיים, וזה יתחיל להחזיר נתונים.
"""
import requests
import config

# שמות שדות משוערים — יעודכנו לפי diagnostics.md
FIELD_CITY   = "city_name"       # שדה שם הרשות/עיר
FIELD_UNITS  = "pq_authorised_quantity_120"  # שדה יחידות דיור (דוגמה)
FIELD_STATUS = "plan_status"     # שדה סטטוס התוכנית
STATUS_APPROVED_VALUES = ["מאושר", "אושרה", "תכנית מאושרת"]


def _num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def fetch_tba_by_city(city_names):
    """
    מחזיר {city_name: total_units}. שואב את כל התוכניות הרלוונטיות ומסכם יח"ד.
    כרגע best-effort; תלוי בשמות השדות האמיתיים (ראה אבחון).
    """
    if not config.ENABLE_IPLAN:
        return {}
    totals = {c: 0.0 for c in city_names}
    offset = 0
    try:
        while True:
            params = {
                "where": "1=1",
                "outFields": f"{FIELD_CITY},{FIELD_UNITS},{FIELD_STATUS}",
                "f": "json", "returnGeometry": "false",
                "resultOffset": offset, "resultRecordCount": 2000,
            }
            r = requests.get(config.IPLAN_XPLAN_QUERY, params=params,
                             headers=config.HTTP_HEADERS, timeout=config.HTTP_TIMEOUT)
            feats = r.json().get("features", [])
            if not feats:
                break
            for f in feats:
                a = f.get("attributes", {})
                city = str(a.get(FIELD_CITY, "")).strip()
                if city not in totals:
                    continue
                if config.TBA_PLAN_STATUS == "approved":
                    status = str(a.get(FIELD_STATUS, ""))
                    if not any(s in status for s in STATUS_APPROVED_VALUES):
                        continue
                totals[city] += _num(a.get(FIELD_UNITS))
            offset += len(feats)
            if len(feats) < 2000:
                break
    except Exception as e:
        print(f"[iplan] failed: {e}")
        return {}
    return {c: int(v) for c, v in totals.items() if v > 0}


if __name__ == "__main__":
    print(fetch_tba_by_city(["תל אביב-יפו", "ירושלים", "חיפה"]))
