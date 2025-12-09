#!/usr/bin/env python3
"""
🚀 DAILY AI PAGES BUILDER → GROQ CONTENT → PEXELS HERO → WP PAGES (SSL FIXED)
Creates/updates: home, about, contact, privacy-policy with beautiful layouts
"""

import requests
import base64
import os
import json
import re
from urllib.parse import quote

print("🚀=== AI PAGES BUILDER (HOME/ABOUT/CONTACT/PRIVACY) ===")

# SECRETS
groq_key = os.getenv('GROQ_KEY')
wp_site = os.getenv('WP_SITE', 'https://softwareinnovationlabs.gamer.gd')
wp_user = os.getenv('WP_USER')
wp_app_pass = os.getenv('WP_APP_PASS')
pexels_key = os.getenv('PEXELS_KEY')

if not all([groq_key, wp_user, wp_app_pass]):
    print("❌ Missing secrets: GROQ_KEY, WP_USER, WP_APP_PASS")
    exit(1)

print(f"✅ Site: {wp_site}")

# WP SETUP (YOUR WORKING AUTH)
token = base64.b64encode(f'{wp_user}:{wp_app_pass}'.encode()).decode()
wp_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {token}',
    'Connection': 'close',
    'User-Agent': 'AI-Pages-Builder/1.0'
}

def groq_chat(prompt, max_tokens=800, temp=0.2):
    groq_url = 'https://api.groq.com/openai/v1/chat/completions'
    groq_data = {
        'model': 'llama-3.1-8b-instant',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': temp
    }
    r = requests.post(groq_url, headers={'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'}, json=groq_data, timeout=30)
    r.raise_for_status()
    return re.sub(r'[#*`_-]+', '', r.json()['choices'][0]['message']['content']).strip()

def get_pexels_image(query):
    if not pexels_key: return f"https://source.unsplash.com/1200x675/?{quote(query)}"
    try:
        r = requests.get("https://api.pexels.com/v1/search", 
                        headers={"Authorization": pexels_key}, 
                        params={"query": query[:50], "per_page": 1, "orientation": "landscape"}, 
                        timeout=15)
        if r.status_code == 200 and r.json()['photos']:
            return r.json()['photos'][0]['src']['large2x']
    except: pass
    return f"https://source.unsplash.com/1200x675/?{quote(query)}"

def find_page(slug):
    url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/pages?slug={slug}"
    r = requests.get(url, headers=wp_headers, timeout=60, verify=False)
    if r.status_code == 200 and r.json():
        return r.json()[0]
    return None

def save_page(slug, title, content_html):
    url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/pages"
    data = {'title': title, 'content': content_html, 'status': 'publish', 'slug': slug}
    
    existing = find_page(slug)
    if existing:
        url = f"{url}/{existing['id']}"
        method = 'update'
    else:
        method = 'create'
    
    r = requests.post(url, headers=wp_headers, json=data, timeout=60, verify=False)
    print(f"  📄 {title}: {method} → {r.status_code}")
    return r.status_code in (200, 201)

# === PAGE TEMPLATES ===
PAGES = {
    "home": {
        "title": "AI Productivity & Automation",
        "prompt": """Homepage for AI Productivity site. EXACTLY:
1. Hero intro: "Daily AI automation guides + human oversight" (2 sentences)
2. 4 benefits as short bullet lines with emojis
3. CTA: "Read daily posts → Contact us →"
Just plain text paragraphs.""",
        "hero_query": "AI productivity automation"
    },
    "about": {
        "title": "About AI Productivity Lab",
        "prompt": """About page for AI automation site:
1. Mission: Daily AI guides with human quality check (2 short paras)
2. "Small team of AI engineers + content experts"
3. 3 core values as short lines with emojis
4. CTA: "Get your automation → Contact now"
Plain text only.""",
        "hero_query": "AI team collaboration"
    },
    "contact": {
        "title": "Contact AI Productivity Lab",
        "prompt": """Contact page content:
1. "Get custom AI automation help" intro
2. 3 contact options: email, form, Twitter/Discord
3. 2 FAQs: "How fast?" "Free consult?"
4. "Let's automate your workflow →" CTA
Short friendly paragraphs.""",
        "hero_query": "contact AI automation"
    },
    "privacy-policy": {
        "title": "Privacy Policy",
        "prompt": """AdSense-compliant Privacy Policy for AI blog:
- Collect: contact forms, cookies, analytics, email subs
- Purpose: improve site, personalization, ads
- Third-parties: Pexels (images), Groq (AI content), Google Analytics/Ads
- No selling data, opt-out options, retention 12mo
- Contact for deletion requests
Plain professional paragraphs. Friendly tone.""",
        "hero_query": "privacy policy data protection"
    }
}

# === BUILD & SAVE PAGES ===
results = {}
for slug, config in PAGES.items():
    print(f"\n🔨 Building {config['title']}...")
    
    # Generate content
    content = groq_chat(config['prompt'])
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
    
    # Hero image
    hero_img = get_pexels_image(config['hero_query'])
    print(f"  🖼️  {hero_img[:60]}...")
    
    # Feature cards (split remaining content)
    cards_html = ""
    for i, para in enumerate(paragraphs[1:5], 1):
        cards_html += f"""
        <div style="padding:20px;border-radius:12px;background:linear-gradient(135deg,#f8fafc,#e2e8f0);border:1px solid #e2e8f0;margin:8px 0;">
          <h4 style="color:#1e293b;margin:0 0 8px 0;">✨ Point {i}</h4>
          <p style="color:#475569;line-height:1.6;margin:0;">{para[:150]}...</p>
          <a href="/blog" style="color:#3b82f6;font-weight:500;">Read more →</a>
        </div>"""
    
    if not cards_html:
        cards_html = """
        <div style="padding:20px;border-radius:12px;background:linear-gradient(135deg,#f8fafc,#e2e8f0);border:1px solid #e2e8f0;margin:8px 0;">
          <h4 style="color:#1e293b;">🚀 Daily AI Insights</h4>
          <p style="color:#475569;">Fresh automation guides every day</p>
        </div>"""
    
    # Full page HTML (BEAUTIFUL LAYOUT)
    page_html = f"""
    <section style="padding:40px 20px;text-align:center;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;">
      <div style="max-width:1200px;margin:0 auto;">
        <h1 style="font-size:3rem;font-weight:800;margin:0 0 16px 0;text-shadow:0 2px 4px rgba(0,0,0,0.3);">{config['title']}</h1>
        <p style="font-size:1.2rem;max-width:600px;margin:0 auto 24px;line-height:1.6;">{paragraphs[0][:120]}...</p>
        <img src="{hero_img}" alt="{config['title']}" style="width:100%;max-height:400px;object-fit:cover;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.3);">
      </div>
    </section>
    
    <main style="max-width:1200px;margin:0 auto;padding:40px 20px;">
      <div style="max-width:800px;margin:0 auto 40px;">
        <p style="font-size:1.1rem;color:#475569;line-height:1.7;">{paragraphs[0] if len(paragraphs)>1 else 'Daily AI productivity guides with human oversight.'}</p>
      </div>
      {cards_html}
      
      <div style="text-align:center;margin:40px 0;padding:24px;background:#f8fafc;border-radius:16px;border:2px solid #e2e8f0;">
        <h3 style="color:#1e293b;">Ready to Automate?</h3>
        <p style="color:#64748b;">Daily posts • Custom solutions • Free consult</p>
        <a href="/contact" style="display:inline-block;padding:12px 32px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;text-decoration:none;border-radius:50px;font-weight:600;">Get Started →</a>
      </div>
    </main>
    """
    
    # Save to WP
    success = save_page(slug, config['title'], page_html)
    results[slug] = {"status": "success" if success else "failed", "title": config['title']}
    
    print("✅" if success else "❌", config['title'])

print("\n🎉 SUMMARY:")
print(json.dumps(results, indent=2))
print("🚀 PAGES READY! Visit your site.")
