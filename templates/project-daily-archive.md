<%*
// 일일 아카이빙 템플릿 (Startup 템플릿으로 설정)
// last_archived와 오늘 날짜가 다르면 완료 항목을 logs로 이동

const projectPath = "50-Project/51_Moduda";
const logsPath = projectPath + "/logs";
const today = tp.date.now("YYYY-MM-DD");

try {
    const currentFile = tp.file.find_tfile(projectPath + "/_current");
    if (!currentFile) return;

    const content = await app.vault.read(currentFile);

    // last_archived 날짜 추출
    const archivedMatch = content.match(/last_archived: (\d{4}-\d{2}-\d{2})/);
    const lastArchived = archivedMatch ? archivedMatch[1] : null;

    // 날짜가 같으면 아무것도 안함
    if (lastArchived === today) return;

    // 작업 중 섹션에서 완료된 항목 추출
    const workingSection = content.split("# 🔥 작업 중")[1];
    if (!workingSection) return;

    const beforeTodo = workingSection.split("# 📝 해야 할 일")[0];
    const lines = beforeTodo.split("\n");

    const completed = [];
    const remaining = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.match(/^- \[x\]/i)) {
            completed.push(line);
        } else if (line.trim() !== "" && line.trim() !== "---") {
            remaining.push(line);
        }
    }

    // 완료 항목이 없으면 날짜만 업데이트
    if (completed.length === 0) {
        const newContent = content.replace(
            /last_archived: \d{4}-\d{2}-\d{2}/,
            "last_archived: " + today
        );
        await app.vault.modify(currentFile, newContent);
        return;
    }

    // logs 파일 생성 (아카이빙 날짜 기준)
    const archiveDate = lastArchived || tp.date.now("YYYY-MM-DD", -1);
    const logPath = logsPath + "/" + archiveDate + ".md";

    const logContent = `---
date: ${archiveDate}
project: Moduda
---

# ✅ 완료된 작업
${completed.join("\n")}
`;

    // 기존 로그 파일이 있으면 추가, 없으면 생성
    const existingLog = tp.file.find_tfile(logsPath + "/" + archiveDate);
    if (existingLog) {
        const oldLog = await app.vault.read(existingLog);
        await app.vault.modify(existingLog, oldLog + "\n" + completed.join("\n"));
    } else {
        await app.vault.create(logPath, logContent);
    }

    // _current.md 업데이트 (완료 항목 제거)
    const todoSection = content.split("# 📝 해야 할 일")[1] || "";

    const newCurrentContent = `---
created: ${content.match(/created: (\d{4}-\d{2}-\d{2})/)[1]}
updated: ${tp.date.now("YYYY-MM-DD HH:mm")}
last_archived: ${today}
project: Moduda
---

# 🔥 작업 중
${remaining.filter(l => l.trim()).join("\n")}

---

# 📝 해야 할 일${todoSection}`;

    await app.vault.modify(currentFile, newCurrentContent);

    new Notice("✅ " + completed.length + "개 완료 항목이 logs/" + archiveDate + ".md로 이동됨");

} catch (e) {
    console.log("Archive error: " + e.message);
}
_%>
