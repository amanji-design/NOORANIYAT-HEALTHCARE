# NOORANIYAT Healthcare - Bilingual Website

English + Arabic Flask website with professional homepage, WhatsApp contact, patient medical enquiry form, medical document upload, admin dashboard, sitemap and robots.txt.

Run locally:
    pip install -r requirements.txt
    python app.py

Open: http://127.0.0.1:5000

Railway:
    Procfile is included: gunicorn --bind 0.0.0.0:$PORT app:app

Recommended environment variables:
SECRET_KEY = a long random secret
ADMIN_USER = your admin username
ADMIN_PASS = a strong admin password
SITE_URL = your final HTTPS domain

SEO:
The site includes canonical URLs, hreflang for English/Arabic, robots.txt, sitemap.xml and basic Organization structured data. Google ranking cannot be guaranteed. After the domain is live, use Google Search Console and submit the sitemap.

Healthcare wording:
The website describes healthcare coordination and access to quality care. It does not promise a guaranteed cure or guaranteed "best" treatment. Treatment decisions remain with qualified healthcare professionals.
