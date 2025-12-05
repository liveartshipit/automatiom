#!/usr/bin/env python3
"""
🚀 FIXED: AI 4-PARA → PEXELS → WP w/ PROPER GROQ PAYLOAD
"""

import os
import requests
import json
import re
from datetime import datetime
from urllib.parse import quote

SITE_URL = "https://softwareinnovationlabs.gamer.gd"
WP_USERNAME = os.getenv('WP_USER')
WP_PASSWORD = os.getenv('WP_APP_PASS')
GROQ_API_KEY = os.getenv('GROQ_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_KEY')

print("🚀=== BULLETPROOF AI PIPELINE ===")

def get_ai_topic():
    """✅ SAFE topic generation"""
    print("✨ AI topic...")
    payload = {
        "model": "llama-3.1-70b-versatile",  # ✅ FIXED MODEL
        "messages": [
            {"role": "user", "content": "Generate ONE catchy blog title (8-12 words) about 2025 AI automation/productivity. Just the title."}
        ],
        "temperature": 0.8,
        "max_tokens": 60  # ✅ SHORTENED
    }
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=20)
        print(f"Debug: Status {r.status_code}")
        if r.status_code != 200:
            print(f"❌ Groq Error: {r.text}")
            raise Exception("API failed")
        topic = r.json()['choices'][0]['message']['content'].strip()
        topic = re.sub(r'[#*`-]+', '', topic).strip()[:80]
        print(f"✅ Topic: '{topic}'")
        return topic
    except:
        print("🔄 Fallback topic")
        return "5 AI Tools That 10x Your Daily Productivity"

def groq_4_paras(topic):
    """✅ FIXED 4-para generation"""
    print("🤖 4-para article...")
    payload = {
        "model": "llama-3.1-70b-versatile",  # ✅ PROVEN MODEL
        "messages": [
            {"role": "user", "content": f"""Write EXACTLY 4 paragraphs about: {topic}

Para1: Hook + problem (120 words)
Para2: Solution 1 + example (120 words)  
Para3: Solution 2 + proof (120 words)
Para4: Conclusion + CTA (120 words)

Tech blog style ONLY."""}
        ],
        "temperature": 0.7,
        "max_tokens": 700  # ✅ REDUCED from 900
    }
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
    print(f"Debug: Status {r.status_code}")
    
    if r.status_code != 200:
        print(f"❌ FULL ERROR: {r.text}")
        raise Exception(f"Groq failed: {r.status_code}")
    
    return r.json()['choices'][0]['message']['content'].strip()

def get_and_upload_image(topic):
    """Pexels → WP Media Library"""
    print("🖼️ Image pipeline...")
    
    # Pexels
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": topic[:50], "per_page": 1, "orientation": "landscape"}
    r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    
    img_url = (r.json()['photos'][0]['src']['large2x'] if r.status_code == 200 and r.json()['photos'] 
               else f"https://source.unsplash.com/1200x675/?{quote(topic[:30])}")
    
    # Download
    img_data = requests.get(img_url).content
    
    # WP Media Upload
    wp_auth = (WP_USERNAME, WP_PASSWORD)
    files = {'file': ('featured.jpg', img_data, 'image/jpeg')}
    
    r_media = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/media",
        auth=wp_auth,
        files=files
    )
    
    if r_media.status_code in [200, 201]:
        media_id = r_media.json()['id']
        print(f"✅ Media ID: {media_id}")
        return media_id
    print(f"⚠️ Media failed, using external: {img_url}")
    return None

def create_wp_post(title, content, media_id=None):
    """✅ WP Post w/ Featured Image"""
    auth = (WP_USERNAME, WP_PASSWORD)
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50]
    
    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "slug": slug,
        "tags": ["AI", "Automation", "Productivity"]
    }
    if media_id:
        post_data["featured_media"] = media_id
    
    r = requests.post(f"{SITE_URL}/wp-json/wp/v2/posts", json=post_data, auth=auth)
    
    if r.status_code in [200, 201]:
        post = r.json()
        print(f"🎉 LIVE: {SITE_URL}/?p={post['id']}")
        return True
    print(f"❌ WP: {r.status_code} - {r.text[:100]}")
    return False

# === MAIN ===
try:
    topic = get_ai_topic()
    title = f"🚀 {topic}"
    print(f"\n📝 {title}")
    
    article = groq_4_paras(topic)
    media_id = get_and_upload_image(topic)
    success = create_wp_post(title, article, media_id)
    
    print("🎊 COMPLETE!" if success else "❌ FAILED")
    exit(0 if success else 1)

except Exception as e:
    print(f"💥 {e}")
    exit(1)
