# -*- coding: utf-8 -*-
"""
diagnose.py — כלי אבחון. הרצה:  python diagnose.py

מטרה: לתפוס את המבנה האמיתי של התשובות מ-nadlan ומ-iplan (ומ-data.gov.il)
ולכתוב אותו ל-output/diagnostics.md. כך אפשר לתקן את הפרסרים לפי נתונים אמיתיים
בלי גישה ישירה ל-APIs.

מריצים את זה ב-GitHub Actions (שם יש גישת רשת), והפלט נדחף ל-repo לעיון.
"""
import json
import requests
import config

CITY = "תל אביב"          # עיר בדיקה
OUT = []


def log(title, obj, limit=2500):
    OUT.append(f"\n## {title}\n")
    if isinstance(obj, (dict, list)):
        txt = json.dumps(obj, ensure_ascii=False, indent=2)
    else:
        txt = str(obj)
    if len(txt) > limit:
        txt = txt[:limit] + "\n... [נחתך] ..."
    OUT.append("```json\n" + txt + "\n```")


def keys_only(obj, depth=0):
    """מחזיר מבנה מפתחות בלבד (בלי ערכים ארוכים) כדי לזהות שמות שדות."""
    if isinstance(obj, dict):
        return {k: keys_only(v, depth + 1) for k, v in list(obj.items())[:25]}
    if isinstance(obj, list):
        return [keys_only(obj[0], depth + 1)] if obj else []
    return type(obj).__name__


# ---- nadlan ----------------------------------------------------------------
def diag_nadlan():
    OUT.append("# אבחון nadlan.gov.il")
    try:
        r1 = requests.post(config.NADLAN_SEARCH, json={"query": CITY},
                           headers=config.HTTP_HEADERS, timeout=config.HTTP_TIMEOUT)
        OUT.append(f"\nGetDataByQuery status: {r1.status_code}")
        try:
            q = r1.json()
            log("GetDataByQuery — מבנה מפתחות", keys_only(q))
            log("GetDataByQuery — תשובה גולמית (תחילה)", q)
        except Exception as e:
            log("GetDataByQuery — טקסט גולמי (לא JSON)", r1.text[:1500])
            q = None

        if q:
            payload = {**(q.get("navProps") or q), "PageNo": 1, "OrderByFilled": "true"}
            r2 = requests.post(config.NADLAN_DEALS, json=payload,
                               headers=config.HTTP_HEADERS, timeout=config.HTTP_TIMEOUT)
            OUT.append(f"\nGetAssestAndDeals status: {r2.status_code}")
            try:
                d = r2.json()
                log("GetAssestAndDeals — מבנה מפתחות", keys_only(d))
                # דגימת עסקה אחת
                results = d.get("AllResults") or d.get("results") or []
                if results:
                    log("דוגמת עסקה בודדת (שמות השדות החשובים!)", results[0])
            except Exception as e:
                log("GetAssestAndDeals — טקסט גולמי", r2.text[:1500])
    except Exception as e:
        OUT.append(f"\n❌ nadlan נכשל לגמרי: {e}")


# ---- iplan (תב"ע) ----------------------------------------------------------
def diag_iplan():
    OUT.append("\n\n# אבחון iplan (מנהל התכנון / XPLAN)")
    # קודם: לבדוק אילו שדות יש בשכבה
    try:
        meta = requests.get(config.IPLAN_XPLAN_QUERY.replace("/query", ""),
                            params={"f": "json"}, headers=config.HTTP_HEADERS,
                            timeout=config.HTTP_TIMEOUT)
        m = meta.json()
        fields = [f.get("name") for f in m.get("fields", [])]
        log("שדות זמינים בשכבת XPLAN", fields)
    except Exception as e:
        OUT.append(f"\n⚠️ שליפת שדות נכשלה: {e}")

    # שאילתת דגימה — תוכניות הקשורות לעיר הבדיקה
    try:
        params = {"where": "1=1", "outFields": "*", "f": "json",
                  "resultRecordCount": 3, "returnGeometry": "false"}
        r = requests.get(config.IPLAN_XPLAN_QUERY, params=params,
                         headers=config.HTTP_HEADERS, timeout=config.HTTP_TIMEOUT)
        j = r.json()
        feats = j.get("features", [])
        if feats:
            log("דוגמת תוכנית (חפש כאן שדה יח\"ד וסטטוס!)", feats[0].get("attributes"))
        else:
            log("תשובת XPLAN (ללא features)", j)
    except Exception as e:
        OUT.append(f"\n❌ שאילתת XPLAN נכשלה: {e}")


# ---- data.gov.il -----------------------------------------------------------
def diag_datagov():
    OUT.append("\n\n# אבחון data.gov.il (איתור דאטהסטים)")
    from sources import datagov
    for key, q in config.CKAN_QUERIES.items():
        title, rid = datagov.discover_resource(q)
        OUT.append(f"- **{key}** (q='{q}') → resource_id: `{rid}`  | {title}")


if __name__ == "__main__":
    diag_nadlan()
    diag_iplan()
    diag_datagov()
    import os
    path = os.path.join(config.ROOT, "output", "diagnostics.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(OUT))
    print("נכתב:", path)
    print("\n".join(OUT)[:1200])
