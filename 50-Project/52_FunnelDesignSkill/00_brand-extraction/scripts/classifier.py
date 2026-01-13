#!/usr/bin/env python3
"""
Brand Image Classifier
크롤링된 이미지를 용도별로 자동 분류합니다.
"""

import argparse
import json
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from PIL import Image

# ============================================================
# 분류 규칙
# ============================================================

CATEGORIES = {
    'hero': {
        'keywords': ['hero', 'banner', 'slider', 'main', 'visual', 'cover', 'header-bg'],
        'min_width': 1200,
        'aspect_ratio': (1.5, 4.0),  # 가로형
    },
    'product': {
        'keywords': ['product', 'item', 'goods', 'thumbnail', 'card'],
        'min_width': 200,
        'aspect_ratio': (0.5, 2.0),
    },
    'icon': {
        'keywords': ['icon', 'logo', 'favicon', 'badge', 'symbol'],
        'max_width': 200,
        'max_height': 200,
    },
    'person': {
        'keywords': ['team', 'member', 'staff', 'profile', 'avatar', 'author', 'testimonial'],
        'aspect_ratio': (0.6, 1.6),  # 정방형~세로형
    },
    'background': {
        'keywords': ['bg', 'background', 'pattern', 'texture'],
        'min_width': 1000,
        'context': ['background'],
    },
    'social': {
        'keywords': ['og', 'social', 'share', 'twitter', 'facebook'],
        'context': ['social'],
    },
}

# ============================================================
# 분류기 클래스
# ============================================================

@dataclass
class ClassificationResult:
    filename: str
    original_path: str
    category: str
    confidence: str  # high, medium, low
    reasons: list

class ImageClassifier:
    def __init__(self, input_dir: str, output_dir: str, metadata_path: Optional[str] = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.metadata_path = Path(metadata_path) if metadata_path else None
        
        self.metadata = {}
        self.results: list[ClassificationResult] = []
        
        self._setup_directories()
        self._load_metadata()
    
    def _setup_directories(self):
        """분류 폴더 생성"""
        categories = list(CATEGORIES.keys()) + ['misc']
        for cat in categories:
            (self.output_dir / cat).mkdir(parents=True, exist_ok=True)
    
    def _load_metadata(self):
        """크롤러에서 생성한 메타데이터 로드"""
        if self.metadata_path and self.metadata_path.exists():
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                images = json.load(f)
                self.metadata = {img['filename']: img for img in images}
            print(f"📋 메타데이터 로드: {len(self.metadata)}개 이미지")
    
    def _get_image_dimensions(self, image_path: Path) -> tuple[int, int]:
        """이미지 크기 확인"""
        # SVG는 별도 처리
        if image_path.suffix.lower() == '.svg':
            try:
                import re
                with open(image_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # width/height 속성 추출
                w_match = re.search(r'width=["\']?(\d+)', content)
                h_match = re.search(r'height=["\']?(\d+)', content)
                w = int(w_match.group(1)) if w_match else 100
                h = int(h_match.group(1)) if h_match else 100
                return (w, h)
            except:
                return (100, 100)  # SVG 기본값
        
        try:
            with Image.open(image_path) as img:
                return img.size
        except:
            return (0, 0)
    
    def _classify_by_metadata(self, filename: str) -> tuple[Optional[str], list]:
        """메타데이터 기반 분류"""
        if filename not in self.metadata:
            return None, []
        
        meta = self.metadata[filename]
        reasons = []
        
        # context 기반 분류 (크롤러에서 추출한 페이지 위치)
        context = meta.get('context', '')
        for category, rules in CATEGORIES.items():
            if 'context' in rules and context in rules['context']:
                reasons.append(f"context: {context}")
                return category, reasons
        
        # context가 직접 카테고리와 매칭되는 경우
        if context in CATEGORIES:
            reasons.append(f"context: {context}")
            return context, reasons
        
        # alt 텍스트 기반
        alt = meta.get('alt', '').lower()
        css_class = meta.get('css_class', '').lower()
        combined_text = f"{alt} {css_class} {filename.lower()}"
        
        for category, rules in CATEGORIES.items():
            for keyword in rules.get('keywords', []):
                if keyword in combined_text:
                    reasons.append(f"keyword: {keyword}")
                    return category, reasons
        
        return None, []
    
    def _classify_by_dimensions(self, width: int, height: int) -> tuple[Optional[str], list]:
        """이미지 크기/비율 기반 분류"""
        if width == 0 or height == 0:
            return None, []
        
        aspect_ratio = width / height
        reasons = []
        
        # Icon 체크 (작은 이미지)
        icon_rules = CATEGORIES['icon']
        if width <= icon_rules.get('max_width', 200) and height <= icon_rules.get('max_height', 200):
            reasons.append(f"size: {width}x{height} (small)")
            return 'icon', reasons
        
        # Hero 체크 (큰 가로형 이미지)
        hero_rules = CATEGORIES['hero']
        if width >= hero_rules.get('min_width', 1200):
            ar_min, ar_max = hero_rules.get('aspect_ratio', (1.5, 4.0))
            if ar_min <= aspect_ratio <= ar_max:
                reasons.append(f"size: {width}x{height}, ratio: {aspect_ratio:.2f}")
                return 'hero', reasons
        
        # Background 체크 (큰 이미지)
        bg_rules = CATEGORIES['background']
        if width >= bg_rules.get('min_width', 1000) and aspect_ratio > 2.0:
            reasons.append(f"size: {width}x{height}, wide ratio")
            return 'background', reasons
        
        # Product 체크 (중간 크기)
        if 200 <= width <= 1000 and 0.5 <= aspect_ratio <= 2.0:
            reasons.append(f"size: {width}x{height}, medium")
            return 'product', reasons
        
        return None, reasons
    
    def classify_image(self, image_path: Path) -> ClassificationResult:
        """단일 이미지 분류"""
        filename = image_path.name
        reasons = []
        
        # 1차: 메타데이터 기반 분류
        category, meta_reasons = self._classify_by_metadata(filename)
        if category:
            return ClassificationResult(
                filename=filename,
                original_path=str(image_path),
                category=category,
                confidence='high',
                reasons=meta_reasons
            )
        
        # 2차: 이미지 크기 기반 분류
        width, height = self._get_image_dimensions(image_path)
        category, dim_reasons = self._classify_by_dimensions(width, height)
        if category:
            return ClassificationResult(
                filename=filename,
                original_path=str(image_path),
                category=category,
                confidence='medium',
                reasons=dim_reasons
            )
        
        # 분류 불가
        return ClassificationResult(
            filename=filename,
            original_path=str(image_path),
            category='misc',
            confidence='low',
            reasons=['no matching rules']
        )
    
    def classify_all(self):
        """모든 이미지 분류"""
        print(f"\n{'='*60}")
        print(f"🏷️ 이미지 분류 시작")
        print(f"   입력: {self.input_dir}")
        print(f"   출력: {self.output_dir}")
        print(f"{'='*60}\n")
        
        image_files = list(self.input_dir.glob('*'))
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'}
        image_files = [f for f in image_files if f.is_file() and f.suffix.lower() in valid_extensions]
        
        if not image_files:
            print(f"⚠️ 입력 폴더에 이미지가 없습니다: {self.input_dir}")
            return
        
        stats = {cat: 0 for cat in list(CATEGORIES.keys()) + ['misc']}
        
        for image_path in image_files:
            result = self.classify_image(image_path)
            self.results.append(result)
            
            # 분류된 폴더로 복사
            dest_path = self.output_dir / result.category / result.filename
            shutil.copy2(image_path, dest_path)
            
            stats[result.category] += 1
            
            # 진행상황 출력
            confidence_emoji = {'high': '🟢', 'medium': '🟡', 'low': '⚪'}
            print(f"{confidence_emoji[result.confidence]} {result.filename} → {result.category}")
            if result.reasons:
                print(f"   └─ {', '.join(result.reasons)}")
        
        self._save_results()
        self._print_summary(stats)
    
    def _save_results(self):
        """분류 결과 저장"""
        results_data = [
            {
                'filename': r.filename,
                'category': r.category,
                'confidence': r.confidence,
                'reasons': r.reasons
            }
            for r in self.results
        ]
        
        with open(self.output_dir / 'classification.json', 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    def _print_summary(self, stats: dict):
        """분류 결과 요약"""
        print(f"\n{'='*60}")
        print(f"✅ 분류 완료!")
        print(f"{'='*60}")
        
        total = sum(stats.values())
        for category, count in sorted(stats.items(), key=lambda x: -x[1]):
            if count > 0:
                pct = count / total * 100
                bar = '█' * int(pct / 5)
                print(f"  {category:12} │ {bar:20} │ {count:3} ({pct:.1f}%)")
        
        print(f"{'='*60}")
        print(f"📁 결과 저장 위치: {self.output_dir}")

# ============================================================
# 메인
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='이미지 분류기')
    parser.add_argument('--input', required=True, help='입력 디렉토리 (raw/images)')
    parser.add_argument('--output', required=True, help='출력 디렉토리 (classified)')
    parser.add_argument('--metadata', help='이미지 메타데이터 JSON 경로 (data/images.json)')
    
    args = parser.parse_args()
    
    classifier = ImageClassifier(
        input_dir=args.input,
        output_dir=args.output,
        metadata_path=args.metadata
    )
    
    classifier.classify_all()

if __name__ == '__main__':
    main()
