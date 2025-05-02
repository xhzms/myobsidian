<%*
// 책 제목 입력 받기
const bookTitle = await tp.system.prompt("책 제목을 입력하세요");
if (!bookTitle) return;

// 파일명 생성을 위한 문자열 정리
const formatText = (text) => {
    return text
        .toLowerCase()
        .replace(/[^가-힣a-z0-9\s-]/g, "")
        .replace(/\s+/g, "_");
};

// 최종 파일명 생성
const filename = `book-${formatText(bookTitle)}`;

// 파일 이름 변경 후 이동
await tp.file.rename(filename);
await tp.file.move("/30-Literature/31-책/" + filename);

// 프론트매터와 기본 내용 생성
tR = `---
title: ${bookTitle}
author: 
publisher: 
date: ${tp.date.now("YYYY-MM-DD")}
created: ${tp.date.now("YYYYMMDDHHmmss")}
tags: [book]
status: [안 읽음]
---

# 📚 ${bookTitle}

## 💡 책 한 줄 요약


## 🎯 이 책을 읽는 목적


## 📑 주요 내용
### 1장


### 2장


### 3장


## ✍️ 인상 깊은 구절
> 

## 🤔 나의 생각


## ⭐ 평가
### 좋았던 점
- 

### 아쉬웠던 점
- 

## 연결된 생각
- 

`
_%> 