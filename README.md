# QQ_auto_Q-A

QQ_auto_Q-A 是一个面向 Claude Code 的本地技能项目，用于组织 QQ/腾讯频道自动问答、校园问答、大学新生电脑配置推荐、中国电商检索比价，以及 Markdown 转 PDF 报告生成等能力。

项目内已配置严格的自动回复门禁：面向 QQ、QQ群、QQ 频道、帖子、评论、私信等外部消息时，只有匹配已批准口令且问题属于对应范围，才允许进入自动问答流程。

## 核心能力

- QQ 好友消息 GUI 自动化：在 Windows 本机 QQ 客户端中打开普通好友单聊、填入消息，并在用户确认后发送。
- 腾讯频道社区管理：支持频道管理、帖子/评论/回复、成员管理、频道私信、通知处理和内容巡检。
- 校园问答：仅处理带 `#集院问答` 的新生生活、学业课程、竞赛科研，以及基于已提供资料的校园问答。
- 新生电脑配置推荐：仅处理带 `#配置推荐` 且属于电脑配置、购机、DIY、兼容性、预算、电商比价等范围的问题。
- 中国电商检索和比价：支持淘宝/天猫、京东、拼多多、苏宁、唯品会、考拉、抖音、快手、1688 等平台的商品检索与价格比较。
- Markdown 转 PDF：把 Markdown 报告转换为支持中文排版、目录、水印和主题样式的 PDF。

## 自动回复门禁

本项目的自动问答路线只批准以下两类：

| 口令 | 允许范围 | 越界处理 |
| --- | --- | --- |
| `#配置推荐` | 大学新生购机、笔记本/台式机选购、DIY 装机、硬件兼容性、预算配置、游戏/AI/仿真性能、电商比价或购买渠道 | 非电脑配置相关问题返回固定兜底文本 |
| `#集院问答` | 新生生活、学业课程、竞赛科研，以及基于用户已提供资料的校园问答 | 只说明当前支持范围；资料不足时说明无法确认并建议咨询官方渠道 |

电商检索、比价、PDF 生成、QQ/频道发送等能力只能作为上述已批准路线的辅助能力，不能因单独出现商品、链接、PDF、QQ、频道、学校、课程等关键词而绕过门禁。

## 项目内容

本仓库主要包含以下内容：

- `.claude/skills/tencent-channel-community/`：腾讯频道（QQ 频道）社区管理、通知处理、帖子/评论/回复和频道私信技能。
- `.claude/skills/qq-friend-message/`：Windows 本机 QQ 普通好友消息 GUI 自动化技能。
- `.claude/skills/campus-qa/`：集院/校园问答技能。
- `.claude/skills/freshman-pc-recommender/`：大学新生电脑配置推荐总控技能。
- `.claude/skills/cn-ecommerce-search-v2/`：中国电商平台搜索技能。
- `.claude/skills/taobao-shop-price/`：全网商品检索、比价、优惠券和购买链接获取技能。
- `.claude/skills/ecommerce-price-comparison/`：京东、淘宝、天猫、拼多多等平台价格比较技能。
- `.claude/skills/md2pdf/`：Markdown 转专业排版 PDF 的工具技能。
- `.claude/skills/*-workspace/`：部分技能的评测、迭代和辅助材料。
- `CLAUDE.md`：项目级规则和维护解锁门禁。
- `资料/`：项目相关研究资料、问答资料或文档。
- `下载/`：技能包或依赖资源压缩包。
- `freshman-pc-recommendation-20260527.md` / `freshman-pc-recommendation-20260527.pdf`：示例电脑配置推荐报告。
- `QQ_auto_Q-A-20260527.zip`：项目打包文件。

## 环境要求

- Git
- Claude Code
- Python 3.8+
- Windows + 已登录 QQ 客户端：仅 QQ 好友消息 GUI 自动化需要
- Node.js / npm：仅腾讯频道 CLI 安装或升级需要
- 可选 Python 依赖：
  - `pywinauto`、`pyperclip`：QQ 好友消息 GUI 自动化。
  - `reportlab`：Markdown 转 PDF。
  - `requests`、`beautifulsoup4`：部分电商抓取脚本。

## 安装方式

### 方式一：克隆仓库

```bash
git clone https://github.com/447662/QQ_auto_Q-A.git
cd QQ_auto_Q-A
```

### 方式二：下载压缩包

也可以直接下载仓库中的：

```text
QQ_auto_Q-A-20260527.zip
```

解压后进入项目目录即可。

## 安装 Claude Code 技能

本项目的技能目录已经按 Claude Code 的项目级技能结构放在 `.claude/skills/` 下。

如果直接在本仓库目录中运行 Claude Code，通常无需额外复制，Claude Code 会读取项目内的 `.claude/skills/`。

如果需要安装到其他项目，可复制整个技能目录：

```bash
cp -r .claude/skills /path/to/your-project/.claude/
```

Windows PowerShell 可使用：

```powershell
Copy-Item -Recurse .claude\skills C:\path\to\your-project\.claude\
```

复制完成后，在目标项目中重新打开 Claude Code 或刷新会话。

## 依赖安装

### QQ 好友消息自动化

```bash
pip install pywinauto pyperclip
```

运行环境检查：

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py check
```

### 腾讯频道 CLI

```bash
npm install -g tencent-channel-cli
```

检查版本和登录状态：

```bash
tencent-channel-cli version
tencent-channel-cli login status
tencent-channel-cli doctor
```

### Markdown 转 PDF

```bash
pip install reportlab
```

### 电商抓取脚本

基础电商检索脚本 `.claude/skills/taobao-shop-price/scripts/price.py` 只依赖 Python 标准库，一般无需安装额外依赖。

如需运行京东抓取示例脚本：

```bash
pip install requests beautifulsoup4
```

## 使用示例

### QQ 好友消息

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py fill \
  --nickname "好友昵称" \
  --message "消息内容"
```

确认发送后：

```bash
python .claude/skills/qq-friend-message/scripts/qq_send.py send \
  --nickname "好友昵称" \
  --message "消息内容" \
  --confirm-text "发送给好友昵称"
```

### 腾讯频道管理

```bash
tencent-channel-cli manage get-guild-info --guild-id 频道ID
```

复杂参数可使用 stdin JSON：

```bash
echo '{"guild_id":"123"}' | tencent-channel-cli manage get-guild-info --json
```

### 集院校园问答

```text
#集院问答 新生报到要提前准备什么？
```

该路线只输出文本，不生成 PDF，不调用电商检索，也不会主动发送 QQ/频道消息。

### 新生电脑推荐

```text
#配置推荐 我是集成电路专业准大一新生，预算 8000 元，帮我推荐电脑并生成 PDF 报告
```

该路线会按预算、专业、便携、游戏、AI/仿真等维度生成方案，并可结合电商检索与比价。

### 全网比价

```text
#配置推荐 帮我比价 RTX 5070 Ti 显卡，看看淘宝、京东、拼多多哪个更合适
```

电商检索和比价应作为电脑配置推荐路线的辅助能力使用。

### PDF 生成示例

```bash
python .claude/skills/md2pdf/scripts/md2pdf.py \
  --input freshman-pc-recommendation-20260527.md \
  --output freshman-pc-recommendation-20260527.pdf \
  --title "大学新生电脑配置推荐" \
  --theme warm-academic
```

## 目录结构

```text
.
├── CLAUDE.md
├── README.md
├── .claude/
│   └── skills/
│       ├── campus-qa/
│       ├── cn-ecommerce-search-v2/
│       ├── ecommerce-price-comparison/
│       ├── freshman-pc-recommender/
│       ├── md2pdf/
│       ├── qq-friend-message/
│       ├── taobao-shop-price/
│       └── tencent-channel-community/
├── 下载/
├── 资料/
├── freshman-pc-recommendation-20260527.md
├── freshman-pc-recommendation-20260527.pdf
└── QQ_auto_Q-A-20260527.zip
```

## 维护说明

- 项目维护、代码修改、技能修改、调试、提交、发布等开发操作必须遵守 `CLAUDE.md` 中的维护解锁门禁。
- 删除文件、删除帖子、踢人、禁言、发送 QQ/频道消息等高风险或外部可见操作需要先确认。
- QQ/频道自动问答不得扩展成通用聊天机器人。
- 校园问答资料不足时必须说明无法确认，不能编造政策、日期、课程替代、教师安排、宿舍规则或竞赛名额。

## 注意事项

- 电商价格会频繁变化，技能输出的价格和购买建议仅供参考，下单前应再次核对价格、店铺、售后和库存。
- 部分电商平台可能存在访问限制、反爬策略或地区差异，检索结果可能不完整。
- 腾讯频道操作需要有效登录状态；鉴权失败时应按 CLI 登录流程重新扫码授权。
- QQ 好友消息自动化依赖本机 QQ 客户端窗口和控件结构，找不到好友或无法确认会话时应停止发送。
- 生成 PDF 时，如包含中文内容，建议在支持中文字体的系统环境下运行。

## 许可证

当前仓库未声明统一许可证。若要公开复用或分发，请先补充 LICENSE 文件并确认各技能包来源与授权。
