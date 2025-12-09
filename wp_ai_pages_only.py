#!/usr/bin/env python3
"""
wp_ai_pages_only.py
- Creates/updates pages: home, about, contact, privacy-policy
- Uses GROQ (GROQ_KEY) for page copy and PEXELS_KEY for hero images (direct links)
- Manual one-time run intended to be called from GitHub Actions (workflow_dispatch)
- DOES NOT create posts or change your post pipeline
"""

import os, re, json, base64, requests
from urllib.parse import quote

# ENV / CONFIG
GROQ_KEY = os.getenv("GROQ_KEY")
PEXELS_KEY = os.getenv("PEXELS_KEY")
WP_SITE = os.getenv("WP_SITE", "https://softwareinnovationlabs.gamer.gd").rstrip('/')
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")

VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() in ("1","true","yes")
TIMEOUT = int(os.getenv("TIMEOUT","60"))

if not all([GROQ_KEY, WP_USER, WP_APP_PASS, WP_SITE]):
    print("❌ Missing required env vars: GROQ_KEY, WP_USER, WP_APP_PASS, WP_SITE")
    raise SystemExit(1)

PAGES = {
    "home": "AI Productivity & Automation",
    "about": "About Us",
    "contact": "Contact Us",
    "privacy-policy": "Privacy Policy"
}

# ---- Helpers ----
def groq_chat(prompt, model="llama-3.1-8b-instant", max_tokens=600, temp=0.18):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages":[{"role":"user","content":prompt}], "max_tokens": max_tokens, "temperature": temp}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content'].strip()

def clean_text(s):
    if not s:
        return ""
    return re.sub(r'[#*`]{1,}', '', s).strip()

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": PEXELS_KEY}
        params = {"query": query[:50], "per_page": 1, "orientation": "landscape"}
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 200:
            j = r.json()
            photos = j.get("photos", [])
            if photos:
                return photos[0]['src'].get('large2x') or photos[0]['src'].get('large')
    except Exception:
        pass
    return None

def wp_headers():
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    return {"Content-Type":"application/json","Authorization":f"Basic {token}","User-Agent":"WP-AI-PagesOnly/1.0"}

def find_page(slug):
    url = f"{WP_SITE}/wp-json/wp/v2/pages"
    r = requests.get(url, headers=wp_headers(), params={"slug":slug}, timeout=TIMEOUT, verify=VERIFY_SSL)
    if r.status_code == 200:
        arr = r.json()
        if arr:
            return arr[0]
    return None

def create_page(payload):
    url = f"{WP_SITE}/wp-json/wp/v2/pages"
    return requests.post(url, headers=wp_headers(), json=payload, timeout=TIMEOUT, verify=VERIFY_SSL)

def update_page(page_id, payload):
    url = f"{WP_SITE}/wp-json/wp/v2/pages/{page_id}"
    return requests.post(url, headers=wp_headers(), json=payload, timeout=TIMEOUT, verify=VERIFY_SSL)

# ---- Templates ----
def page_template(title, hero_img, intro_html, cards_html):
    return f"""
    <section style="padding:28px 12px;text-align:center;background:linear-gradient(90deg,#fff,#f7fbff);">
      <div style="max-width:1100px;margin:0 auto;">
        <h1 style="font-size:2.1rem;margin-bottom:6px;">{clean_text(title)}</h1>
        <p style="color:#475569;margin-bottom:12px;">Actionable AI guides & automation recipes.</p>
        <img src="{hero_img}" alt="{clean_text(title)}" style="width:100%;max-height:420px;object-fit:cover;border-radius:10px;">
      </div>
    </section>
    <main style="max-width:1100px;margin:20px auto;padding:0 12px;">
      {intro_html}
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:16px;">
        {cards_html}
      </div>
    </main>
    """

def card_html(h,t,link="#"):
    return f"<div style='padding:12px;border-radius:8px;background:#fff;border:1px solid #eef2f6;'><h4>{clean_text(h)}</h4><p>{clean_text(t)}</p><a href='{link}'>Read →</a></div>"

# ---- Generate page content ----
def generate_page_content(slug,title):
    prompts = {
        "home": f"Write a friendly homepage intro for '{title}'. 3 short paragraphs and 3 short feature lines with emoji. CTA to blog and contact. Plain text.",
        "about": "Write an About Us page: mission (2 short paragraphs), short team sentence, and 3 values as short lines. End with CTA to contact.",
        "contact": "Write a Contact page: short intro, 3 contact methods (email/form/social), and 2 quick FAQs.",
        "privacy-policy": ("Write a concise, plain-language Privacy Policy summary suitable for AdSense. "
                           "Cover: what we collect (contact form, email, cookies, analytics), why, third-party services used (Pexels for images, Groq/OpenAI for content), "
                           "images served externally, cookies & analytics, advertising, retention, how to opt-out/request deletion, and contact for privacy.")
    }
    prompt = prompts.get(slug, f"Write a short page titled '{title}' in friendly language.")
    try:
        raw = groq_chat(prompt, max_tokens=700, temp=0.18)
    except Exception as e:
        raw = f"Content generation failed: {e}"
    clean = clean_text(raw)
    paras = [p.strip() for p in re.split(r'\n\s*\n', clean) if p.strip()]
    intro = "<p>" + "</p><p>".join(paras[:2]) + "</p>" if paras else "<p>Welcome.</p>"
    cards = []
    for i,p in enumerate(paras[2:6]):
        cards.append(card_html(f"Point {i+1}", p))
    if not cards:
        cards = [card_html("Why us","Practical automation guides."), card_html("Get started","Contact us to build pipelines.")]
    hero_img = fetch_pexels_image(title) or f"https://source.unsplash.com/1200x675/?{quote(title)}"
    return page_template(title, hero_img, intro, "\n".join(cards))

# ---- Main ----
def main():
    results = {}
    for slug,title in PAGES.items():
        print("Processing:",slug)
        html = generate_page_content(slug,title)
        payload = {"title":title,"content":html,"status":"publish","slug":slug}
        existing = find_page(slug)
        if existing:
            pid = existing.get("id")
            r = update_page(pid,payload)
            if r.status_code in (200,201):
                results[slug] = {"status":"updated","link":r.json().get("link")}
                print(" Updated:",title)
            else:
                results[slug] = {"status":"error","code":r.status_code,"text":r.text[:200]}
                print(" Update error:",r.status_code)
        else:
            r = create_page(payload)
            if r.status_code in (200,201):
                results[slug] = {"status":"created","link":r.json().get("link")}
                print(" Created:",title)
            else:
                results[slug] = {"status":"error","code":r.status_code,"text":r.text[:200]}
                print(" Create error:",r.status_code)
    print("\nSummary:")
    print(json.dumps(results,indent=2))
    print("Done.")

if __name__ == "__main__":
    main()
