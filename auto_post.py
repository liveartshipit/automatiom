#!/usr/bin/env python3
"""
🚀 AI 4-PARA → PEXELS → WP MEDIA UPLOAD → AUTO POST w/ FEATURED IMAGE
https://softwareinnovationlabs.gamer.gd
"""

import os
import requests
import json
import re
from datetime import datetime
from urllib.parse import quote

# === YOUR SECRETS ===
SITE_URL = "https://softwareinnovationlabs.gamer.gd"
WP_USERNAME = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_APP_PASS')
GROQ_API_KEY = os.getenv('GROQ_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_KEY')

print("🚀=== FULL AI PIPELINE LIVE ===")

def get_ai_topic():
    """AI generates fresh topic"""
    print("✨ AI topic generation...")
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": "Generate ONE catchy 8-12 word blog title about 2025 AI automation/productivity tools/trends. Clickable + SEO."},
                     {"role": "user", "content": "Today's trending topic:"}],
        "temperature": 0.8, "max_tokens": 80
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        topic = re.sub(r'[#*`-]+', '', r.json()['choices'][0]['message']['content']).strip()
        print(f"✅ Topic: '{topic}'")
        return topic
    except:
        return "5 AI Tools That Automate 80% of Your Workday"

def groq_4_paras(topic):
    """Groq: EXACTLY 4 paragraphs"""
    print("🤖 Writing 4-para article...")
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "system", "content": "Write EXACTLY 4 paragraphs (120 words each): 1.HOOK+problem 2.Solution1+example 3.Solution2+proof 4.Conclusion+CTA. Tech blog style."},
                     {"role": "user", "content": topic}],
        "temperature": 0.7, "max_tokens": 900
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content'].strip()

def get_and_upload_image(topic):
    """Pexels → Download → UPLOAD to WP Media Library"""
    print("🖼️ Pexels → WP Media...")
    
    # 1. Get Pexels image
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": topic, "per_page": 1, "orientation": "landscape"}
    r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
    
    if r.status_code == 200 and r.json()['photos']:
        img_url = r.json()['photos'][0]['src']['large2x']
        print("✅ Pexels image found")
    else:
        img_url = f"https://source.unsplash.com/1200x675/?{quote(topic)}"
        print("🔄 Unsplash fallback")
    
    # 2. Download image
    img_response = requests.get(img_url, timeout=20)
    img_response.raise_for_status()
    
    # 3. UPLOAD to WP Media (/wp/v2/media)
    wp_auth = (WP_USERNAME, WP_PASSWORD)
    media_headers = {
        'Content-Disposition': 'attachment; filename="ai-blog-image.jpg"',
        'Content-Type': 'image/jpeg'
    }
    
    media_response = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/media",
        auth=wp_auth,
        headers=media_headers,
        data=img_response.content,
        timeout=30
    )
    
    if media_response.status_code in [200, 201]:
        media_id = media_response.json()['id']
        print(f"✅ Image UPLOADED! Media ID: {media_id}")
        return media_id
    else:
        print(f"❌ Media upload failed: {media_response.status_code}")
        return None

def create_wp_post(title, content, featured_image_id):
    """Create post with featured image"""
    print("📤 Creating WP post...")
    
    auth = (WP_USERNAME, WP_PASSWORD)
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50]
    
    post_data = {
        "title": title,
        "content": f'<figure class="wp-block-image"><img src="" alt="{title}" class="wp-image-{featured_image_id}" style="width:100%;height:auto;"></figure><br>{content}',
        "status": "publish",
        "slug": slug,
        "tags": ["AI", "Automation", "Productivity"],
        "featured_media": featured_image_id  # 🎯 SETS FEATURED IMAGE
    }
    
    r = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/posts",
        json=post_data,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if r.status_code in [200, 201]:
        post = r.json()
        post_url = f"{SITE_URL}/?p={post['id']}"
        print(f"🎉 LIVE: {post_url}")
        return True
    print(f"❌ Post failed: {r.status_code} - {r.text[:100]}")
    return False

# === 🚀 MAIN EXECUTION ===
try:
    topic = get_ai_topic()
    title = f"🚀 {topic} - AI Automation Insights"
    
    print(f"\n📝 TITLE: {title}")
    article = groq_4_paras(topic)
    media_id = get_and_upload_image(topic)
    
    if media_id:
        success = create_wp_post(title, article, media_id)
        print("🎊" if success else "❌")
        exit(0 if success else 1)
    else:
        print("❌ No image, aborting")
        exit(1)

except Exception as e:
    print(f"💥 ERROR: {e}")
    exit(1)
