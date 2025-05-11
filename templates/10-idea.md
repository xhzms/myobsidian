<%*
// Drafts 폴더의 파일 목록에서 어미단어 추출
const fleetingFiles = app.vault.getFiles()
    .filter(file => file.path.startsWith('20-Drafts/'))
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

// 계층값에 따라 이동할 폴더 결정
const targetFolder = hierarchy === 'where' ? '10-Inbox' : '20-Drafts';

// 파일 이름 변경 후 이동
await tp.file.rename(filename);
await tp.file.move(`/${targetFolder}/` + filename);

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

// Drafts MOC에 새로운 링크 추가
const mocFile = app.vault.getAbstractFileByPath("00-Map_Of_Contents/Drafts.md");
if (mocFile) {
    const mocContent = await app.vault.read(mocFile);
    const newLink = `- [[${filename}]]`;
    
    // 주제별 초입점 섹션 찾기
    const sectionIndex = mocContent.indexOf("## 주제별 초입점");
    if (sectionIndex !== -1) {
        // 새로운 링크를 주제별 초입점 섹션 바로 다음 줄에 추가
        const updatedContent = mocContent.slice(0, sectionIndex + "## 주제별 초입점".length) + 
                             "\n\n" + newLink + 
                             mocContent.slice(sectionIndex + "## 주제별 초입점".length);
        await app.vault.modify(mocFile, updatedContent);
    }
}
_%>
