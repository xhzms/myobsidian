# CLAUDE.md

이 프로젝트는 Obsidian 기반의 개인 지식 관리(PKM) 시스템입니다.

## 폴더 구조 (PARA 메소드 기반)

```
00-Map_Of_Contents/  # MOC - 주제별 인덱스
10-Inbox/            # 새로운 아이디어, 임시 노트
20-Drafts/           # 작성 중인 노트
30-Literature/       # 참고 자료
  ├── 31-책/         # 책 정보
  └── 32-독서노트/   # 독서 메모
40-Perment/          # 영구 노트 (완성된 지식)
50-Project/          # 진행 중인 프로젝트
60-Area/             # 관심 영역
  ├── 61-예수님/     # 신앙 관련
  ├── 62-가정/       # 가정 관련
  └── 63-일/         # 업무 관련
70-Resources/        # 참고 리소스
80-Archives/         # 아카이브
90-Logs/             # 로그 (미팅 기록 등)
templates/           # 노트 템플릿
Excalidraw/          # 드로잉
```

## 파일 명명 규칙

- 형식: `{주제}-{순서}-{제목}.md`
- 예시: `marketing-z-후킹.md`, `diestro-a-퍼스널브랜딩.md`
- 순서: a, b, c... (메인) / z, zz, zzz... (부가)

## 템플릿

- `10-idea.md` - 아이디어 노트
- `20-jesus.md` - 예배/신앙 노트
- `30-meeting.md` - 미팅 노트
- `80-book.md` - 책 정보
- `81-book-note.md` - 독서 노트

## 프론트매터 필수 항목

```yaml
---
title: 제목
date: YYYY-MM-DD
tags: #태그
---
```

## 주요 주제 키워드

- `marketing` - 마케팅
- `diestro` - 퍼스널 브랜딩
- `gdesk` - 지데스크 관련
- `mes` - MES 관련
- `websell` - 웹 판매
- `consulting_service` - 컨설팅 서비스
