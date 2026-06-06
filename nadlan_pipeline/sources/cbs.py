# -*- coding: utf-8 -*-
"""
sources/cbs.py — חיבור ל-API הרשמי של הלמ"ס (api.cbs.gov.il)

מקור מאומת ועובד. משמש כאן ל:
  • מדד מחירי הדירות הארצי  -> NATIONAL.priceIdx (מגמת מחירים)
  • מחירים ממוצעים משוק הדירות (פרק aa) -> הצלבה ל-price24
  • מדד שכר דירה -> rent2025 (ברמה ארצית/אזורית)

ה-API מחזיר XML/JSON. price_all תומך כרגע ב-XML בלבד.
"""
import requests
import xml.etree.ElementTree as ET
import config


def _get(url, params):
    params = {**params, "format": params.get("format", "json"), "download": "false"}
    r = requests.get(url, params=params, headers=config.HTTP_HEADERS,
                     timeout=config.HTTP_TIMEOUT)
    r.raise_for_status()
    return r


def discover_housing_index_code():
    """
    מאתר את קוד מדד מחירי הדירות בקטלוג הלמ"ס לפי טקסט חיפוש.
    מחזיר את קוד המדד (int) או None. מריצים פעם אחת; אפשר לשמור ב-config.
    """
    try:
        r = _get(config.CBS_CATALOG_TREE,
                 {"q": "מחירי דירות", "string_match_type": "contains", "format": "json"})
        data = r.json()
        # מבנה התשובה: רשימת נושאים עם code+name. מחזירים את ההתאמה הראשונה.
        for item in _flatten_catalog(data):
            name = (item.get("name") or item.get("Name") or "")
            if "מחירי הדירות" in name or "מחירי דירות" in name:
                return item.get("code") or item.get("Code")
    except Exception as e:
        print(f"[cbs] discover failed: {e}")
    return None


def _flatten_catalog(node, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        if "code" in node or "Code" in node:
            out.append(node)
        for v in node.values():
            _flatten_catalog(v, out)
    elif isinstance(node, list):
        for v in node:
            _flatten_catalog(v, out)
    return out


def fetch_housing_price_index(last=12):
    """
    מחזיר את ערכי מדד מחירי הדירות האחרונים: [{period, value}, ...]
    משמש לעדכון NATIONAL.priceIdx באפליקציה.
    """
    code = config.CBS_HOUSING_INDEX_CODE or discover_housing_index_code()
    if not code:
        print("[cbs] housing index code not found — skipping")
        return []
    try:
        r = _get(config.CBS_DATA_PRICE, {"id": code, "last": last, "format": "json"})
        data = r.json()
        rows = []
        for s in _flatten_catalog(data):
            # שדות אופייניים: date / value / month / year
            val = s.get("value") or s.get("Value") or s.get("currBase", {})
            if isinstance(val, (int, float)):
                rows.append({"period": s.get("date") or s.get("Date"), "value": val})
        return rows
    except Exception as e:
        print(f"[cbs] index fetch failed: {e}")
        return []


def fetch_housing_avg_prices():
    """
    פרק aa = "מדד ומחירים ממוצעים משוק הדירות".
    מחזיר מחירים ממוצעים לפי אזור (לא 51 ערים) — להצלבה/בקרת שפיות מול nadlan.
    מחזיר dict {region_or_label: avg_price} ככל שזמין, אחרת {} .
    """
    try:
        r = _get(config.CBS_PRICE_ALL,
                 {"chapter": config.CBS_HOUSING_CHAPTER, "format": "xml"})
        root = ET.fromstring(r.content)
        prices = {}
        for el in root.iter():
            # XML של הלמ"ס משתנה במבנה — שולפים זוגות label/value בצורה סלחנית
            label = el.attrib.get("name") or el.attrib.get("Name")
            value = el.attrib.get("value") or el.attrib.get("Value")
            if label and value:
                try:
                    prices[label] = float(str(value).replace(",", ""))
                except ValueError:
                    pass
        return prices
    except Exception as e:
        print(f"[cbs] avg prices fetch failed: {e}")
        return {}


if __name__ == "__main__":
    print("housing index code:", discover_housing_index_code())
    print("last index values:", fetch_housing_price_index(3))
