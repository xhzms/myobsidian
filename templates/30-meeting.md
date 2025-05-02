<%*
// 날짜 정보 가져오기
const today = tp.date.now("YYYYMMDD");
const created = tp.date.now("YYYYMMDDHHmmss");
const displayDate = tp.date.now("YYYY-MM-DD");

// 미팅 대상자/메모 입력 받기
const meetingTitle = await tp.system.prompt("미팅 대상자/메모를 입력하세요");
if (!meetingTitle) return;

// 파일명 생성을 위한 문자열 정리
const formatText = (text) => {
    return text
        .toLowerCase()
        .replace(/[^가-힣a-z0-9\s-]/g, "")
        .replace(/\s+/g, "_");
};

// 최종 파일명 생성
const filename = `meet-${today}-${formatText(meetingTitle)}`;

// 파일 이름 변경 후 이동
await tp.file.rename(filename);
await tp.file.move("/90-Logs/Meet/" + filename);

// 프론트매터와 기본 내용 생성
tR = `---
title: ${meetingTitle}
date: ${displayDate}
created: ${created}
tags: [meeting]
type: meeting-note
---

# 🤝 ${meetingTitle} 미팅

## 📝 메모
`
_%> 