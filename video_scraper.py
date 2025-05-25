import requests
from bs4 import BeautifulSoup
import re

def extract_media_tags(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    media = {
        'video_urls': [],
        'thumbnails': [],
        'embed_tags': []
    }

    # 1. <video> and <source> tags
    for video in soup.find_all('video'):
        # direct video src
        src = video.get('src')
        if src:
            media['video_urls'].append(src)
        # <source> children
        for source in video.find_all('source'):
            src = source.get('src')
            if src:
                media['video_urls'].append(src)

    # 2. <iframe> tags (common for embeds)
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src')
        if src and re.search(r'video|embed', src):
            media['embed_tags'].append(str(iframe))

    # 3. Open Graph meta tags for video and image
    for meta in soup.find_all('meta'):
        prop = meta.get('property', '') or meta.get('name', '')
        content = meta.get('content', '')
        if prop in ('og:video', 'og:video:url', 'og:video:secure_url') and content:
            media['video_urls'].append(content)
        if prop in ('og:image', 'twitter:image') and content:
            media['thumbnails'].append(content)

    # 4. <link> tags for thumbnails
    for link in soup.find_all('link', attrs={'rel': 'image_src'}):
        href = link.get('href')
        if href:
            media['thumbnails'].append(href)

    # Deduplicate
    for k in media:
        media[k] = list(dict.fromkeys(media[k]))

    return media


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract video URLs, thumbnails, and embed tags from a web page')
    parser.add_argument('url', help='Target web page URL')
    args = parser.parse_args()

    results = extract_media_tags(args.url)
    print('Video URLs:')
    for v in results['video_urls']:
        print('- ', v)
    print('\nThumbnails:')
    for t in results['thumbnails']:
        print('- ', t)
    print('\nEmbed Tags:')
    for e in results['embed_tags']:
        print(e)

# Usage:
#   pip install requests beautifulsoup4
#   python video_scraper.py https://example.com/page-with-video
