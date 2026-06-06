# -*- coding: utf-8 -*-
"""
normalize.py — מיזוג נתונים טריים לתוך סכמת CITIES + תיוג אמינות

מקבל את ה-seed (הנתונים הקיימים) ואת התוצרים מכל מקור,
ומחזיר רשימת ערים מעודכנת + מטא-נתוני אמינות לכל שדה ולכל עיר.

עיקרון: מקור רשמי דורס אומדן, אבל לעולם לא דורסים PROTECTED_FIELDS,
ולא דורסים ערך קיים בערך ריק (None) ממקור שנכשל.
"""
import config

REL_WEIGHT = {"high": 1.0, "mid": 0.6, "low": 0.2}


def merge_city(city, updates):
    """
    city   = dict קיים (seed)
    updates= dict {field: (value, reliability)}  מהמקורות
    מעדכן in-place ומחזיר את city עם city['_rel'] = {field: reliability}.
    """
    rel = city.get("_rel", {})
    for field, (value, reliability) in updates.items():
        if field in config.PROTECTED_FIELDS:
            continue
        if value is None:
            # מקור נכשל — שומרים על הקיים, אבל מורידים את התג אם היה אומדן
            rel.setdefault(field, config.FIELD_SOURCES.get(field, {}).get("reliability", "low"))
            continue
        city[field] = value
        rel[field] = reliability
    # שדות שלא נגענו בהם — תג ברירת מחדל לפי המיפוי
    for field in city:
        if field.startswith("_"):
            continue
        rel.setdefault(field, config.FIELD_SOURCES.get(field, {}).get("reliability", "high"))
    city["_rel"] = rel
    return city


def city_reliability_score(city):
    """ציון אמינות 0-100 לעיר = ממוצע משוקלל של תגי השדות (METHODOLOGY §6)."""
    rels = city.get("_rel", {})
    if not rels:
        return 0
    score = sum(REL_WEIGHT.get(r, 0.2) for r in rels.values()) / len(rels)
    return round(score * 100)


def finalize(cities):
    """מוסיף ציון אמינות לכל עיר ומסכם."""
    for c in cities:
        c["_relScore"] = city_reliability_score(c)
    return cities


def reliability_summary(cities):
    high = sum(1 for c in cities if c["_relScore"] >= 75)
    mid  = sum(1 for c in cities if 55 <= c["_relScore"] < 75)
    low  = sum(1 for c in cities if c["_relScore"] < 55)
    return {"high": high, "mid": mid, "low": low, "total": len(cities)}
