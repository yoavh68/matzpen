# -*- coding: utf-8 -*-
"""
config.py — הגדרות מרכזיות לצינור הנתונים של "מצפן · NADLAN INTELLIGENCE"

כל ה-endpoints, קודי המדדים, ומיפוי מקור->שדה נמצאים כאן.
שינוי מקור נתונים = עריכה כאן בלבד, בלי לגעת בקוד הלוגיקה.
"""

# ----------------------------------------------------------------------------
# 1. למ"ס — API רשמי למדדי מחירים  (מאומת, עובד, חינמי)
#    תיעוד: https://www.cbs.gov.il/he/Pages/מדדי-מחירים-באמצעות-API.aspx
# ----------------------------------------------------------------------------
CBS_BASE = "https://api.cbs.gov.il/index"

# קטלוג הנושאים — לאיתור קוד המדד הנכון לפי טקסט חיפוש
CBS_CATALOG_TREE = CBS_BASE + "/catalog/tree"      # ?q=...&format=json
# משיכת נתוני מדד לפי קוד
CBS_DATA_PRICE   = CBS_BASE + "/data/price"         # ?id={code}&format=json&last=N
# כל מדדי הדיור (פרק aa = "מדד ומחירים ממוצעים משוק הדירות")
CBS_PRICE_ALL    = CBS_BASE + "/data/price_all"     # ?chapter=aa&format=xml  (XML בלבד)

# פרק aa מכיל מחירים ממוצעים אמיתיים לפי אזור/מחוז (לא רק מדד) — הבסיס ל-price24.
# שים לב: הנתון הוא ברמת מחוז/אזור, לא 51 ערים. לדיוק ברמת עיר משתמשים ב-nadlan.
CBS_HOUSING_CHAPTER = "aa"

# קוד מדד מחירי הדירות הארצי (לשימוש כ-NATIONAL.priceIdx fallback).
# מאומת ידנית מול הקטלוג בהרצה ראשונה (ראה discover_cbs_codes()).
CBS_HOUSING_INDEX_CODE = None  # יתמלא אוטומטית ע"י discover

# ----------------------------------------------------------------------------
# 2. data.gov.il — CKAN API (פורטל נתונים פתוחים ממשלתי)
#    תיעוד: https://data.gov.il/api/docs
#    תבנית: package_search -> package_show -> datastore_search
#    הערה: דורש User-Agent אמיתי כדי לעקוף WAF, וקידוד עברית ב-URL.
# ----------------------------------------------------------------------------
CKAN_BASE = "https://data.gov.il/api/3/action"
CKAN_PACKAGE_SEARCH  = CKAN_BASE + "/package_search"
CKAN_PACKAGE_SHOW    = CKAN_BASE + "/package_show"
CKAN_DATASTORE       = CKAN_BASE + "/datastore_search"
CKAN_DATASTORE_SQL   = CKAN_BASE + "/datastore_search_sql"

# מילות חיפוש לאיתור הדאטהסטים הרלוונטיים (ה-resource_id מתגלה בזמן ריצה,
# כי הוא משתנה כשהלמ"ס מעדכן גרסה — לכן לא קובעים אותו קשיח).
CKAN_QUERIES = {
    "localities":     "רשימת ישובים סמל יישוב",    # מיפוי שם עיר -> סמל יישוב (semel)
    "population":     "אוכלוסייה ישובים סוף שנה",
    "building_starts":"התחלות בנייה גמר בנייה",
    "building_permits":"היתרי בנייה",
    "unsold":         "מלאי דירות חדשות לא מכורות",
}

# ----------------------------------------------------------------------------
# 3. nadlan.gov.il — עסקאות אמיתיות (רשות המסים / KARMEN)
#    אין API רשמי. קיים endpoint פנימי לא מתועד שמשמש את האתר עצמו.
#    ⚠️ שיקול משפטי: בדוק את תנאי השימוש של האתר לפני שימוש מסחרי/אוטומטי.
#    מתג ENABLE_NADLAN שולט אם המודול רץ בכלל.
# ----------------------------------------------------------------------------
ENABLE_NADLAN = False  # ברירת מחדל כבוי עד אישור משפטי. שנה ל-True להפעלה.
NADLAN_BASE = "https://www.nadlan.gov.il/Nadlan.REST/Main"
NADLAN_SEARCH = NADLAN_BASE + "/GetDataByQuery"   # לפי שם עיר/כתובת
NADLAN_DEALS  = NADLAN_BASE + "/GetAssestAndDeals" # רשימת עסקאות לאזור

# ----------------------------------------------------------------------------
# 4. מיפוי מקור -> שדה + רמת אמינות הבסיסית של כל שדה
#    high=🟢  mid=🟡  low=🔴   (תואם את METHODOLOGY.md סעיף 6)
# ----------------------------------------------------------------------------
# המקור הסמכותי לכל שדה גולמי בסכמת CITIES.
FIELD_SOURCES = {
    "pop24":       {"source": "datagov:population",      "reliability": "high"},
    "pop18":       {"source": "datagov:population",      "reliability": "high"},
    "stock24":     {"source": "datagov:building_starts", "reliability": "high"},
    "stock18":     {"source": "datagov:building_starts", "reliability": "high"},
    "naturalPct":  {"source": "datagov:population",      "reliability": "high"},
    "active":      {"source": "datagov:building_starts", "reliability": "mid"},
    "permits":     {"source": "datagov:building_permits","reliability": "mid"},
    "unsold24":    {"source": "datagov:unsold",          "reliability": "high"},  # 17 ערים מובילות
    "price24":     {"source": "nadlan",                  "reliability": "high"},  # 🟡->🟢 כשנדל"ן פעיל
    "price18":     {"source": "nadlan",                  "reliability": "mid"},
    "rent2025":    {"source": "cbs:rent_index",          "reliability": "high"},  # 18 ערים
    "sales25new":  {"source": "datagov:transactions",    "reliability": "high"},
    "sales25used": {"source": "datagov:transactions",    "reliability": "high"},
    "sales24total":{"source": "datagov:transactions",    "reliability": "high"},
    # שדות תכנון — אין מקור feed נקי, נשארים אומדן (🔴)
    "tbaUnits":    {"source": "manual:estimate",         "reliability": "low"},
    "popPotential":{"source": "manual:estimate",         "reliability": "low"},
}

# שדות שהצינור לעולם לא דורס (אומדנים מקצועיים שאין להם מקור רשמי).
PROTECTED_FIELDS = {"tbaUnits", "popPotential", "r", "n"}

# ----------------------------------------------------------------------------
# 5. נתיבים
# ----------------------------------------------------------------------------
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
SEED_JSON   = os.path.join(ROOT, "output", "cities.seed.json")   # נקודת התחלה
OUTPUT_JSON = os.path.join(ROOT, "output", "cities.json")        # תוצר הצינור
HTML_PATH   = os.path.join(os.path.dirname(ROOT), "nadlan_analytics.html")
REPORT_MD   = os.path.join(ROOT, "output", "refresh_report.md")  # דוח ריצה

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NadlanIntelligence/2.0; +https://example.com)",
    "Accept": "application/json, text/xml, */*",
}
HTTP_TIMEOUT = 30
