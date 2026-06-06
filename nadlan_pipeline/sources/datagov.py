# -*- coding: utf-8 -*-
"""
sources/datagov.py — חיבור ל-data.gov.il (CKAN API)

הפורטל הממשלתי הפתוח. כאן מושכים את הנתונים המבניים:
  • אוכלוסייה לפי ישוב (pop24/pop18/naturalPct)
  • מלאי דירות / בנייה (stock, active, permits)
  • מלאי לא מכור (unsold24)
  • מיפוי שם עיר -> סמל יישוב (semel) דרך דאטהסט הישובים

עיקרון מפתח: ה-resource_id מתגלה בזמן ריצה (discover_resource) לפי מילות חיפוש,
כי הוא מתחלף כשהלמ"ס מעלה גרסה חדשה. כך הצינור לא נשבר בעדכון.

הערות תפעוליות:
  • data.gov.il עם WAF — חובה User-Agent אמיתי (מוגדר ב-config.HTTP_HEADERS).
  • עברית ב-URL עוברת אוטומטית דרך requests (params).
  • מעבר ל-32K רשומות: עימוד עם offset/limit.
"""
import requests
import config


def _ckan(action_url, params):
    r = requests.get(action_url, params=params, headers=config.HTTP_HEADERS,
                     timeout=config.HTTP_TIMEOUT)
    r.raise_for_status()
    js = r.json()
    if not js.get("success"):
        raise RuntimeError(f"CKAN error: {js}")
    return js["result"]


def discover_resource(query):
    """
    מאתר את ה-resource_id הראשון (datastore active) של דאטהסט שתואם למילות חיפוש.
    מחזיר (package_title, resource_id) או (None, None).
    """
    try:
        res = _ckan(config.CKAN_PACKAGE_SEARCH, {"q": query, "rows": 10})
        for pkg in res.get("results", []):
            for resource in pkg.get("resources", []):
                if resource.get("datastore_active"):
                    return pkg.get("title"), resource.get("id")
    except Exception as e:
        print(f"[datagov] discover '{query}' failed: {e}")
    return None, None


def fetch_records(resource_id, limit=100000, q=None):
    """
    מושך רשומות מ-datastore_search עם עימוד עד limit.
    מחזיר רשימת dict.
    """
    out, offset, page = [], 0, 32000
    while offset < limit:
        params = {"resource_id": resource_id, "limit": min(page, limit - offset),
                  "offset": offset}
        if q:
            params["q"] = q
        try:
            res = _ckan(config.CKAN_DATASTORE, params)
        except Exception as e:
            print(f"[datagov] fetch failed at offset {offset}: {e}")
            break
        recs = res.get("records", [])
        out.extend(recs)
        if len(recs) < params["limit"]:
            break
        offset += len(recs)
    return out


# --- שכבת "תרגום" מרשומות גולמיות לשדות הסכמה -------------------------------
# כל פונקציה מקבלת את שם העיר ומחזירה dict חלקי של שדות לעדכון.
# מבנה הרשומות משתנה בין דאטהסטים — לכן השמות נשלפים בסלחנות (כמה חלופות).

def _num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def build_locality_index():
    """שם עיר -> סמל יישוב, מתוך דאטהסט הישובים הרשמי."""
    _, rid = discover_resource(config.CKAN_QUERIES["localities"])
    idx = {}
    if not rid:
        return idx
    for rec in fetch_records(rid, limit=5000):
        name = rec.get("שם_ישוב") or rec.get("שם ישוב") or rec.get("name")
        semel = rec.get("סמל_ישוב") or rec.get("סמל ישוב") or rec.get("code")
        if name and semel:
            idx[str(name).strip()] = str(semel).strip()
    return idx


def fetch_population_by_city():
    """מחזיר {city_name: {pop, naturalPct}} מהדאטהסט העדכני ביותר."""
    _, rid = discover_resource(config.CKAN_QUERIES["population"])
    out = {}
    if not rid:
        return out
    for rec in fetch_records(rid, limit=5000):
        name = rec.get("שם_ישוב") or rec.get("שם ישוב")
        pop = _num(rec.get("סהכ") or rec.get("סה\"כ") or rec.get("total"))
        if name and pop:
            out[str(name).strip()] = {"pop": pop}
    return out


def fetch_unsold_by_city():
    """מחזיר {city_name: unsold_units} מדאטהסט המלאי הלא מכור."""
    _, rid = discover_resource(config.CKAN_QUERIES["unsold"])
    out = {}
    if not rid:
        return out
    for rec in fetch_records(rid, limit=5000):
        name = rec.get("שם_ישוב") or rec.get("ישוב") or rec.get("name")
        units = _num(rec.get("מלאי") or rec.get("דירות") or rec.get("value"))
        if name and units is not None:
            out[str(name).strip()] = units
    return out


if __name__ == "__main__":
    for key, q in config.CKAN_QUERIES.items():
        title, rid = discover_resource(q)
        print(f"{key:18} -> {rid}  ({title})")
