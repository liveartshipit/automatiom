#!/usr/bin/env python3
"""
Groq AI → WordPress Daily Poster for GitHub Actions
Reads from environment variables (GROQ_KEY, WP_SITE, etc.)
"""

import requests
import base64
import os
import json
import sys

print("🚀=== DAILY AI WORDPRESS POSTER ===")

# Get secrets from GitHub Actions
groq_key = os.getenv('GROQ_KEY')
wp_site = os.getenv('WP_SITE') or 'https://softwareinnovationlabs.gamer.gd'
wp_user = os.getenv('WP_USER')
wp_app_pass = os.getenv('WP_APP_PASS')

if not all([groq_key, wp_user, wp_app_pass]):
    print("❌ ERROR: Missing secrets! Need GROQ_KEY, WP_USER, WP_APP_PASS")
    sys.exit(1)

print(f"✅ Site: {wp_site}")

# 1. Generate AI content with Groq
print("🤖 Generating AI content...")
groq_url = 'https://api.groq.com/openai/v1/chat/completions'
groq_headers = {
    'Authorization': f'Bearer {groq_key}',
    'Content-Type': 'application/json'
}
groq_data = {
    'model': 'llama-3.1-8b-instant',
    'messages': [{'role': 'user', 'content': 'Write a 2-3 sentence tech blog tip for developers about AI productivity'}],
    'max_tokens': 200,
    'temperature': 0.3
}
r_groq = requests.post(groq_url, headers=groq_headers, json=groq_data, timeout=30)
r_groq.raise_for_status()
content = r_groq.json()['choices'][0]['message']['content'].strip()
print(f"✅ AI Generated: {content[:80]}...")

# 2. Post to WordPress (YOUR WORKING METHOD - ID 51)
print("📤 Posting to WordPress...")
posts_url = wp_site.rstrip('/') + '/wp-json/wp/v2/posts'
token = base64.b64encode(f'{wp_user}:{wp_app_pass}'.encode()).decode()
wp_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {token}',
    'Connection': 'close',
    'User-Agent': 'GitHub-AI-Poster'
}
title = f"🤖 AI Dev Tip: {content.split('.')[0][:45]}"
wp_data = {
    'title': title,
    'content': f"<p>{content.replace('\\n', '<br>')}</p>",
    'status': 'publish'
}
r_wp = requests.post(posts_url, headers=wp_headers, json=wp_data, timeout=60)
print(f"📊 WP Status: {r_wp.status_code}")

if r_wp.status_code == 201:
    post = r_wp.json()
    print(f"🎉 SUCCESS! NEW POST LIVE!")
    print(f"🆔 ID: {post['id']}")
    print(f"🔗 URL: {post['link']}")
else:
    print(f"❌ WP ERROR: {r_wp.text}")
    sys.exit(1)

print("✅ DAILY AUTOMATION COMPLETE!")
