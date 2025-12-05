#!/usr/bin/env python3
"""
🚀 DAILY 4-PARA AI → PEXELS (EXTERNAL) → WP POST (SSL FIXED)
No WP Media upload - uses Pexels direct link ✅
"""

import requests
import base64
import os
import json
import re
from urllib.parse import quote

print("🚀=== SSL-FIXED 4-PARA AI POSTER ===")

# YOUR SECRETS
groq_key = os.getenv('GROQ_KEY')
wp_site = os.getenv('WP_SITE') or 'https://softwareinnovationlabs.gamer.gd'
wp_user = os.getenv('WP_USER')
wp_app_pass = os.getenv('WP_APP_PASS')
pexels_key = os.getenv('PEXELS_KEY')

if not all([groq_key, wp_user, wp_app_pass]):
    print("❌ Missing secrets")
    exit(1)

print(f"✅ Site: {wp_site}")

# === 1. AI TOPIC ===
print("✨ AI topic...")
groq_url = 'https://api.groq.com/openai/v1/chat/completions'
groq_headers = {'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'}

groq_data = {
    'model': 'llama-3.1-8b-instant',
    'messages': [{'role': 'user', 'content': 'Catchy 8-12 word blog title about AI automation/productivity. Just title.'}],
    'max_tokens': 60,
    'temperature': 0.7
}

r_topic = requests.post(groq_url, headers=groq_headers, json=groq_data, timeout=20)
if r_topic.status_code != 200:
    topic = "5 AI Tools That 10x Developer Productivity"
else:
    topic = re.sub(r'[#*`-]+', '', r_topic.json()['choices'][0]['message']['content']).strip()[:80]

print(f"✅ Topic: '{topic}'")

# === 2. AI 4-PARA ===
print("🤖 4-para article...")
groq_data = {
    'model': 'llama-3.1-8b-instant',
    'messages': [{'role': 'user', 'content': f"""Write EXACTLY 4 short paragraphs about: {topic}

Para1: Problem + hook
Para2: Solution 1 + example  
Para3: Solution 2 + proof
Para4: Conclusion + CTA"""}],
    'max_tokens': 600,
    'temperature': 0.3
}

r_article = requests.post(groq_url, headers=groq_headers, json=groq_data, timeout=30)
r_article.raise_for_status()
content = r_article.json()['choices'][0]['message']['content'].strip()
print("✅ Article ready!")

# === 3. PEXELS IMAGE (DIRECT LINK - NO UPLOAD) ===
print("🖼️ Pexels image...")
pexels_headers = {"Authorization": pexels_key}
pexels_params = {"query": topic[:50], "per_page": 1, "orientation": "landscape"}
r_pexels = requests.get("https://api.pexels.com/v1/search", headers=pexels_headers, params=pexels_params)

if r_pexels.status_code == 200 and r_pexels.json()['photos']:
    featured_img = r_pexels.json()['photos'][0]['src']['large2x']
    print("✅ Pexels image ready!")
else:
    featured_img = f"https://source.unsplash.com/1200x675/?{quote(topic[:30])}"
    print("🔄 Unsplash fallback")

# === 4. WP POST (YOUR WORKING BASIC AUTH + SSL DISABLE) ===
print("📤 WordPress post...")
posts_url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/posts"

# YOUR WORKING BASIC AUTH
token = base64.b64encode(f'{wp_user}:{wp_app_pass}'.encode()).decode()
wp_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {token}',
    'Connection': 'close',
    'User-Agent': 'GitHub-AI-Poster'
}

title = f"🚀 {topic} - Daily AI Insights"
content_html = f"""
<figure class="wp-block-image size-large">
<img src="{featured_img}" alt="{title}" style="width:100%;height:auto;display:block;margin:0 auto 20px;">
</figure>
{content.replace('\n', '<br><br>')}
"""

wp_data = {
    'title': title,
    'content': content_html,
    'status': 'publish',
    'tags': ['AI', 'Automation', 'Productivity']
}

# SSL FIX: verify=False for your site
r_wp = requests.post(posts_url, headers=wp_headers, json=wp_data, 
                    timeout=60, verify=False)  # ✅ SSL BYPASS

print(f"📊 WP Status: {r_wp.status_code}")

if r_wp.status_code == 201:
    post = r_wp.json()
    print(f"🎉 LIVE: {post['link']}")
    print(f"🆔 ID: {post['id']}")
    print("✅ DAILY POST COMPLETE! IMAGE AT TOP!")
    exit(0)
else:
    print(f"❌ WP ERROR: {r_wp.status_code}")
    print(f"Response: {r_wp.text[:200]}")
    exit(1)
