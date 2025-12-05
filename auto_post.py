#!/usr/bin/env python3
"""
🚀 YOUR WORKING METHOD + 4 PARA + PEXELS + FEATURED IMAGE
Uses llama-3.1-8b-instant (ACTIVE) + Basic Auth
"""

import requests
import base64
import os
import json
import re
from datetime import datetime
from urllib.parse import quote

print("🚀=== DAILY 4-PARA AI → PEXELS → WP w/ FEATURED ===")

# YOUR SECRETS (working)
groq_key = os.getenv('GROQ_KEY')
wp_site = os.getenv('WP_SITE') or 'https://softwareinnovationlabs.gamer.gd'
wp_user = os.getenv('WP_USER')
wp_app_pass = os.getenv('WP_APP_PASS')
pexels_key = os.getenv('PEXELS_KEY')

if not all([groq_key, wp_user, wp_app_pass]):
    print("❌ Missing: GROQ_KEY, WP_USER, WP_APP_PASS")
    exit(1)

print(f"✅ Site: {wp_site}")

# === 1. AI TOPIC (Your working model) ===
print("✨ AI topic...")
groq_url = 'https://api.groq.com/openai/v1/chat/completions'
groq_headers = {'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'}

groq_data = {
    'model': 'llama-3.1-8b-instant',  # ✅ YOUR WORKING MODEL
    'messages': [{'role': 'user', 'content': 'Generate ONE catchy 8-12 word blog title about AI automation/productivity tools. Just title.'}],
    'max_tokens': 60,
    'temperature': 0.7
}

r_topic = requests.post(groq_url, headers=groq_headers, json=groq_data, timeout=20)
if r_topic.status_code != 200:
    print("🔄 Fallback topic")
    topic = "5 AI Tools That 10x Developer Productivity"
else:
    topic = r_topic.json()['choices'][0]['message']['content'].strip()
    topic = re.sub(r'[#*`-]+', '', topic)[:80]

print(f"✅ Topic: '{topic}'")

# === 2. AI 4-PARA ARTICLE (Your working model) ===
print("🤖 4-para article...")
groq_data = {
    'model': 'llama-3.1-8b-instant',  # ✅ WORKING
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

# === 3. PEXELS IMAGE + WP MEDIA UPLOAD ===
print("🖼️ Pexels → WP Media...")
pexels_headers = {"Authorization": pexels_key}
pexels_params = {"query": topic, "per_page": 1, "orientation": "landscape"}
r_pexels = requests.get("https://api.pexels.com/v1/search", headers=pexels_headers, params=pexels_params)

if r_pexels.status_code == 200 and r_pexels.json()['photos']:
    img_url = r_pexels.json()['photos'][0]['src']['large2x']
else:
    img_url = f"https://source.unsplash.com/1200x675/?{quote(topic[:30])}"

# Download image
img_data = requests.get(img_url).content

# WP Basic Auth (YOUR WORKING METHOD)
token = base64.b64encode(f'{wp_user}:{wp_app_pass}'.encode()).decode()
wp_headers = {
    'Authorization': f'Basic {token}',
    'Content-Disposition': 'attachment; filename="featured.jpg"',
    'Content-Type': 'image/jpeg'
}

# UPLOAD to WP Media
media_url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/media"
r_media = requests.post(media_url, headers=wp_headers, data=img_data, timeout=40)

featured_id = None
if r_media.status_code in [200, 201]:
    featured_id = r_media.json()['id']
    print(f"✅ Featured Image ID: {featured_id}")
else:
    print("⚠️ Using external image")

# === 4. WP POST (YOUR WORKING METHOD) ===
print("📤 WordPress post...")
posts_url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/posts"
title = f"🚀 {topic} - AI Insights"

wp_data = {
    'title': title,
    'content': f'<figure class="wp-block-image size-large"><img src="" alt="{title}" class="wp-image-{featured_id}" style="width:100%;height:auto;"></figure><br>{content.replace("\n", "<br>")}',
    'status': 'publish',
    'tags': ['AI', 'Automation', 'Productivity']
}

if featured_id:
    wp_data['featured_media'] = featured_id

r_wp = requests.post(posts_url, headers=wp_headers, json=wp_data, timeout=60)

if r_wp.status_code == 201:
    post = r_wp.json()
    print(f"🎉 LIVE: {post['link']}")
    print(f"🆔 ID: {post['id']}")
    print("✅ DAILY 4-PARA POST COMPLETE!")
    exit(0)
else:
    print(f"❌ WP ERROR: {r_wp.status_code} - {r_wp.text[:200]}")
    exit(1)
