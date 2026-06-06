# אבחון nadlan.gov.il

GetDataByQuery status: 200

## GetDataByQuery — טקסט גולמי (לא JSON)

```json
<!doctype html>
<html lang="en">
<head>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <!-- TO DO ->  REMEMBER TO REMOVE THE META TAGS BELOW IN PRODUCTION -->
    <!-- <meta name="robots" content="noindex, nofollow">
    <meta http-equiv="X-Robots-Tag" content="noindex, nofollow"> -->
    
    <title data-react-helmet="true">××ª×¨ ×× ××&quot;× ××××©××ª×</title>
    <meta charset="utf-8" />
    <link rel="icon" href="/nadlan-icon.png" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <link rel="apple-touch-icon" href="/logo192.png" />
    <style src="./assets/styles/main.css"></style>
    <style src="./assets/styles/chunks.css"></style>
    <style src="./assets/styles/reset.scss"></style>

    <meta property="og:title" content="Gov × ××&quot;×" />
    <meta property="og:description" content="××ª×¨ ×× ××&quot;× ××××©××ª×" />
    <meta property="og:image" content="https://dev.nadlan.gov.il/images/share.jpeg" />
    <meta property="og:url" content="https://dev.nadlan.gov.il" />
    <meta property="og:type" content="website" />

    <script>
      const isProduction = window.location.hostname === "www.nadlan.gov.il";
        //"6LdJAz4qAAAAAGnDqX4rT9kMeQSWngUOsYTHOtNT"
    
      if (!isProduction) {
        const robotsMeta = document.crea
```


# אבחון iplan (מנהל התכנון / XPLAN)

⚠️ שליפת שדות נכשלה: HTTPSConnectionPool(host='ags.iplan.gov.il', port=443): Max retries exceeded with url: /arcgis/rest/services/PlanningPublic/Xplan/MapServer/0?f=json (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1010)')))

❌ שאילתת XPLAN נכשלה: HTTPSConnectionPool(host='ags.iplan.gov.il', port=443): Max retries exceeded with url: /arcgis/rest/services/PlanningPublic/Xplan/MapServer/0/query?where=1%3D1&outFields=%2A&f=json&resultRecordCount=3&returnGeometry=false (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1010)')))


# אבחון data.gov.il (איתור דאטהסטים)
- **localities** (q='ישובים') → resource_id: `b8112650-a2f8-41f2-9c05-a9b9483fb4c0`  | תושבים צעירים בישראל לפי ישובים
- **population** (q='אוכלוסייה') → resource_id: `dac7a88f-d627-46be-93e8-4901ac8242fb`  | טבלת המרה שכונות - אזורים סטטיסטיים
- **building_starts** (q='בנייה') → resource_id: `b9257d8f-f93a-4c7d-84dd-e4b0838eadaa`  | אתרי בניה שנסגרו
- **building_permits** (q='היתרי') → resource_id: `7cfee2aa-1ab3-41f6-aedb-e0eb92f5ad3b`  | היתרי שריפת גזם חקלאי
- **unsold** (q='דירות') → resource_id: `7c8255d0-49ef-49db-8904-4cf917586031`  | נתונים תקופתיים - תכנית דירה בהנחה