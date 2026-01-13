---
name: funnel-design-project-setup
description: "마케팅 퍼널 프로젝트의 가이드 문서 작성 스킬. 프로젝트 폴더 구조 생성, 사업 골조 정의, 퍼널 설계, 마케팅 가이드 문서 작성을 지원합니다. 트리거: 프로젝트 세팅, 폴더 구조, 타겟 정의, 퍼널 설계, 마케팅 문서"
---

# Project Setup Skill

프로젝트 초기 세팅부터 마케팅 가이드 문서까지 작성하는 스킬입니다.

## 작업 Phase

### Phase 1: 프로젝트 세팅
1. 프로젝트 파악 (서비스 유형, 현재 상태)
2. 폴더 구조 생성
3. 기존 문서 정리

**폴더 구조:**
```
프로젝트/
├── _index.md
├── _current.md
├── 00_foundation/
├── 01_strategy/
├── 02_marketing/
├── 03_product/
├── meet_logs/
└── working_logs/
```

### Phase 2: 사업 골조 정의
1. 비즈니스 모델 (수익 구조, 가격 정책)
2. 타겟 오디언스 (표면/내면 구분)
3. 성장 로드맵

**타겟 정의 핵심:**
| 레이어 | 질문 | 마케팅 언급 |
|--------|------|-------------|
| 표면 | 고객이 말하는 것 | 직접 언급 ✅ |
| 내면 | 진짜 원하는 것 | 암시만 💭 |

### Phase 3: 퍼널 설계
1. 전체 퍼널 구조 (인지 → 관심 → 전환)
2. 단계별 콘텐츠 정의
3. 운영 프로세스

**인지 단계 콘텐츠 4유형:**
| 유형 | 비율 | 역할 |
|------|------|------|
| 교육/정보성 | 40% | 가치 제공, 전문성 |
| 트렌드/공감 | 30% | 관계 형성 |
| 문제-솔루션 | 20% | What, 포지셔닝 |
| 브랜드 철학 | 10% | Why, 감정 연결 |

### Phase 4: 마케팅 가이드
1. 메시지 프레임워크
2. 콘텐츠 전략 (Cascading 구조)
3. 채널별 제작 가이드

**Cascading 문서 구조:**
```
Level 1: content-strategy.md (전체 전략)
    ↓ [[채널-strategy]]
Level 2: channel-strategy.md (채널별)
    ↓ [[채널-콘텐츠유형]]
Level 3: content-type.md (제작 가이드)
```

## 문서 템플릿

각 문서 템플릿은 `templates/` 폴더에 있습니다:
- [business-model.md](templates/business-model.md) - 비즈니스 모델
- [target-audience.md](templates/target-audience.md) - 타겟 오디언스
- [funnel-overview.md](templates/funnel-overview.md) - 퍼널 개요
- [content-strategy.md](templates/content-strategy.md) - 콘텐츠 전략
- [channel-strategy.md](templates/channel-strategy.md) - 채널 전략

## 클라이언트 질문 템플릿

### 초기 세팅
- "현재 어떤 채널에서 콘텐츠를 운영하고 있나요?"
- "기존 콘텐츠 데이터를 공유해주실 수 있나요?"

### 타겟/메시지
- "고객이 왜 이 서비스를 찾는다고 생각하세요?" (표면)
- "고객이 진짜 원하는 건 뭘까요?" (내면)
- "왜 이 서비스를 시작하셨어요?" (브랜드 철학)

### 퍼널 설계
- "현재 전환 흐름이 어떻게 되나요?"
- "가장 효과적인 전환 포인트가 어디인가요?"
