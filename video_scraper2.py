# video_scraper.py

import requests
from bs4 import BeautifulSoup
import re

def extract_mp4_urls(url):
    """HTML 中の .mp4 URL をすべて返す"""
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    return list(dict.fromkeys(
        re.findall(r'https?://[^"\']+?\.mp4', r.text)
    ))

def extract_media_tags(url):
    """動画(.mp4)、サムネ(og:image)、埋め込み(iframe) を抽出"""
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

    media = {
        'video_urls': extract_mp4_urls(url),
        'thumbnails': [],
        'embed_tags': []
    }

    # サムネイル（og:image / twitter:image）
    for meta in soup.find_all('meta', attrs={'property': ['og:image','twitter:image']}):
        if meta.get('content'):
            media['thumbnails'].append(meta['content'])

    # iframe 埋め込みタグ
    for iframe in soup.find_all('iframe'):
        media['embed_tags'].append(str(iframe))

    # 重複を除去
    media['thumbnails'] = list(dict.fromkeys(media['thumbnails']))
    media['embed_tags']  = list(dict.fromkeys(media['embed_tags']))

    return media

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract video URLs, thumbnails, and embed tags from a web page'
    )
    parser.add_argument('url', help='Target web page URL')
    args = parser.parse_args()

    results = extract_media_tags(args.url)

    print('Video URLs:')
    for v in results['video_urls']:
        print('-', v)
    print('\nThumbnails:')
    for t in results['thumbnails']:
        print('-', t)
    print('\nEmbed Tags:')
    for e in results['embed_tags']:
        print(e)
