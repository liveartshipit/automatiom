#!/usr/bin/env python3
"""
🚀 Daily 4-5 Para AI Articles + Images Automation
Fixed version for GitHub Actions with proper error handling
"""

import os
import requests
import json
import time
from datetime import datetime
import re

# Configuration
SITE_URL = "***"  # Your WordPress site
WP_USERNAME = os.getenv('WP_USERNAME')
WP_PASSWORD = os.getenv('WP_PASSWORD')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Validate required env vars
required_vars = ['WP_USERNAME', 'WP_PASSWORD', 'GROQ_API_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    exit(1)

print("🚀=== DAILY 4-5 PARA AI + AUTO TOPICS + IMAGES ===")
print(f"✅ Site: {SITE_URL}")
print("✨ Auto-generated topic: 'Hidden Secrets to Time-Saving Tech'")

def generate_ai_article(topic):
    """Generate 4-5 paragraph article using Groq API"""
    print("🤖 Generating 4-5 paragraph article...")
    
    system_prompt = """You are an expert content writer. Write a high-quality, engaging 4-5 paragraph article (400-600 words) on the given topic. 
    Structure: 
    1. Compelling intro with hook
    2-4. 3 detailed body paragraphs with practical tips/examples
    5. Strong conclusion with call-to-action
    Use natural conversational tone, active voice, and SEO-friendly keywords."""
    
    user_prompt = f"Write a complete 4-5 paragraph article about: '{topic}'\n\nMake it ready to publish directly."
    
    payload = {
        "model": "llama3-70b-8192",  # Valid Groq model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1200,
        "top_p": 0.9
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        article = result['choices'][0]['message']['content'].strip()
        return article
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Groq API HTTP Error: {e}")
        print(f"Response: {response.text[:500]}...")
        raise
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        raise

def generate_image_prompt(topic):
    """Generate DALL-E image prompt"""
    return f"Professional blog header image for article '{topic}'. Modern, vibrant, high-quality, 16:9 aspect ratio, tech theme."

def generate_image(prompt):
    """Generate image using free/low-cost API (fallback to placeholder)"""
    print("🖼️ Generating featured image...")
    
    # Option 1: Use your DeAPI key (from user history)
    deapi_key = os.getenv('DEAPI_KEY')
    if deapi_key:
        try:
            payload = {
                "prompt": prompt,
                "model": "gamercoin",
                "width": 1200,
                "height": 675
            }
            headers = {"Authorization": f"Bearer {deapi_key}"}
            response = requests.post("https://api.deapi.ai/v1/images/generations", 
                                   json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()['data'][0]['url']
        except:
            pass
    
    # Fallback: Free placeholder service
    print("⚠️ Using placeholder image")
    return "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&h=675&q=80"

def publish_to_wordpress(title, content, image_url):
    """Publish article to WordPress"""
    print("📤 Publishing to WordPress...")
    
    # WordPress REST API Auth
    auth = (WP_USERNAME, WP_PASSWORD)
    
    # Post data
    post_data = {
        "title": title,
        "content": f'<img src="{image_url}" alt="{title}" style="width:100%;height:auto;"><br><br>{content}',
        "status": "publish",
        "slug": re.sub(r'[^\w\s-]', '', title.lower()).strip().replace(' ', '-'),
        "categories": [1],  # Default category ID
        "tags": ["AI", "automation", "tech"],
        "featured_media": 0  # Set featured image separately if needed
    }
    
    response = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/posts",
        json=post_data,
        auth=auth,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Published: {SITE_URL}/?p={result['id']}")
        return True
    else:
        print(f"❌ WordPress Error {response.status_code}: {response.text[:200]}")
        return False

# Main execution
try:
    topic = "Hidden Secrets to Time-Saving Tech"
    title = f"🔥 {topic}: Transform Your Productivity Today!"
    
    # Step 1: Generate article
    article_content = generate_ai_article(topic)
    
    # Step 2: Generate image
    image_prompt = generate_image_prompt(topic)
    featured_image = generate_image(image_prompt)
    
    # Step 3: Publish
    success = publish_to_wordpress(title, article_content, featured_image)
    
    if success:
        print("🎉 Daily article published successfully!")
        exit(0)
    else:
        print("❌ Publishing failed")
        exit(1)
        
except KeyboardInterrupt:
    print("\n⏹️ Interrupted by user")
    exit(130)
except Exception as e:
    print(f"💥 Unexpected error: {e}")
    exit(1)
