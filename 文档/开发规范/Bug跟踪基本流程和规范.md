# Issue/Bug 跟踪基本流程

## 1. 引言

本文档定义了本项目使用 Issue/Bug 跟踪系统的基本流程和规范。有效的 Issue 跟踪有助于管理任务、修复缺陷、记录问题历史并促进沟通。

## 2. 使用平台

*   **跟踪平台:** **GitHub Issues** ([占位符：填写项目 GitHub 仓库 Issues 页面的链接])

## 3. Issue/Bug 的生命周期

一个典型的 Issue/Bug 会经历以下状态 (使用 GitHub Labels 管理)：

1.  **Open (打开):** 问题被报告，尚未分配或确认。默认状态，通常无特定标签，或可标记为 `status: needs triage`。
2.  **Triage/Backlog (待分类/待办):** 可选用 `status: needs triage` 或 `status: backlog` 标签，表示已初步查看，等待评估优先级和分配。
3.  **Accepted/To Do (已接受/待办):** 移除 `needs triage` 标签，可添加 `status: todo` 或直接分配负责人。表示问题已确认，计划处理。
4.  **In Progress (进行中):** 添加 `status: in progress` 标签，表示已有人正在处理此问题。通常与分配负责人同时进行。
5.  **Needs Review (待审查):** 当关联的 Pull Request 被创建时，可自动或手动添加 `status: needs review` 标签。
6.  **Blocked (受阻):** 添加 `status: blocked` 标签，并在评论中说明受阻原因。
7.  **Resolved/Fixed (已解决/已修复):** 当关联的 Pull Request 被合并到主开发分支 (`main` 或 `develop`) 时，Issue 通常会自动关闭或标记为已解决。可保留 `status: resolved` 标签一段时间用于跟踪。
8.  **Closed/Done (已关闭/完成):** 问题最终关闭。GitHub 会自动处理此状态。可根据关闭原因添加 `resolution: fixed`, `resolution: duplicate`, `resolution: wontfix`, `resolution: invalid` 等标签。

**本项目简化流程:**
*   **新建:** 默认 Open。
*   **分配/认领:** 添加负责人，添加 `status: in progress`。
*   **提交 PR:** 添加 `status: needs review`。
*   **PR 合并:** Issue 自动关闭 (通过 Commit Message 或 PR 关联)。
*   **其他情况:** 手动添加 `status: blocked`, `status: backlog` 或 `resolution:*` 标签并关闭。

## 4. 报告 Issue/Bug (提交规范)

*   **搜索重复:** 在报告新问题前，请先搜索现有 Issue，避免重复报告。
*   **使用模板:** **必须**使用 GitHub 提供的 Issue 模板 (如果配置了) 或遵循以下格式来报告问题。
    *   **Bug 报告模板:**
        *   **标题:** 清晰、简洁地描述问题（例如："用户登录时输入错误密码提示信息不明确"）。
        *   **环境 (Environment):** (如果相关) 提供操作系统、浏览器、库版本、相关软件版本等。
        *   **复现步骤 (Steps to Reproduce):** 提供详细、清晰、按顺序的步骤，让其他人能够稳定地复现该问题。
        *   **期望行为 (Expected Behavior):** 清晰描述在上述步骤下，系统本应如何表现。
        *   **实际行为 (Actual Behavior):** 清晰描述系统实际的表现，包括完整的错误信息和堆栈跟踪（如果适用）。
        *   **截图/日志 (Screenshots/Logs):** (强烈建议) 附上能说明问题的截图或相关日志片段。
    *   **功能请求/改进建议模板:**
        *   **标题:** 清晰描述所需功能或改进点。
        *   **用户故事 (User Story):** (可选) 描述用户角色、期望动作和收益。
        *   **功能描述 (Description):** 详细说明功能的具体内容、目标和理由。为什么需要这个功能？它解决了什么问题？
        *   **验收标准 (Acceptance Criteria):** (可选) 定义如何判断该功能已成功实现。
        *   **建议方案/想法 (Suggestions/Ideas):** (可选) 如果有初步的想法或建议方案，可以写出来。
*   **添加标签 (Labels):** 根据问题类型、优先级、涉及模块等，添加合适的标签（见下文）。
*   **分配与里程碑 (Assignment & Milestone):** (如果适用) 将 Issue 分配给负责人（即使是你自己），并关联到相关的里程碑或项目计划。

## 5. 处理 Issue/Bug

*   **认领/分配:** 明确谁负责处理某个 Issue。将状态更新为 `status: in progress` 并分配负责人。
*   **分支关联:** 创建新的 Git 分支来处理该 Issue，分支名称应与 Issue 相关（参考版本控制规范）。
*   **沟通与更新:** 在 Issue 的评论区记录处理进展、遇到的问题、需要澄清的信息等。保持沟通顺畅。
*   **代码提交关联:** 提交代码时，在 Commit Message 中关联对应的 Issue ID（例如 `Fixes #123` 或 `Ref #123`，参考版本控制规范）。
*   **修复/完成后:**
    *   提交包含修复或实现代码的 Pull Request (PR)。
    *   在 PR 的描述中链接到对应的 Issue。
    *   确保 PR 通过 CI 检查。
    *   请求代码审查。
    *   更新 Issue 状态为 `status: needs review`。

## 6. 关闭 Issue/Bug

*   **验证:** 在 PR 合并到 `main` 分支后，应进行最终验证，确保问题已解决且没有引入新的回归问题。
*   **关闭:** PR 合并后，如果配置正确，GitHub 通常会自动关闭关联的 Issue。若未自动关闭，则手动关闭 Issue。可以根据情况添加 `resolution:*` 标签。
*   **无效/重复/不处理:** 如果 Issue 被确认为无效、重复或决定不予处理，也应将其关闭，并添加相应的 `resolution:*` 标签和说明原因。

## 7. 标签体系 (Labels)

建议使用以下标签体系（可在 GitHub 仓库的 Labels 页面配置）：

*   **类型 (Type):** `type: bug`, `type: feature`, `type: enhancement`, `type: documentation`, `type: chore`, `type: question`, `type: performance`, `type: security`
*   **优先级 (Priority):** `priority: critical`, `priority: high`, `priority: medium`, `priority: low`, `priority: backlog`
*   **状态 (Status):** `status: needs triage`, `status: todo`, `status: in progress`, `status: needs review`, `status: blocked`
*   **解决方式 (Resolution):** `resolution: fixed`, `resolution: duplicate`, `resolution: wontfix`, `resolution: invalid`, `resolution: works-as-intended`
*   **模块/范围 (Module/Scope):** `module: core-engine`, `module: adapter-manager`, `module: adapter-chrome`, `module: adapter-vscode`, `module: dkg`, `module: docs`, `module: ci-cd`, `module: tests` **[根据项目实际模块调整]**
*   **(可选) 难度 (Difficulty):** `difficulty: easy`, `difficulty: medium`, `difficulty: hard`
*   **(可选) 寻求帮助 (Help Wanted):** `help wanted`, `good first issue`

**要求:** 每个 Issue 都应至少有一个 `type` 标签。鼓励根据情况添加其他标签。

## 8. AI 助手与 Issue 跟踪

*   AI 助手在发现 Bug 或完成任务时，应遵循此规范在 GitHub Issues 中创建或更新 Issue。
*   AI 助手在处理 Bug 时，应先查阅对应的 Issue (#IssueID)，了解背景、复现步骤和已尝试的方法。
*   AI 助手在启动高级调试协议前，应检查并要求确认 GitHub Issue 中关于此问题的记录是否最新。
