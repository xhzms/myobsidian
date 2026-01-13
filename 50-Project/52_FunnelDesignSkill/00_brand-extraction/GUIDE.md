---
name: funnel-design-brand-extraction
---

# Brand Extraction Guide

웹사이트에서 브랜드 자산(이미지, 텍스트, 폰트, 색상)을 추출하고, 용도별로 분류하여 마케팅/디자인 작업에 활용할 수 있는 형태로 정리합니다.

## 목적

- 클라이언트/경쟁사 브랜드 자산 수집
- 이미지 자산을 용도별로 자동 분류
- **주요 애셋 리스트 생성** (로컬 파일 경로 매핑)
- **브랜드 분석 리포트 자동 생성**
- 프로젝트 세팅 전 브랜드 분석 자료 확보

## 핵심 원칙

- **코드 기반 실행**: 크롤링/다운로드/분류는 Python 스크립트로 처리
- **컨텍스트 효율**: Claude는 분석/판단만, 반복 작업은 코드로
- **이미지 우선**: 시각 자산이 가장 중요한 추출 대상
- **옵시디언 호환**: 모든 링크는 상대경로로 생성

---

## 워크플로우

```
[입력] URL 제공
    ↓
[Step 1] 크롤러 실행 → 페이지 탐색 + 자산 다운로드
    ↓
[Step 2] 분류기 실행 → 이미지 용도별 폴더링
    ↓
[Step 3] 애셋 리스트 생성 → brand-assets.md (로컬 경로 매핑)
    ↓
[Step 4] 브랜드 분석 → brand-analysis.md (컬러, 폰트, 카피 분석)
    ↓
[출력] output 폴더 → 프로젝트 세팅에 활용
```

---

## 출력 폴더 구조

```
output/{project-name}/
├── data/
│   ├── texts.json          # 추출된 텍스트 (by_page, common, unique)
│   ├── colors.json         # 추출된 색상 (빈도수 순)
│   ├── fonts.json          # 추출된 폰트
│   ├── images.json         # 이미지 메타데이터
│   └── pages.json          # 크롤링된 페이지 목록
├── raw/
│   └── images/             # 원본 다운로드 (해시 파일명)
├── classified/             # 분류된 이미지
│   ├── hero/
│   ├── product/
│   ├── icon/
│   ├── person/
│   ├── background/
│   ├── social/
│   └── misc/
├── brand-assets.md         # 주요 애셋 리스트 (로컬 경로)
└── brand-analysis.md       # 브랜드 분석 리포트
```

---

## 이미지 분류 체계

| 폴더명 | 용도 | 판단 기준 |
|--------|------|-----------|
| `hero/` | 메인 배너, 히어로 이미지 | 가로형, 대형 (1200px+) |
| `product/` | 제품/서비스/리뷰 이미지 | 정방형~가로형, 중형 |
| `icon/` | 아이콘, 로고, UI 요소 | 소형 (200px 이하), SVG/PNG |
| `person/` | 인물, 팀, 고객 사진 | 얼굴 감지, 프로필 형태 |
| `background/` | 배경, 패턴, 텍스처 | CSS background, 대형 |
| `social/` | SNS 이미지, OG 이미지 | meta 태그 추출 |
| `misc/` | 분류 불가 | 기타 |

---

## 브랜드 분석 리포트 (brand-analysis.md)

### 포함 항목

1. **브랜드 아이덴티티**: 슬로건, 포지셔닝, 타겟 추정
2. **컬러 시스템**: 상위 10개 색상 + 용도 추정
3. **타이포그래피**: 폰트 목록 + 용도
4. **핵심 카피**: 헤드라인, CTA, 슬로건
5. **퍼널 구조 분석**: 리드마그넷, CTA 패턴, 신뢰 요소

---

## 스크립트 사용법

### 1. 크롤러 실행

```bash
python crawler.py --url "https://example.com" --output "./output/brand-name" --depth 2
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--url` | 시작 URL | (필수) |
| `--output` | 저장 경로 | ./output |
| `--depth` | 크롤링 깊이 | 2 |

### 2. 분류기 실행

```bash
python classifier.py --input "./output/brand-name/raw" --output "./output/brand-name/classified"
```

### 3. Claude에게 요청

```
"images.json을 분석해서 brand-assets.md를 만들어줘."
"texts.json, colors.json을 분석해서 brand-analysis.md를 만들어줘."
```

---

## Claude 역할

| 역할 | 설명 |
|------|------|
| 스크립트 생성/수정 | 사이트 특성에 맞게 커스터마이징 |
| 애셋 리스트 생성 | images.json → brand-assets.md |
| 브랜드 분석 | 추출 데이터 → brand-analysis.md |
| 프로젝트 연결 | 추출 자산을 01_project-setup으로 전달 |

---

## 다음 단계

```
[00_brand-extraction] 완료
    ↓
[01_project-setup] 프로젝트 폴더 생성
    - brand-assets.md 참조
    - brand-analysis.md → 브랜드 가이드 초안
```

---

## 주의사항

- robots.txt 준수
- 요청 간 딜레이 (1-2초)
- 저작권 자산은 참고용으로만
- 대형 사이트는 depth=2~3 권장
