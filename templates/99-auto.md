<%*
// 기본 설정
const currentFolder = tp.file.folder(true)
    .split("/")  // 슬래시로 분리
    .pop()       // 마지막 폴더명만 가져오기
    .toLowerCase();

// 제목 입력 받기
const title = await tp.system.prompt("제목을 입력하세요");
if (!title) return;

// 파일명 생성을 위한 제목 정리 (한글은 그대로 두고 영문/특수문자만 처리)
const formattedTitle = title
    .toLowerCase()
    .replace(/[^가-힣a-z0-9\s-]/g, "") // 한글, 영문 소문자, 숫자, 공백, 하이픈만 허용
    .replace(/\s+/g, "-"); // 공백을 하이픈으로 변경

// 최종 파일명 생성
const filename = `${currentFolder}-${formattedTitle}`;

// 파일 이름 변경
await tp.file.rename(filename);

// 프론트매터와 기본 내용 생성
tR = `---
title: ${title}
date: ${tp.date.now("YYYY-MM-DD")}
created: ${tp.date.now("YYYYMMDDHHmmss")}
tags:
---

# ${title}

`
_%>
