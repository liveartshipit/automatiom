#!/usr/bin/env python3
"""
🚀 COMPLETE Groq AI (4-5 Paragraphs) + Auto Topic Generation + Pexels → WordPress
Dynamically generates fresh topics around AI automation/productivity + 4-5 para posts
"""

import requests
import base64
import os
import json
import sys
import time
import random

print("🚀=== DAILY 4-5 PARA AI + AUTO TOPICS + IMAGES ===")

# Get environment secrets
groq_key = os.getenv('GROQ_KEY')
pexels_key = os.getenv('PEXELS_KEY')
wp_site = os.getenv('WP_SITE') or 'https://softwareinnovationlabs.gamer.gd'
wp_user = os.getenv('WP_USER')
wp_app_pass = os.getenv('WP_APP_PASS')

if not all([groq_key, pexels_key, wp_user, wp_app_pass]):
    print("❌ ERROR: Missing secrets!")
    sys.exit(1)

print(f"✅ Site: {wp_site}")

# 🎯 BASE THEMES (AI Automation & Productivity)
base_themes = [
    "AI Automation", "Productivity Hacks", "Cloud Tools", 
    "No-Code Solutions", "Developer Workflows", "Time-Saving Tech"
]

# 🔄 Generate FRESH topic daily (inspired by themes)
day_seed = int(time.time() // 86400)
random.seed(day_seed * 100 + random.randint(1, 100))  # Extra randomness
theme1, theme2 = random.sample(base_themes, 2)
topic_adjectives = ["Ultimate", "Smart", "Easy", "Fast", "Pro", "Beginner", "Hidden"]
topic_verbs = ["Guide", "Hacks", "Secrets", "Workflow", "Strategy", "Blueprint", "System"]

today_topic = f"{random.choice(topic_adjectives)} {random.choice(topic_verbs)} to {random.choice([theme1, theme2])}"
print(f"✨ Auto-generated topic: '{today_topic}'")

# 1. Generate 4-5 PARAGRAPH article (detailed + engaging)
print("🤖 Generating 4-5 paragraph article...")
groq_url = 'https://api.groq.com/openai/v1/chat/completions'
groq_headers = {'Authorization': f'Bearer {groq_key}', 'Content-Type': 'application/json'}

prompt = f"""Write a detailed, emoji-rich 4-5 paragraph blog post titled "{today_topic}" for complete beginners 👶💻.

Requirements:
• Super simple language
• Relatable examples everyone understands 
• Lots of emojis throughout ✨🚀📱
• Actionable steps (what to do first)
• Conversational tone (talking to a friend)
• 4-5 paragraphs, 400-600 words total
• End with clear call-to-action

Topic: {today_topic}"""

groq_data = {
    'model': 'llama-3.1-70b-versatile',  # Bigger model for longer content
    'messages': [{'role': 'user', 'content': prompt}],
    'max_tokens': 800,
    'temperature': 0.75  # Creative but focused
}
r_groq = requests.post(groq_url, headers=groq_headers, json=groq_data, timeout=45)
r_groq.raise_for_status()
content = r_groq.json()['choices'][0]['message']['content'].strip()
print(f"✅ Article generated ({len(content)//10}0 chars): {content[:150]}...")

# 2. Smart Pexels image search (topic-based)
print("📸 Smart image search...")
pexels_url = "https://api.pexels.com/v1/search"
pexels_headers = {"Authorization": pexels_key}
# Dynamic search based on topic
search_query = "AI automation productivity technology laptop workflow"
if "cloud" in today_topic.lower():
    search_query = "cloud computing AI technology"
elif "no-code" in today_topic.lower():
    search_query = "no code programming drag drop"

pexels_params = {"query": search_query, "per_page": 5, "orientation": "landscape"}
r_pexels = requests.get(pexels_url, headers=pexels_headers, params=pexels_params, timeout=20)
r_pexels.raise_for_status()
photos = r_pexels.json().get("photos", [])
photo_html = ""
if photos:
    best_photo = random.choice(photos[:3])  # Top quality images
    photo_url = best_photo['src']['large2x']  # High-res
    photo_alt = best_photo.get('alt', f'{today_topic} visual')
    photo_html = f'''
<div style="text-align:center;margin:25px 0;">
    <img src="{photo_url}" alt="{photo_alt}" 
         style="max-width:100%;height:auto;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.2);"/>
    <p style="text-align:center;color:#666;font-style:italic;">{photo_alt}</p>
</div>'''
    print(f"✅ Featured image: {photo_alt[:40]}...")
else:
    print("⚠️ No images found")

# 3. Create engaging title
title_words = today_topic.split()[:6]
title = f"🚀 {today_topic} – {len(content)//20} Min Read ✨"
print(f"📝 Final title: {title}")

# 4. Format rich content for WordPress
full_content = f"""
<h1 style='text-align:center;color:#2c3e50;margin-bottom:30px;'>{title}</h1>
{photo_html}
{content}
<div style='background:#f8f9fa;padding:20px;border-left:4px solid #3498db;margin:30px 0;'>
    <h3> Ready to Start?</h3>
    <p>Pick <strong>one tool</strong> from this guide and spend <strong>15 minutes today</strong> setting it up 🚀</p>
</div>
"""

# 5. Post to WordPress
print("📤 Publishing article...")
posts_url = wp_site.rstrip('/') + '/wp-json/wp/v2/posts'
token = base64.b64encode(f'{wp_user}:{wp_app_pass}'.encode()).decode()
wp_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {token}',
    'Connection': 'close',
    'User-Agent': 'GitHub-AI-Article-Poster'
}
wp_data = {
    'title': title,
    'content': full_content,
    'status': 'publish',
    'format': 'standard'
}
r_wp = requests.post(posts_url, headers=wp_headers, json=wp_data, timeout=90)
print(f"📊 WP Status: {r_wp.status_code}")

if r_wp.status_code == 201:
    post = r_wp.json()
    print(f"\n🎉 FULL ARTICLE POSTED LIVE!")
    print(f"🆔 Post ID: {post['id']}")
    print(f"🔗 Live: {post['link']}")
    print(f"📈 Words: ~{len(content)//5}")
else:
    print(f"❌ WP ERROR: {r_wp.text}")
    sys.exit(1)

print("\n✅ DAILY 4-5 PARA ARTICLE + IMAGE COMPLETE! 🚀")
