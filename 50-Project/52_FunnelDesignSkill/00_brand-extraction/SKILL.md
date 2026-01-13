# Brand Extraction Skill

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
├── classified/             # 분류된 이미지 (심볼릭 링크 또는 복사)
│   ├── hero/
│   ├── product/
│   ├── icon/
│   ├── person/
│   ├── background/
│   ├── social/
│   └── misc/
├── brand-assets.md         # 주요 애셋 리스트 (로컬 경로)
├── brand-analysis.md       # 브랜드 분석 리포트
└── crawl-log.json          # 크롤링 로그
```

---

## 이미지 분류 체계

| 폴더명 | 용도 | 판단 기준 |
|--------|------|-----------|
| `hero/` | 메인 배너, 히어로 이미지 | 가로형, 대형 (1200px+), context="hero" |
| `product/` | 제품/서비스/리뷰 이미지 | 정방형~가로형, 중형, context="product"/"testimonial" |
| `icon/` | 아이콘, 로고, UI 요소 | 소형 (200px 이하), SVG/PNG, context="header"/"footer" |
| `person/` | 인물, 팀, 고객 사진 | 얼굴 감지, 프로필 형태 |
| `background/` | 배경, 패턴, 텍스처 | CSS background, 대형, 반복 |
| `social/` | SNS 이미지, OG 이미지 | meta 태그 추출, 특정 비율 |
| `misc/` | 분류 불가 | 기타 |

---

## 주요 애셋 리스트 생성 (brand-assets.md)

크롤링 완료 후 `images.json`을 기반으로 **용도별로 분류된 애셋 리스트**를 마크다운으로 생성합니다.

### 분류 카테고리

| 섹션 | 파일명 패턴 / context | 설명 |
|------|----------------------|------|
| 로고 & BI | `*logo*`, `*brand*`, `*bi-*`, `*ci-*` | 브랜드 아이덴티티 |
| 히어로 슬라이드 | `slide-*`, context="hero" | 메인 배너 이미지 |
| 캐릭터 | `char-*`, `character*` | 마스코트, 캐릭터 |
| 메인 콘텐츠 | `main-*`, `section*-pic*` | 주요 사진 |
| 픽토그램 & 아이콘 | `*icon*`, `*picto*`, context="icon" | UI 요소 |
| SNS 아이콘 | `instagram*`, `youtube*`, `line*` 등 | 소셜 미디어 |
| 후기/리뷰 | `review/*`, `r-*`, `rm-*` | 고객 리뷰 이미지 |
| 상품 이미지 | `/product/` 경로, alt에 상품명 | 제품/서비스 |

### 테이블 형식

```markdown
| 용도 | 로컬 파일 | 원본 | 비고 |
|-----|----------|------|------|
| 메인 로고 | [a4fd5fb193e8.svg](raw/images/a4fd5fb193e8.svg) | main-logo.svg | |
| 히어로 슬라이드 1 | [db572e8b26cf.svg](raw/images/db572e8b26cf.svg) | slide-0.svg | ⚠️ 흰색 그래픽 |
```

### SVG 색상 분석 (비고 표기)

SVG 파일의 경우 `fill` 속성을 파싱하여 배경 필요 여부를 자동 감지합니다:

| 조건 | 비고 표기 |
|------|----------|
| `fill="white"` + 배경 없음 | `⚠️ 흰색 그래픽, 컬러 배경 위에서 사용` |
| `fill="none"` (투명) | `⚠️ 투명 배경` |
| 단일 컬러 fill | 해당 컬러 HEX 표기 |

---

## 브랜드 분석 리포트 (brand-analysis.md)

추출된 데이터를 기반으로 브랜드 분석 리포트를 자동 생성합니다.

### 포함 항목

#### 1. 브랜드 아이덴티티
- 핵심 슬로건
- 포지셔닝 키워드
- 타겟 오디언스 추정

#### 2. 컬러 시스템
```markdown
### Primary Colors
| 용도 | HEX | 사용빈도 |
|-----|-----|---------|
| Primary Blue | `#3b84f5` | 2,205회 |

### Accent Colors
| 용도 | HEX | 사용빈도 |
|-----|-----|---------|
| Accent Yellow-Green | `#e8ffb0` | 213회 |
```

- 상위 10개 색상 추출
- 용도 추정 (Primary, Secondary, Accent, Text, Background)

#### 3. 타이포그래피
| 폰트명 | 용도 추정 |
|-------|----------|
| Pretendard | 본문 |
| Montserrat | 영문 헤드라인 |

#### 4. 핵심 카피
- 헤드라인 (h1, h2)
- CTA 버튼 텍스트
- 슬로건/미션

#### 5. 퍼널 구조 분석
```
[Awareness] → [Interest] → [Trust] → [Conversion] → [Expansion]
```
- 리드마그넷 URL
- CTA 패턴
- 신뢰 요소 (리뷰, 파트너 로고 등)

#### 6. 주요 페이지 링크
| 페이지 | URL |
|-------|-----|
| 메인 | https://example.com |
| 리드마그넷 | https://example.com/free |

---

## 텍스트 추출 구조 (texts.json)

depth >= 2 크롤링 시 페이지별 텍스트를 3-tier 구조로 정리:

```json
{
  "by_page": {
    "https://example.com": {
      "headlines": ["..."],
      "cta_buttons": ["..."]
    }
  },
  "common": ["Footer text", "Copyright..."],
  "unique": {
    "https://example.com": ["Page-specific text..."]
  }
}
```

| 필드 | 설명 |
|------|------|
| `by_page` | 페이지별 전체 텍스트 |
| `common` | 50% 이상 페이지에서 반복되는 텍스트 (footer 등) |
| `unique` | 해당 페이지에서만 나타나는 고유 텍스트 |

---

## 스크립트 사용법

### 1. 크롤러 실행

```bash
cd scripts
python crawler.py --url "https://example.com" --output "../output/brand-name" --depth 2
```

**옵션:**
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--url` | 시작 URL | (필수) |
| `--output` | 저장 경로 | ./output |
| `--depth` | 크롤링 깊이 | 2 |
| `--same-domain` | 동일 도메인만 | True |

### 2. 분류기 실행

```bash
python classifier.py --input "../output/brand-name/raw" --output "../output/brand-name/classified"
```

**분류 방식:**
1. **1차 - 메타데이터 기반**: 파일명, alt 텍스트, CSS 클래스
2. **2차 - 크기/비율 기반**: 이미지 dimensions 분석
3. **3차 - context 필드**: 크롤러가 추출한 위치 정보

### 3. 애셋 리스트 생성

크롤링 완료 후 Claude가 `images.json`을 분석하여 `brand-assets.md` 생성:

```
Claude에게 요청:
"images.json을 분석해서 주요 애셋 리스트를 brand-assets.md로 만들어줘.
로컬 파일 경로로 링크하고, SVG는 색상 분석해서 비고에 표기해줘."
```

### 4. 브랜드 분석 리포트 생성

```
Claude에게 요청:
"texts.json, colors.json, fonts.json을 분석해서 brand-analysis.md를 만들어줘."
```

---

## Claude 역할

Claude는 **직접 크롤링하지 않고** 다음을 담당:

| 역할 | 설명 |
|------|------|
| 스크립트 생성/수정 | 사이트 특성에 맞게 크롤러 커스터마이징 |
| 분류 기준 조정 | 브랜드 특성에 맞는 분류 카테고리 추가 |
| **애셋 리스트 생성** | images.json → brand-assets.md 변환 |
| **브랜드 분석** | 추출 데이터 기반 brand-analysis.md 생성 |
| **SVG 색상 분석** | fill 속성 파싱, 사용 시 주의사항 표기 |
| 프로젝트 연결 | 추출 자산을 01_project-setup으로 전달 |

---

## 옵시디언 호환성

### 상대경로 링크
모든 파일 링크는 `brand-assets.md` 기준 상대경로로 생성:

```markdown
# 올바른 예시
[a4fd5fb193e8.svg](raw/images/a4fd5fb193e8.svg)

# 잘못된 예시 (절대경로)
[main-logo.svg](https://example.com/img/main-logo.svg)
```

### 이미지 임베드 (선택)
옵시디언에서 이미지 미리보기가 필요한 경우:

```markdown
# 링크 형식
[파일명](raw/images/파일명.jpg)

# 임베드 형식 (옵시디언 전용)
![[raw/images/파일명.jpg]]
```

---

## 다음 단계

추출 완료 후:

```
[00_brand-extraction] 완료
    ↓
[01_project-setup] 프로젝트 폴더 생성
    - brand-assets.md 참조하여 필요 자산 선별
    - brand-analysis.md → 브랜드 가이드 초안으로 활용
    - classified/ 폴더 → assets/ 폴더로 이동
```

---

## 주의사항

- robots.txt 준수
- 요청 간 딜레이 설정 (1-2초)
- 저작권 있는 자산은 참고용으로만 사용
- 대형 사이트는 depth 제한 권장 (depth=2~3)
- SVG 파일은 반드시 색상 분석하여 사용 조건 명시
