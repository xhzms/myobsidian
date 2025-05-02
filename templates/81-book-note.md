<%*
// 기존 책 목록 가져오기
const bookFiles = app.vault.getFiles()
    .filter(file => file.path.startsWith('30-Literature/31-책/'))
    .filter(file => file.name.startsWith('book-'))
    .map(file => {
        const title = app.metadataCache.getFileCache(file)?.frontmatter?.title || file.basename.replace('book-', '');
        return {
            title: title,
            filename: file.basename.replace('book-', '')
        };
    });

if (bookFiles.length === 0) {
    new Notice("31-책 폴더에 책이 없습니다. 먼저 책을 추가해주세요.");
    return;
}

// 책 선택하기
const selectedBook = await tp.system.suggester(
    (item) => item.title,
    bookFiles,
    "어떤 책의 메모인가요?"
);

if (!selectedBook) return;

// 메모 주제 입력 받기
const noteSubject = await tp.system.prompt("이 메모의 주제는 무엇인가요? (예: 1장_요약, 인상깊은_구절, 질문_정리 등)");
if (!noteSubject) return;

// 파일명 생성을 위한 문자열 정리
const formatText = (text) => {
    return text
        .toLowerCase()
        .replace(/[^가-힣a-z0-9\s-]/g, "")
        .replace(/\s+/g, "_");
};

// 최종 파일명 생성
const filename = `note-${selectedBook.filename}-${formatText(noteSubject)}`;

// 파일 이름 변경 후 이동
await tp.file.rename(filename);
await tp.file.move("/30-Literature/32-독서노트/" + filename);

// 프론트매터와 기본 내용 생성
tR = `---
title: ${selectedBook.title} - ${noteSubject}
book: ${selectedBook.title}
date: ${tp.date.now("YYYY-MM-DD")}
created: ${tp.date.now("YYYYMMDDHHmmss")}
tags: [booknote]
type: reading-note
---

# 📝 ${selectedBook.title} - ${noteSubject}

## 📍 현재 진행 상황
- 페이지: 
- 챕터: 

## ✏️ 메모
- 

## 💭 떠오른 생각
- 

## ❓ 추가로 알아볼 것
- 

## 🔗 연결된 메모
- [[book-${selectedBook.filename}]]
- 

`
_%> 