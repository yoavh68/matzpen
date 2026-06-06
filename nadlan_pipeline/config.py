# -*- coding: utf-8 -*-
"""
config.py - הגדרות מרכזיות לצינור הנתונים של "מצפן NADLAN INTELLIGENCE"
כל ה-endpoints, קודי המדדים, ומיפוי מקור->שדה נמצאים כאן.
"""

# ---------------------------------------------------------------------------
# 1. למ"ס - API רשמי למדדי מחירים (מאומת, עובד, חינמי)
# ---------------------------------------------------------------------------
CBS_BASE = "https://api.cbs.gov.il/index"
CBS_CATALOG_TREE = CBS_BASE + "/catalog/tree"
CBS_DATA_PRICE = CBS_BASE + "/data/price"
CBS_PRICE_ALL = CBS_BASE + "/data/price_all"
CBS_HOUSING_CHAPTER = "aa"
CBS_HOUSING_INDEX_CODE = None

# ---------------------------------------------------------------------------
# 2. data.gov.il - CKAN API
#    מילות חיפוש - מילה אחת/קצרה! CKAN עושה AND, ביטוי ארוך = 0 תוצאות.
# ---------------------------------------------------------------------------
CKAN_BASE = "https://data.gov.il/api/3/action"
CKAN_PACKAGE_SEARCH = CKAN_BASE + "/package_search"
CKAN_PACKAGE_SHOW = CKAN_BASE + "/package_show"
CKAN_DATASTORE = CKAN_BASE + "/datastore_search"
CKAN_DATASTORE_SQL = CKAN_BASE + "/datastore_search_sql"

CKAN_QUERIES = {
    "localities": "ישובים",
    "population": "אוכלוסייה",
    "building_starts": "בנייה",
    "building_permits": "היתרי",
    "unsold": "דירות",
}

# ---------------------------------------------------------------------------
# 3. nadlan.gov.il - עסקאות אמיתיות (רשות המסים / KARMEN)
#    אין API רשמי. שיקול משפטי - האחריות על המשתמש.
# ---------------------------------------------------------------------------
ENABLE_NADLAN = True
NADLAN_BASE = "https://www.nadlan.gov.il/Nadlan.REST/Main"
NADLAN_SEARCH = NADLAN_BASE + "/GetDataByQuery"
NADLAN_DEALS = NADLAN_BASE + "/GetAssestAndDeals"

# ---------------------------------------------------------------------------
# 3b. מנהל התכנון (iplan / מבא"ת) - תב"ע: יחידות דיור בתוכניות
# ---------------------------------------------------------------------------
ENABLE_IPLAN = True
IPLAN_XPLAN_QUERY = "https://ags.iplan.gov.il/arcgis/rest/services/PlanningPublic/Xplan/MapServer/0/query"
TBA_PLAN_STATUS = "approved"

# ---------------------------------------------------------------------------
# 4. מיפוי מקור -> שדה + רמת אמינות (high/mid/low)
# ---------------------------------------------------------------------------
FIELD_SOURCES = {
    "pop24": {"source": "datagov:population", "reliability": "high"},
    "pop18": {"source": "datagov:population", "reliability": "high"},
    "stock24": {"source": "datagov:building_starts", "reliability": "high"},
    "stock18": {"source": "datagov:building_starts", "reliability": "high"},
    "naturalPct": {"source": "datagov:population", "reliability": "high"},
    "active": {"source": "datagov:building_starts", "reliability": "mid"},
    "permits": {"source": "datagov:building_permits", "reliability": "mid"},
    "unsold24": {"source": "datagov:unsold", "reliability": "high"},
    "price24": {"source": "nadlan", "reliability": "high"},
    "price18": {"source": "nadlan", "reliability": "mid"},
    "rent2025": {"source": "cbs:rent_index", "reliability": "high"},
    "sales25new": {"source": "datagov:transactions", "reliability": "high"},
    "sales25used": {"source": "datagov:transactions", "reliability": "high"},
    "sales24total": {"source": "datagov:transactions", "reliability": "high"},
    "tbaUnits": {"source": "iplan", "reliability": "mid"},
    "popPotential": {"source": "manual:estimate", "reliability": "low"},
}

PROTECTED_FIELDS = {"popPotential", "r", "n"}

# ---------------------------------------------------------------------------
# 5. נתיבים
# ---------------------------------------------------------------------------
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
SEED_JSON = os.path.join(ROOT, "output", "cities.seed.json")
OUTPUT_JSON = os.path.join(ROOT, "output", "cities.json")
HTML_PATH = os.path.join(os.path.dirname(ROOT), "nadlan_analytics.html")
REPORT_MD = os.path.join(ROOT, "output", "refresh_report.md")

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NadlanIntelligence/2.0)",
    "Accept": "application/json, text/xml, */*",
}
HTTP_TIMEOUT = 30
