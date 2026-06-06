# -*- coding: utf-8 -*-
"""
sources/nadlan.py — עסקאות נדל"ן אמיתיות מ-nadlan.gov.il (רשות המסים / KARMEN)

זה המקור היחיד למחיר עסקאות *בפועל* לכל עיר — הפתרון לבעיית "3 ההגדרות
של מחיר ממוצע" המתוארת ב-DATA_SOURCES.md. מחליף את price24 ה-🟡 ב-🟢.

⚠️  אזהרה משפטית
    לאתר nadlan.gov.il אין API ציבורי רשמי. הקוד כאן משתמש ב-endpoint
    הפנימי שהאתר עצמו צורך. שימוש אוטומטי/מסחרי עשוי לחרוג מתנאי השימוש.
    >>> בדוק תנאי שימוש והתייעץ משפטית לפני הפעלה. <<<
    המודול כבוי כברירת מחדל (config.ENABLE_NADLAN = False).

מתודולוגיה: מושכים עסקאות אחרונות לעיר, מסננים לדירות מגורים,
מחשבים מחיר ממוצע/חציוני -> price24. שנה את חלון התאריכים ל-price18.
"""
import statistics
import requests
import config


def _post(url, payload):
    r = requests.post(url, json=payload, headers=config.HTTP_HEADERS,
                      timeout=config.HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()


def fetch_city_deals(city_name, max_pages=5):
    """
    מחזיר רשימת עסקאות גולמיות לעיר. כל עסקה: {price, rooms, date, ...}.
    מבנה התשובה של nadlan משתנה — נשלף בסלחנות.
    """
    if not config.ENABLE_NADLAN:
        return []
    deals = []
    try:
        # שלב 1: פתרון שם עיר -> אובייקט חיפוש (polygon/neighborhood id)
        q = _post(config.NADLAN_SEARCH, {"query": city_name})
        nav = q.get("navProps") or q
        # שלב 2: משיכת עסקאות עמוד-אחר-עמוד
        for page in range(1, max_pages + 1):
            payload = {**nav, "PageNo": page, "OrderByFilled": "true"}
            res = _post(config.NADLAN_DEALS, payload)
            batch = res.get("AllResults") or res.get("results") or []
            if not batch:
                break
            deals.extend(batch)
    except Exception as e:
        print(f"[nadlan] {city_name}: {e}")
    return deals


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("₪", "").strip())
    except (TypeError, ValueError):
        return None


def city_average_price(city_name):
    """
    מחזיר מחיר ממוצע (חציון, עמיד לחריגים) לעיר, או None.
    מסנן עסקאות עם מחיר סביר בלבד (200K–20M).
    """
    deals = fetch_city_deals(city_name)
    prices = []
    for d in deals:
        p = _num(d.get("DEALAMOUNT") or d.get("price") or d.get("amount"))
        if p and 200_000 <= p <= 20_000_000:
            prices.append(p)
    if len(prices) < 5:        # מדגם קטן מדי — לא אמין
        return None
    return round(statistics.median(prices))


if __name__ == "__main__":
    config.ENABLE_NADLAN = True  # להרצת בדיקה ידנית בלבד
    for c in ["תל אביב-יפו", "באר שבע"]:
        print(c, "->", city_average_price(c))
