<%*
// 날짜 정보 가져오기
const today = tp.date.now("YYYYMMDD");
const created = tp.date.now("YYYYMMDDHHmmss");
const displayDate = tp.date.now("YYYY-MM-DD");

// 제목 입력 받기
const title = await tp.system.prompt("예배/묵상 제목을 입력하세요 (예: 학개1장, 수요예배 등)");
if (!title) return;

// 파일명 생성
const filename = `예배-${today}-${title}`;

// 파일 이름 변경
await tp.file.rename(filename);
await tp.file.move("60-Area/61-예수님/" + filename);

// 프론트매터와 기본 내용 생성
tR = `---
title: ${title}
date: ${displayDate}
created: ${created}
tags: [묵상, 예배]
type: worship-note
---

# ${title}

## 📖 말씀
* 본문: 
* 주제:
* 메모: 

## 🙏 기도
* 회개:
  * 

* 감사:
  * 

* 중보:
  * 

## 💡 깨달음
* 

`
_%> 