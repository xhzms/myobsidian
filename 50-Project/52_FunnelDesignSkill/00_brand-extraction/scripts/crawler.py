#!/usr/bin/env python3
"""
Brand Asset Crawler
웹사이트에서 브랜드 자산(이미지, 색상, 폰트 등)을 추출합니다.
"""

import argparse
import json
import os
import re
import time
from urllib.parse import urljoin, urlparse
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Optional
import hashlib

import requests
from bs4 import BeautifulSoup

# ============================================================
# 설정
# ============================================================

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'}
SKIP_PATTERNS = [
    'tracking', 'pixel', 'analytics', 'ad-', 'ads-', '1x1',
    'facebook.com/tr', 'google-analytics', 'googletagmanager',
    'doubleclick', 'adservice', 'beacon', 'spacer', 'blank.gif'
]

# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class ImageAsset:
    url: str
    local_path: str
    filename: str
    alt: str
    width: Optional[int]
    height: Optional[int]
    source_page: str
    context: str  # hero, content, footer 등 페이지 내 위치
    css_class: str
    file_size: int = 0

@dataclass
class PageData:
    url: str
    title: str
    images: list
    colors: list
    fonts: list
    texts: dict = None  # 텍스트 데이터 추가

# ============================================================
# 크롤러 클래스
# ============================================================

class BrandCrawler:
    def __init__(self, base_url: str, output_dir: str, depth: int = 2, delay: float = 1.0):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.depth = depth
        self.delay = delay
        
        self.visited_urls = set()
        self.downloaded_images = set()  # 중복 다운로드 방지
        self.images: list[ImageAsset] = []
        self.pages: list[PageData] = []
        self.colors = Counter()  # 빈도수 기반 색상 카운터
        self.fonts = set()
        self.texts = {  # 텍스트 데이터
            'by_page': {},        # 페이지별 그룹핑
            'common': {           # 공통 요소 (반복 발견 시)
                'footer': [],
                'navigation': [],
            },
            'unique': {           # 고유 콘텐츠 (중복 제거)
                'headlines': [],
                'cta_buttons': [],
                'hero_texts': [],
                'meta': [],
            }
        }
        
        self._setup_directories()
    
    def _setup_directories(self):
        """출력 디렉토리 구조 생성"""
        dirs = [
            self.output_dir / 'raw' / 'images',
            self.output_dir / 'classified',
            self.output_dir / 'data',
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _is_same_domain(self, url: str) -> bool:
        """동일 도메인 확인"""
        return urlparse(url).netloc == self.base_domain
    
    def _should_skip_image(self, url: str, width: int = None, height: int = None) -> bool:
        """스킵할 이미지인지 확인 (트래킹 픽셀 등)"""
        url_lower = url.lower()
        
        # URL 패턴 체크
        if any(pattern in url_lower for pattern in SKIP_PATTERNS):
            return True
        
        # 1x1 픽셀 체크 (트래킹 픽셀)
        if width is not None and height is not None:
            if width <= 2 and height <= 2:
                return True
        
        return False
    
    def _get_image_context(self, img_tag, soup) -> str:
        """이미지의 페이지 내 위치/컨텍스트 추출"""
        # 부모 요소들 확인
        parent = img_tag.parent
        for _ in range(5):  # 최대 5단계 상위까지
            if parent is None:
                break
            
            parent_class = parent.get('class', [])
            parent_id = parent.get('id', '')
            
            # 컨텍스트 키워드 매칭
            context_keywords = {
                'hero': ['hero', 'banner', 'slider', 'carousel', 'main-visual'],
                'header': ['header', 'nav', 'logo'],
                'footer': ['footer'],
                'product': ['product', 'item', 'card', 'gallery'],
                'content': ['content', 'article', 'post', 'blog'],
                'sidebar': ['sidebar', 'aside', 'widget'],
                'testimonial': ['testimonial', 'review', 'quote'],
                'team': ['team', 'member', 'staff', 'about'],
            }
            
            all_attrs = ' '.join(parent_class) + ' ' + parent_id
            all_attrs = all_attrs.lower()
            
            for context, keywords in context_keywords.items():
                if any(kw in all_attrs for kw in keywords):
                    return context
            
            parent = parent.parent
        
        return 'unknown'
    
    def _fetch_external_css(self, soup, base_url: str) -> str:
        """외부 CSS 파일 내용 가져오기"""
        css_contents = []
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if not href:
                continue
            
            css_url = urljoin(base_url, href)
            
            # 외부 CDN은 스킵 (Google Fonts 등)
            if 'fonts.googleapis.com' in css_url:
                continue
            
            try:
                response = requests.get(css_url, headers=DEFAULT_HEADERS, timeout=5)
                if response.status_code == 200:
                    css_contents.append(response.text)
                    print(f"  📄 CSS 로드: {css_url[:60]}...")
            except:
                pass
        
        return '\n'.join(css_contents)
    
    def _extract_colors(self, soup, css_text: str = '', base_url: str = '') -> Counter:
        """CSS에서 색상 추출 (빈도수 포함)"""
        colors = []
        
        # 외부 CSS 파일 가져오기
        external_css = self._fetch_external_css(soup, base_url) if base_url else ''
        
        # 인라인 스타일에서 색상 추출
        style_tags = soup.find_all('style')
        all_css = css_text + '\n'.join(tag.string or '' for tag in style_tags) + '\n' + external_css
        
        # 인라인 style 속성에서도 추출
        for elem in soup.find_all(style=True):
            all_css += '\n' + elem.get('style', '')
        
        # HEX 색상 (3자리, 6자리)
        hex_pattern = r'#(?:[0-9a-fA-F]{3}){1,2}\b'
        colors.extend(re.findall(hex_pattern, all_css))
        
        # RGB/RGBA
        rgb_pattern = r'rgba?\s*\([^)]+\)'
        colors.extend(re.findall(rgb_pattern, all_css))
        
        # HSL/HSLA
        hsl_pattern = r'hsla?\s*\([^)]+\)'
        colors.extend(re.findall(hsl_pattern, all_css))
        
        # 정규화 + 필터링
        normalized = []
        skip_colors = {'#fff', '#ffffff', '#000', '#000000'}
        
        for color in colors:
            # 소문자로 통일, 공백 제거
            c = color.lower().replace(' ', '')
            
            # 흑백/투명 제외
            if c in skip_colors or 'transparent' in c or 'rgba(0,0,0,0)' in c:
                continue
            
            # HEX 3자리 → 6자리로 확장
            if c.startswith('#') and len(c) == 4:
                c = f'#{c[1]*2}{c[2]*2}{c[3]*2}'
            
            normalized.append(c)
        
        return Counter(normalized)
    
    def _extract_fonts(self, soup, css_text: str = '') -> set:
        """CSS에서 폰트 추출"""
        fonts = set()
        
        style_tags = soup.find_all('style')
        all_css = css_text + '\n'.join(tag.string or '' for tag in style_tags)
        
        # font-family 추출
        font_pattern = r'font-family:\s*([^;]+)'
        matches = re.findall(font_pattern, all_css)
        
        for match in matches:
            # 개별 폰트 분리
            font_list = [f.strip().strip('"\'') for f in match.split(',')]
            fonts.update(font_list)
        
        # Google Fonts 링크 추출
        link_tags = soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com'))
        for link in link_tags:
            href = link.get('href', '')
            # family 파라미터 추출
            family_match = re.search(r'family=([^&]+)', href)
            if family_match:
                families = family_match.group(1).replace('+', ' ').split('|')
                fonts.update(f.split(':')[0] for f in families)
        
        return fonts
    
    def _process_texts(self) -> dict:
        """텍스트 후처리: 공통 요소 분리 + 고유 콘텐츠 추출"""
        from collections import Counter
        
        # 모든 텍스트 수집
        all_headlines = []
        all_cta = []
        all_nav = []
        all_hero = []
        all_meta = []
        
        for url, page_texts in self.texts['by_page'].items():
            for h in page_texts.get('headlines', []):
                all_headlines.append(h['text'])
            for c in page_texts.get('cta_buttons', []):
                all_cta.append(c['text'])
            all_nav.extend(page_texts.get('navigation', []))
            for h in page_texts.get('hero_texts', []):
                all_hero.append(h['text'])
            for m in page_texts.get('meta', []):
                all_meta.append(m['text'])
        
        # 빈도수 계산
        headline_counts = Counter(all_headlines)
        cta_counts = Counter(all_cta)
        nav_counts = Counter(all_nav)
        
        total_pages = len(self.texts['by_page'])
        threshold = max(2, total_pages * 0.5)  # 50% 이상 페이지에서 반복되면 공통 요소
        
        # 공통 요소 분리 (footer, navigation)
        common_headlines = {text for text, count in headline_counts.items() if count >= threshold}
        common_cta = {text for text, count in cta_counts.items() if count >= threshold}
        common_nav = {text for text, count in nav_counts.items() if count >= threshold}
        
        # 고유 콘텐츠 추출 (중복 제거)
        unique_headlines = []
        unique_cta = []
        unique_hero = []
        unique_meta = []
        
        seen_headlines = set()
        seen_cta = set()
        seen_hero = set()
        seen_meta = set()
        
        for url, page_texts in self.texts['by_page'].items():
            for h in page_texts.get('headlines', []):
                text = h['text']
                if text not in common_headlines and text not in seen_headlines:
                    seen_headlines.add(text)
                    unique_headlines.append({
                        'tag': h['tag'],
                        'text': text,
                        'page': url
                    })
            
            for c in page_texts.get('cta_buttons', []):
                text = c['text']
                if text not in common_cta and text not in seen_cta:
                    seen_cta.add(text)
                    unique_cta.append({
                        'text': text,
                        'page': url
                    })
            
            for h in page_texts.get('hero_texts', []):
                text = h['text']
                if text not in seen_hero:
                    seen_hero.add(text)
                    unique_hero.append({
                        'text': text,
                        'page': url
                    })
            
            for m in page_texts.get('meta', []):
                text = m['text']
                if text not in seen_meta:
                    seen_meta.add(text)
                    unique_meta.append(m)
        
        return {
            'common': {
                'footer': sorted(list(common_headlines | common_cta)),
                'navigation': sorted(list(common_nav)),
            },
            'unique': {
                'headlines': unique_headlines,
                'cta_buttons': unique_cta,
                'hero_texts': unique_hero,
                'meta': unique_meta,
            },
            'by_page': self.texts['by_page']  # 원본도 유지
        }
    
    def _extract_texts(self, soup, url: str) -> dict:
        """페이지에서 텍스트 추출"""
        texts = {
            'headlines': [],
            'cta_buttons': [],
            'navigation': [],
            'hero_texts': [],
            'meta': [],
        }
        
        def clean_text(text):
            """\ud14d\uc2a4\ud2b8 \uc815\ub9ac"""
            if not text:
                return ''
            return ' '.join(text.strip().split())
        
        # 1. 헤드라인 (h1, h2, h3)
        for tag in ['h1', 'h2', 'h3']:
            for elem in soup.find_all(tag):
                text = clean_text(elem.get_text())
                if text and len(text) > 2:
                    texts['headlines'].append({
                        'tag': tag,
                        'text': text,
                        'page': url
                    })
        
        # 2. CTA 버튼 (button, a.btn, a.button, input[type=submit])
        cta_selectors = [
            'button',
            'a[class*="btn"]',
            'a[class*="button"]',
            'a[class*="cta"]',
            'input[type="submit"]',
            '[class*="cta"]',
        ]
        for selector in cta_selectors:
            for elem in soup.select(selector):
                text = clean_text(elem.get_text()) or elem.get('value', '')
                if text and len(text) > 1 and len(text) < 50:
                    if text not in [item['text'] for item in texts['cta_buttons']]:
                        texts['cta_buttons'].append({
                            'text': text,
                            'page': url
                        })
        
        # 3. 네비게이션 메뉴
        nav_elements = soup.find_all(['nav', 'header'])
        for nav in nav_elements:
            for link in nav.find_all('a'):
                text = clean_text(link.get_text())
                if text and len(text) > 1 and len(text) < 30:
                    if text not in texts['navigation']:
                        texts['navigation'].append(text)
        
        # 4. 히어로 섹션 텍스트
        hero_selectors = [
            '[class*="hero"]',
            '[class*="banner"]',
            '[class*="main-visual"]',
            '[class*="jumbotron"]',
            '[class*="intro"]',
            'section:first-of-type',
        ]
        for selector in hero_selectors:
            for elem in soup.select(selector):
                # 큰 텍스트 찾기 (p, span 등)
                for p in elem.find_all(['p', 'span', 'div']):
                    text = clean_text(p.get_text())
                    if text and 20 < len(text) < 200:  # 적절한 길이
                        if text not in [item['text'] for item in texts['hero_texts']]:
                            texts['hero_texts'].append({
                                'text': text,
                                'page': url
                            })
        
        # 5. 메타 디스크립션
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            texts['meta'].append({
                'type': 'description',
                'text': clean_text(meta_desc['content']),
                'page': url
            })
        
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            texts['meta'].append({
                'type': 'og:description', 
                'text': clean_text(og_desc['content']),
                'page': url
            })
        
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            texts['meta'].append({
                'type': 'og:title',
                'text': clean_text(og_title['content']),
                'page': url
            })
        
        return texts
    
    def _download_image(self, img_url: str, source_page: str) -> Optional[str]:
        """이미지 다운로드 및 로컬 경로 반환"""
        # 중복 다운로드 방지
        if img_url in self.downloaded_images:
            return None
        
        try:
            response = requests.get(img_url, headers=DEFAULT_HEADERS, timeout=10)
            response.raise_for_status()
            
            # 파일명 생성 (URL 해시 + 원본 확장자)
            parsed = urlparse(img_url)
            ext = Path(parsed.path).suffix.lower() or '.jpg'
            if ext not in IMAGE_EXTENSIONS:
                ext = '.jpg'
            
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:12]
            filename = f"{url_hash}{ext}"
            local_path = self.output_dir / 'raw' / 'images' / filename
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            # 다운로드 후 크기 체크 (트래킹 픽셀 + 빈 파일 필터링)
            file_size = os.path.getsize(local_path)
            if file_size == 0:
                os.remove(local_path)
                print(f"  ⏭️ 빈 파일 제외: {filename}")
                return None
            
            # SVG 내용 체크 (실제 그래픽 요소가 있는지)
            if ext == '.svg':
                try:
                    with open(local_path, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    # path, rect, circle, polygon 등 실제 그래픽 요소 확인
                    if not re.search(r'<(path|rect|circle|polygon|ellipse|line|polyline|image|text|g)\s', svg_content):
                        os.remove(local_path)
                        print(f"  ⏭️ 빈 SVG 제외: {filename}")
                        return None
                except:
                    pass
            
            try:
                from PIL import Image
                with Image.open(local_path) as img:
                    w, h = img.size
                    if w <= 2 and h <= 2:
                        os.remove(local_path)
                        print(f"  ⏭️ 트래킹 픽셀 제외: {filename} ({w}x{h})")
                        return None
            except:
                pass  # PIL로 열 수 없는 파일은 통과
            
            self.downloaded_images.add(img_url)
            return str(local_path)
            
        except Exception as e:
            print(f"  ⚠️ 이미지 다운로드 실패: {img_url[:50]}... ({e})")
            return None
    
    def _crawl_page(self, url: str) -> Optional[PageData]:
        """단일 페이지 크롤링"""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        print(f"\n📄 크롤링: {url}")
        
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"  ⚠️ 페이지 접근 실패: {e}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ''
        
        # 이미지 추출
        page_images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not src:
                continue
            
            img_url = urljoin(url, src)
            
            if self._should_skip_image(img_url):
                continue
            
            # srcset에서 가장 큰 이미지 추출
            srcset = img.get('srcset')
            if srcset:
                srcset_urls = re.findall(r'(https?://[^\s]+)', srcset)
                if srcset_urls:
                    img_url = srcset_urls[-1]  # 보통 마지막이 가장 큼
            
            # 이미지 다운로드
            local_path = self._download_image(img_url, url)
            if not local_path:
                continue
            
            # 메타데이터 수집
            asset = ImageAsset(
                url=img_url,
                local_path=local_path,
                filename=Path(local_path).name,
                alt=img.get('alt', ''),
                width=int(img.get('width', 0)) if img.get('width', '').isdigit() else None,
                height=int(img.get('height', 0)) if img.get('height', '').isdigit() else None,
                source_page=url,
                context=self._get_image_context(img, soup),
                css_class=' '.join(img.get('class', [])),
                file_size=os.path.getsize(local_path)
            )
            
            page_images.append(asset)
            self.images.append(asset)
            print(f"  🖼️ {asset.filename} ({asset.context})")
        
        # CSS background-image 추출
        for elem in soup.find_all(style=re.compile(r'background.*url')):
            style = elem.get('style', '')
            bg_urls = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', style)
            for bg_url in bg_urls:
                img_url = urljoin(url, bg_url)
                if self._should_skip_image(img_url):
                    continue
                
                local_path = self._download_image(img_url, url)
                if local_path:
                    asset = ImageAsset(
                        url=img_url,
                        local_path=local_path,
                        filename=Path(local_path).name,
                        alt='',
                        width=None,
                        height=None,
                        source_page=url,
                        context='background',
                        css_class=' '.join(elem.get('class', [])),
                        file_size=os.path.getsize(local_path)
                    )
                    page_images.append(asset)
                    self.images.append(asset)
        
        # OG 이미지 추출
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = urljoin(url, og_image['content'])
            local_path = self._download_image(img_url, url)
            if local_path:
                asset = ImageAsset(
                    url=img_url,
                    local_path=local_path,
                    filename=Path(local_path).name,
                    alt='og:image',
                    width=None,
                    height=None,
                    source_page=url,
                    context='social',
                    css_class='',
                    file_size=os.path.getsize(local_path)
                )
                page_images.append(asset)
                self.images.append(asset)
        
        # 색상/폰트/텍스트 추출 (외부 CSS 포함)
        page_colors = self._extract_colors(soup, base_url=url)
        page_fonts = self._extract_fonts(soup)
        page_texts = self._extract_texts(soup, url)
        
        self.colors.update(page_colors)
        self.fonts.update(page_fonts)
        
        # 텍스트 누적 (페이지별 그룹핑)
        self.texts['by_page'][url] = page_texts
        
        page_data = PageData(
            url=url,
            title=title,
            images=[asdict(img) for img in page_images],
            colors=list(page_colors),
            fonts=list(page_fonts),
            texts=page_texts
        )
        self.pages.append(page_data)
        
        return page_data
    
    def _get_subpage_links(self, soup, current_url: str) -> list:
        """서브페이지 링크 추출"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(current_url, href)
            
            # 필터링
            if not self._is_same_domain(full_url):
                continue
            if full_url in self.visited_urls:
                continue
            if '#' in full_url:
                full_url = full_url.split('#')[0]
            if any(ext in full_url.lower() for ext in ['.pdf', '.zip', '.mp4']):
                continue
            
            links.append(full_url)
        
        return list(set(links))
    
    def crawl(self):
        """크롤링 실행"""
        print(f"\n{'='*60}")
        print(f"🚀 브랜드 자산 크롤링 시작")
        print(f"   URL: {self.base_url}")
        print(f"   깊이: {self.depth}")
        print(f"   출력: {self.output_dir}")
        print(f"{'='*60}")
        
        urls_to_crawl = [(self.base_url, 0)]
        
        while urls_to_crawl:
            url, current_depth = urls_to_crawl.pop(0)
            
            if current_depth > self.depth:
                continue
            
            try:
                response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
            except:
                continue
            
            self._crawl_page(url)
            
            # 서브페이지 추가
            if current_depth < self.depth:
                subpages = self._get_subpage_links(soup, url)
                for subpage in subpages[:20]:  # 페이지당 최대 20개
                    if subpage not in self.visited_urls:
                        urls_to_crawl.append((subpage, current_depth + 1))
            
            time.sleep(self.delay)
        
        self._save_results()
    
    def _save_results(self):
        """결과 저장"""
        data_dir = self.output_dir / 'data'
        
        # 이미지 메타데이터
        with open(data_dir / 'images.json', 'w', encoding='utf-8') as f:
            json.dump([asdict(img) for img in self.images], f, indent=2, ensure_ascii=False)
        
        # 페이지 데이터
        with open(data_dir / 'pages.json', 'w', encoding='utf-8') as f:
            json.dump([asdict(p) for p in self.pages], f, indent=2, ensure_ascii=False)
        
        # 색상 (빈도수 순 정렬)
        sorted_colors = [
            {"color": color, "count": count}
            for color, count in self.colors.most_common()
        ]
        with open(data_dir / 'colors.json', 'w', encoding='utf-8') as f:
            json.dump(sorted_colors, f, indent=2, ensure_ascii=False)
        
        # Top 10 브랜드 컨러 출력
        print(f"\n🎨 Top 10 브랜드 컨러:")
        for i, item in enumerate(sorted_colors[:10], 1):
            print(f"   {i:2}. {item['color']:20} ({item['count']}회)")
        
        # 폰트
        with open(data_dir / 'fonts.json', 'w', encoding='utf-8') as f:
            json.dump(list(self.fonts), f, indent=2)
        
        # 텍스트 (공통 요소 분리 + 고유 콘텐츠 추출)
        processed_texts = self._process_texts()
        with open(data_dir / 'texts.json', 'w', encoding='utf-8') as f:
            json.dump(processed_texts, f, indent=2, ensure_ascii=False)
        
        # 텍스트 요약 출력
        print(f"\n📝 텍스트 추출 결과:")
        print(f"   페이지: {len(self.texts['by_page'])}개")
        print(f"   공통 요소: {len(processed_texts['common']['footer'])}개")
        print(f"   고유 헤드라인: {len(processed_texts['unique']['headlines'])}개")
        print(f"   고유 CTA: {len(processed_texts['unique']['cta_buttons'])}개")
        
        # 요약 출력
        print(f"\n{'='*60}")
        print(f"✅ 크롤링 완료!")
        print(f"   페이지: {len(self.pages)}개")
        print(f"   이미지: {len(self.images)}개")
        print(f"   색상: {len(self.colors)}개")
        print(f"   폰트: {len(self.fonts)}개")
        print(f"\n📁 결과 저장 위치: {self.output_dir}")
        print(f"{'='*60}")

# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='브랜드 자산 크롤러')
    parser.add_argument('--url', required=True, help='시작 URL')
    parser.add_argument('--output', default='./output', help='출력 디렉토리')
    parser.add_argument('--depth', type=int, default=2, help='크롤링 깊이')
    parser.add_argument('--delay', type=float, default=1.0, help='요청 간 딜레이(초)')
    
    args = parser.parse_args()
    
    crawler = BrandCrawler(
        base_url=args.url,
        output_dir=args.output,
        depth=args.depth,
        delay=args.delay
    )
    
    crawler.crawl()

if __name__ == '__main__':
    main()
