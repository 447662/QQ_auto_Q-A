---
name: qq-friend-message
description: Windows 本机 QQ 普通好友消息 GUI 自动化。在本项目 QQ/频道等外部消息自动问答中，只能用于发送已通过项目批准口令门禁的回复：`#配置推荐` 仅限电脑配置相关问题，`#集院问答` 仅限新生生活、学业课程、竞赛科研及基于已提供资料的校园问答；未匹配批准口令时不得生成通用 AI 自动回复。用于在 QQ 桌面客户端已登录时，按好友昵称或备注名打开普通好友单聊并填入消息；只有用户明确要求直接发送时才发送。适用于用户说“用 QQ 给某个普通好友发消息”“QQ 好友消息”“不是 QQ 频道”的场景。
metadata:
  version: "0.1.0"
  tags: qq windows gui automation friend-message
---

# QQ Friend Message

这个 skill 通过 Windows 桌面 GUI 自动化控制本机 QQ 客户端，用于普通 QQ 好友单聊。它不是 QQ 频道接口，也不依赖 `tencent-channel-cli`。

## 项目全局 AI 自动回复门禁

在本项目的 QQ、QQ群、QQ 频道、帖子、评论、私信或其他外部消息自动问答场景中，本技能只能发送已经通过项目批准口令门禁的回复。

当前批准路线：

- `#配置推荐`：仅限电脑配置、大学新生购机、笔记本/台式机选购、DIY 装机、硬件兼容性、预算配置、游戏/AI/仿真性能、电商比价或购买渠道。未通过该路线时，按电脑配置推荐技能的兜底规则处理。
- `#集院问答`：仅限新生生活、学业课程、竞赛科研，以及基于已提供资料的校园问答。带口令但越界时只发送范围说明；资料不足时说明无法确认并建议查看官方通知或咨询辅导员、教务/教学办。

不得因为用户发起 QQ 好友消息、私信、群消息或聊天内容，就绕过本项目门禁变成通用 AI 问答。

## 适用场景

- 用户要给普通 QQ 好友发消息。
- 用户明确说不是 QQ 频道，而是 QQ 好友聊天。
- 本机 Windows QQ 客户端已经登录，并且好友可以通过昵称或备注名搜索到。

## 硬性安全规则

1. 用户要求发送 QQ 好友消息或文件时，先向用户确认目标好友和内容/文件。
2. 用户确认后，自动调用 `send` 或 `send-file` 完成发送，不再要求用户手动点击 QQ 的发送按钮。
3. 如果用户只要求草稿、预填、检查，才使用 `fill`，只打开会话并填入消息，不发送。
4. 使用 `send` 时必须传入确认文本：`--confirm-text "发送给<昵称>"`；使用 `send-file` 时必须传入确认文本：`--confirm-text "发送文件给<昵称>"`。
5. 不支持群聊、批量群发、营销骚扰或绕过平台限制。
6. 找不到好友、搜索结果不可靠、无法确认当前会话时必须停止，不要猜测目标。
7. 不要在日志或最终回复中复述长消息全文；只说明成功填入/发送或失败原因。

## 依赖

需要 Windows + Python 3.8+，并安装：

```bash
pip install pywinauto pyperclip
```

不要自动安装依赖；如果脚本提示缺依赖，告诉用户运行上面的命令。

## 命令

所有命令从项目根目录执行。

### 环境检查

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py check
```

### 控件树调试

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py inspect --depth 3
```

### 安全预填（默认推荐）

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py fill \
  --nickname "纯乎一芯" \
  --message "消息内容"
```

执行后应停在 QQ 输入框，消息已填入但未发送。

### 明确确认后发送

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py send \
  --nickname "纯乎一芯" \
  --message "消息内容" \
  --confirm-text "发送给纯乎一芯"
```

### 明确确认后发送文件

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py send-file \
  --nickname "纯乎一芯" \
  --file "g:/My_code/trae_solo/QQ_auto_Q&A/freshman-pc-recommendation-20260527.pdf" \
  --confirm-text "发送文件给纯乎一芯"
```

默认倒计时 3 秒后用 Enter 触发发送。如果用户 QQ 设置为 Ctrl+Enter 发送，可增加：

```bash
--send-keys "^{ENTER}"
```

## 故障处理

- 未找到 QQ 窗口：请用户先打开并登录 Windows QQ。
- 缺依赖：提示 `pip install pywinauto pyperclip`。
- 无法确认会话：不要发送，建议先运行 `inspect` 查看当前 QQ 版本控件树，或让用户手动打开目标聊天后再尝试。
- 多个 QQ/TIM 窗口：使用 `--title-hint` 指定窗口标题关键词。
