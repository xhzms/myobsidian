<%*
// Fleeting 폴더의 파일 목록에서 어미단어 추출
const fleetingFiles = app.vault.getFiles()
    .filter(file => file.path.startsWith('20-Fleeting/'))
    .map(file => file.basename.split('-')[0]);

// 중복 제거하여 고유한 어미단어 목록 생성
const uniquePrefixes = [...new Set(fleetingFiles)];

// 새로운 아이디어 입력 옵션 추가
uniquePrefixes.push("+New");

// 어미단어 선택 또는 새로 입력
const selectedOption = await tp.system.suggester(
    (item) => item,
    uniquePrefixes,
    "아이디어 분류를 선택하세요"
);

if (!selectedOption) return;

let ideaName;
if (selectedOption === "+New") {
    ideaName = await tp.system.prompt("새로운 아이디어 분류명을 입력하세요");
    if (!ideaName) return;
} else {
    ideaName = selectedOption;
}

// 계층 값 입력 여부 확인
const shouldInputHierarchy = await tp.system.suggester(
    ["N 계층값 부여 보류", "Y 계층값 부여"],
    ["no", "yes"],
    "계층 값을 지금 입력하시겠습니까?"
);

// 계층 값 설정
let hierarchy = 'where';
if (shouldInputHierarchy === 'yes') {
    const inputHierarchy = await tp.system.prompt("계층 값을 입력하세요");
    if (inputHierarchy) {
        hierarchy = inputHierarchy;
    }
}

// 소제목 입력 받기
const subtitle = await tp.system.prompt("소제목을 입력하세요");
if (!subtitle) return;

// 파일명 생성을 위한 문자열 정리
const formatText = (text) => {
    return text
        .toLowerCase()
        .replace(/[^가-힣a-z0-9\s-]/g, "")
        .replace(/\s+/g, "_");
};

// 최종 파일명 생성
const filename = `${formatText(ideaName)}-${hierarchy}-${formatText(subtitle)}`;

// 파일 이름 변경 후 이동
await tp.file.rename(filename);
await tp.file.move("/20-Fleeting/" + filename);

// 프론트매터와 기본 내용 생성
tR = `---
title: ${subtitle}
date: ${tp.date.now("YYYY-MM-DD")}
created: ${tp.date.now("YYYYMMDDHHmmss")}
tags: [${ideaName}]
idea: ${ideaName}
hierarchy: ${hierarchy}
---

* 
* 
* 
`
_%>
