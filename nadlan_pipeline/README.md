# nadlan_pipeline — הפיכת "מצפן" למערכת חיה ואוטומטית

צינור נתונים שמושך מקורות רשמיים, מתייג אמינות, ומזריק נתונים טריים
ישירות לתוך `nadlan_analytics.html` — בלי לשבור את האפליקציה ובלי שרת.

```
┌─────────────┐   ┌──────────────┐   ┌───────────┐   ┌──────────────────┐
│ data.gov.il │──▶│              │   │           │   │                  │
│   למ"ס API  │──▶│  build.py    │──▶│ cities.json│──▶│ הזרקה ל-HTML      │
│ nadlan.gov  │──▶│ (ממזג+מתייג) │   │ +דוח אמינות│   │ (סטטי, אופליין)  │
└─────────────┘   └──────────────┘   └───────────┘   └──────────────────┘
        GitHub Actions מריץ את זה אוטומטית פעמיים בחודש
```

## מבנה
```
nadlan_pipeline/
├── build.py              ← הרץ אותי:  python build.py
├── config.py             ← כל ה-endpoints, המקורות, ומתג nadlan
├── normalize.py          ← מיזוג + תיוג אמינות 🟢🟡🔴
├── sources/
│   ├── cbs.py            ← למ"ס API (מדד מחירים, מחירים ממוצעים)  ✅ מאומת
│   ├── datagov.py        ← data.gov.il CKAN (אוכלוסייה, מלאי, בנייה)
│   └── nadlan.py         ← עסקאות אמיתיות (כבוי כברירת מחדל ⚠️)
├── output/
│   ├── cities.seed.json  ← נקודת התחלה (51 ערים, חולץ מה-HTML)
│   ├── cities.json       ← תוצר הצינור (נוצר בריצה)
│   └── refresh_report.md ← דוח מה התעדכן ומה האמינות
└── .github/workflows/refresh.yml  ← האוטומציה
```

## הרצה מקומית (לבדיקה)
```bash
cd nadlan_pipeline
pip install -r requirements.txt
python build.py
```
הצינור "נכשל ברכות": אם מקור לא זמין, השדה הקיים נשמר והדבר מדווח ב-`refresh_report.md`.

## בדיקת מקורות בנפרד
```bash
python -m sources.datagov   # מדפיס אילו resource_id התגלו ב-data.gov.il
python -m sources.cbs       # מאתר את קוד מדד מחירי הדירות ומדפיס ערכים אחרונים
```

## מה כל מקור מספק (תואם DATA_SOURCES.md)
| שדה | מקור | אמינות |
|---|---|---|
| pop24 / pop18 / naturalPct | data.gov.il (אוכלוסייה) | 🟢 |
| stock / active / permits | data.gov.il (בנייה) | 🟢/🟡 |
| unsold24 | data.gov.il (מלאי לא מכור) | 🟢 (17 ערים) |
| **price24** | **nadlan.gov.il (עסקאות בפועל)** | 🟢 כשמופעל |
| rent2025 | למ"ס (מדד שכ"ד) | 🟢 (18 ערים) |
| מדד מחירים ארצי | למ"ס API | 🟢 |
| tbaUnits / popPotential | אומדן (אין feed) | 🔴 — לא נדרס |

## ⚠️ הפעלת nadlan (price24 מ-🟡 ל-🟢)
המקור הזה כבוי כברירת מחדל. כדי להפעיל:
1. **בדוק את תנאי השימוש של nadlan.gov.il והתייעץ משפטית** — אין API רשמי.
2. ב-`config.py` שנה `ENABLE_NADLAN = False` ל-`True`.
3. הרץ `python build.py`.

## הקמת האוטומציה (GitHub Actions + Pages — מומלץ, חינמי)
1. צור repo ב-GitHub והעלה אליו את כל תיקיית הפרויקט (כולל `nadlan_analytics.html` ו-`nadlan_pipeline/`).
2. הקובץ `.github/workflows/refresh.yml` כבר מוגדר — GitHub יזהה אותו אוטומטית.
3. Settings → Pages → בחר את ה-branch הראשי. האתר יתפרסם בכתובת `https://<user>.github.io/<repo>/nadlan_analytics.html`.
4. ה-workflow ירוץ ב-1 וב-15 לחודש, ימשוך נתונים, יזריק ל-HTML, וידחוף — והאתר יתעדכן מעצמו.
5. להרצה ידנית מיידית: Actions → "רענון נתוני מצפן" → Run workflow.

## החלפת מודל הרצה
הקוד זהה בכל מודל — רק המתזמן משתנה:
- **מקומי**: הרץ `python build.py` ידנית, או דרך Task Scheduler (Windows) / cron.
- **Cloud Function**: עטוף את `run()` ב-handler והפעל עם Cloud Scheduler.
- **שרת/VPS**: הוסף שורת cron שמריצה את `build.py`.

## הערות דיוק
- בהרצה הראשונה ה-resource_id מתגלה אוטומטית לפי מילות חיפוש ב-`config.CKAN_QUERIES`.
  אם דאטהסט לא נמצא, הרץ `python -m sources.datagov` וכוונן את מילות החיפוש.
- מדד למ"ס הוא ברמת מחוז/אזור; דיוק ברמת עיר מגיע מ-nadlan בלבד.
- שלושת הערכים האחרונים של מדד מחירי הדירות "ארעיים" (מתעדכנים) — כך גם בלמ"ס.
