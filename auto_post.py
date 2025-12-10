# === 4. WP POST (YOUR WORKING BASIC AUTH + SSL DISABLE) ===
print("📤 WordPress post...")
posts_url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/posts"

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
{re.sub(r'[*`#_=>\[\]()]+', '', content).strip()}
"""

wp_data = {
    'title': title,
    'content': content_html,
    'status': 'publish',
}

# If your host’s cert is valid, switch this to verify=True
r_wp = requests.post(
    posts_url,
    headers=wp_headers,
    json=wp_data,
    timeout=60,
    verify=False  # temporary; best is verify=True with a valid cert on the server
)

print(f"📊 WP Status: {r_wp.status_code}")

# Accept any 2xx as “success-ish”
if 200 <= r_wp.status_code < 300:
    try:
        post = r_wp.json()
        link = post.get('link')
        post_id = post.get('id')
        if link and post_id:
            print(f"🎉 LIVE: {link}")
            print(f"🆔 ID: {post_id}")
            print("✅ DAILY POST COMPLETE! IMAGE AT TOP!")
            exit(0)
        else:
            print("⚠️ 2xx but unexpected JSON structure, here is the body:")
            print(r_wp.text[:500])
            # You can decide whether to fail or not here
            exit(1)
    except ValueError:
        # Not JSON – likely HTML/JS challenge or error page
        print("⚠️ 2xx but response is not JSON (likely HTML/JS from host):")
        print(r_wp.text[:500])
        exit(1)
else:
    print(f"❌ WP ERROR: {r_wp.status_code}")
    print(f"Response: {r_wp.text[:500]}")
    exit(1)
