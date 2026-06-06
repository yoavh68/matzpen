# -*- coding: utf-8 -*-
"""
build.py - אורקסטרטור הצינור.  הרצה:  python build.py
טוען seed -> מושך מכל מקור -> ממזג+מתייג -> כותב cities.json -> מזריק ל-HTML.
נכשל "ברכות": אם מקור נופל, שומרים על הערך הקיים ומדווחים.
"""
import json
import re
import datetime
import config
from sources import datagov, cbs, nadlan, iplan
import normalize


def load_seed():
    with open(config.SEED_JSON, encoding="utf-8") as f:
        return json.load(f)


def collect_updates(cities):
    updates = {c["n"]: {} for c in cities}
    report = []

    # data.gov.il : אוכלוסייה
    try:
        pop = datagov.fetch_population_by_city()
        for name, d in pop.items():
            if name in updates and d.get("pop"):
                updates[name]["pop24"] = (d["pop"], "high")
        report.append(f"אוכלוסייה (data.gov.il): {len(pop)} ערים")
    except Exception as e:
        report.append(f"אוכלוסייה נכשל: {e}")

    # data.gov.il : מלאי לא מכור
    try:
        unsold = datagov.fetch_unsold_by_city()
        for name, units in unsold.items():
            if name in updates:
                updates[name]["unsold24"] = (units, "high")
        report.append(f"מלאי לא מכור (data.gov.il): {len(unsold)} ערים")
    except Exception as e:
        report.append(f"מלאי לא מכור נכשל: {e}")

    # nadlan.gov.il : מחיר עסקאות אמיתי
    if config.ENABLE_NADLAN:
        ok = 0
        for c in cities:
            price = nadlan.city_average_price(c["n"])
            if price:
                updates[c["n"]]["price24"] = (price, "high")
                ok += 1
        report.append(f"מחירי עסקאות (nadlan): {ok}/{len(cities)} ערים")
    else:
        report.append("nadlan כבוי - price24 נשאר כפי שהוא")

    # iplan : תב"ע (יחידות דיור בתוכניות)
    if config.ENABLE_IPLAN:
        try:
            tba = iplan.fetch_tba_by_city([c["n"] for c in cities])
            for name, units in tba.items():
                updates[name]["tbaUnits"] = (units, "mid")
            report.append(f"תב\"ע (iplan): {len(tba)} ערים")
        except Exception as e:
            report.append(f"תב\"ע (iplan) נכשל: {e}")

    # למ"ס : מדד מחירים ארצי
    try:
        idx = cbs.fetch_housing_price_index(6)
        report.append(f"מדד מחירי דירות (למ\"ס): {len(idx)} ערכים אחרונים")
    except Exception as e:
        report.append(f"מדד למ\"ס נכשל: {e}")

    return updates, report


def run():
    cities = load_seed()
    updates, report = collect_updates(cities)
    for c in cities:
        normalize.merge_city(c, updates.get(c["n"], {}))
    cities = normalize.finalize(cities)
    summary = normalize.reliability_summary(cities)

    with open(config.OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    inject_into_html(cities)
    write_report(report, summary)
    print("\n".join(report))
    print(f"\nרמות אמינות: {summary}")
    print(f"נכתב: {config.OUTPUT_JSON}")


def inject_into_html(cities):
    raw_fields = [k for k in cities[0] if not k.startswith("_")]
    lines = []
    for c in cities:
        parts = []
        for k in raw_fields:
            v = c.get(k)
            if v is None:
                continue
            parts.append(f'{k}:{json.dumps(v, ensure_ascii=False)}')
        lines.append("  {" + ", ".join(parts) + "}")
    stamp = datetime.date.today().isoformat()
    new_block = ('const CITIES = [\n  // updated automatically by nadlan_pipeline on '
                 + stamp + "\n" + ",\n".join(lines) + "\n];")

    with open(config.HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    new_html, n = re.subn(r"const CITIES = \[[\s\S]*?\n\];", new_block, html, count=1)
    if n == 1:
        with open(config.HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"הוזרק ל-HTML ({len(cities)} ערים)")
    else:
        print("לא נמצא בלוק CITIES ב-HTML - דילוג")


def write_report(report, summary):
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    md = ["# דוח רענון נתונים - מצפן", "", f"תאריך: {stamp}", "", "## מקורות", ""]
    md += [f"- {line}" for line in report]
    md += ["", "## אמינות כוללת", "",
           f"- גבוהה (75+): {summary['high']} ערים",
           f"- בינונית (55-74): {summary['mid']} ערים",
           f"- נמוכה (<55): {summary['low']} ערים"]
    with open(config.REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


if __name__ == "__main__":
    run()
