<%*
// 수동 아카이빙 템플릿
// 완료 항목([x])과 하위 내용을 logs로 이동

const projectPath = "50-Project/51_Moduda";
const logsPath = projectPath + "/logs";
const today = tp.date.now("YYYY-MM-DD");

try {
    const currentFile = tp.file.find_tfile(projectPath + "/_current");
    if (!currentFile) {
        new Notice("⚠️ _current.md 파일을 찾을 수 없습니다.");
        return;
    }

    const content = await app.vault.read(currentFile);

    // 작업 중 섹션 추출
    const workingSection = content.split("# 🔥 작업 중")[1];
    if (!workingSection) {
        new Notice("⚠️ '작업 중' 섹션을 찾을 수 없습니다.");
        return;
    }

    const beforeTodo = workingSection.split("# 📝 해야 할 일")[0];
    const lines = beforeTodo.split("\n");

    const completed = [];
    const remaining = [];
    let isCompleted = false;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // 완료된 항목 시작
        if (line.match(/^- \[x\]/i)) {
            isCompleted = true;
            completed.push(line);
        }
        // 미완료 항목 시작
        else if (line.match(/^- \[ \]/)) {
            isCompleted = false;
            remaining.push(line);
        }
        // 하위 내용 (탭이나 공백으로 시작)
        else if (line.match(/^[\t\s]+/) && line.trim() !== "") {
            if (isCompleted) {
                completed.push(line);
            } else {
                remaining.push(line);
            }
        }
        // 구분선은 스킵
        else if (line.trim() === "---" || line.trim() === "") {
            // skip
        }
    }

    // 완료 항목이 없으면 알림
    if (completed.length === 0) {
        new Notice("ℹ️ 완료된 항목이 없습니다.");
        return;
    }

    // logs 파일 생성
    const logPath = logsPath + "/" + today + ".md";
    const logContent = `---
date: ${today}
project: Moduda
---

# ✅ 완료된 작업
${completed.join("\n")}
`;

    // 기존 로그 파일이 있으면 추가, 없으면 생성
    const existingLog = tp.file.find_tfile(logsPath + "/" + today);
    if (existingLog) {
        const oldLog = await app.vault.read(existingLog);
        await app.vault.modify(existingLog, oldLog + "\n" + completed.join("\n"));
    } else {
        await app.vault.create(logPath, logContent);
    }

    // _current.md 업데이트
    const todoSection = content.split("# 📝 해야 할 일")[1] || "";
    const createdDate = content.match(/created: (\d{4}-\d{2}-\d{2})/);

    const newCurrentContent = `---
created: ${createdDate ? createdDate[1] : today}
updated: ${tp.date.now("YYYY-MM-DD HH:mm")}
last_archived: ${today}
project: Moduda
---

# 🔥 작업 중
${remaining.length > 0 ? remaining.join("\n") : ""}

---

# 📝 해야 할 일${todoSection}`;

    await app.vault.modify(currentFile, newCurrentContent);

    new Notice("✅ " + completed.filter(l => l.match(/^- \[x\]/i)).length + "개 완료 항목이 logs/" + today + ".md로 이동됨");

} catch (e) {
    new Notice("❌ 오류: " + e.message);
    console.log("Archive error: " + e.message);
}
_%>
