# QQ_auto_Q-A

QQ_auto_Q-A 是一个面向 Claude Code 的本地技能项目，主要围绕中国电商检索、商品比价、大学新生电脑配置推荐，以及 Markdown 转 PDF 报告生成等场景组织。

## 项目内容

本仓库主要包含以下内容：

- `.claude/skills/cn-ecommerce-search-v2/`：中国电商平台搜索技能。
- `.claude/skills/taobao-shop-price/`：全网商品检索、比价、优惠券和购买链接获取技能。
- `.claude/skills/ecommerce-price-comparison/`：京东、淘宝、天猫、拼多多等平台价格比较技能。
- `.claude/skills/freshman-pc-recommender/`：大学新生电脑配置推荐总控技能，可结合电商检索并生成配置报告。
- `.claude/skills/md2pdf/`：Markdown 转专业排版 PDF 的工具技能。
- `资料/`：项目相关研究资料。
- `下载/`：技能包或依赖资源压缩包。
- `freshman-pc-recommendation-20260527.md` / `freshman-pc-recommendation-20260527.pdf`：示例电脑配置推荐报告。
- `QQ_auto_Q-A-20260527.zip`：项目完整打包文件。

## 环境要求

- Git
- Claude Code
- Python 3.8+
- 可选 Python 依赖：
  - `reportlab`：用于 `md2pdf` 生成 PDF。
  - `requests`、`beautifulsoup4`：用于部分电商抓取脚本。

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

如果你直接在本仓库目录中运行 Claude Code，通常无需额外复制，Claude Code 会读取项目内的 `.claude/skills/`。

如果需要安装到其他项目，可复制整个技能目录：

```bash
cp -r .claude/skills /path/to/your-project/.claude/
```

在 Windows PowerShell 中可使用：

```powershell
Copy-Item -Recurse .claude\skills C:\path\to\your-project\.claude\
```

复制完成后，在目标项目中重新打开 Claude Code 或刷新会话。

## Python 依赖安装

基础电商检索脚本 `taobao-shop-price/scripts/price.py` 只依赖 Python 标准库，一般无需安装额外依赖。

如果需要使用 Markdown 转 PDF：

```bash
pip install reportlab
```

如果需要运行京东抓取示例脚本：

```bash
pip install requests beautifulsoup4
```

## 使用示例

### 全网比价

在 Claude Code 中提出类似需求：

```text
帮我比价 iPhone 16 Pro，看看淘宝、京东、拼多多哪个更便宜
```

会触发 `taobao-shop-price` 或相关电商检索技能。

### 新生电脑推荐

```text
我是集成电路专业准大一新生，预算 8000 元，帮我推荐电脑并生成 PDF 报告
```

会触发 `freshman-pc-recommender`，按预算、专业、便携、游戏、AI/仿真等维度生成方案。

### Markdown 转 PDF

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
├── .claude/
│   └── skills/
│       ├── cn-ecommerce-search-v2/
│       ├── ecommerce-price-comparison/
│       ├── freshman-pc-recommender/
│       ├── md2pdf/
│       └── taobao-shop-price/
├── 下载/
├── 资料/
├── freshman-pc-recommendation-20260527.md
├── freshman-pc-recommendation-20260527.pdf
└── QQ_auto_Q-A-20260527.zip
```

## 注意事项

- 电商价格会频繁变化，技能输出的价格和购买建议仅供参考，下单前应再次核对价格、店铺、售后和库存。
- 部分电商平台可能存在访问限制、反爬策略或地区差异，检索结果可能不完整。
- 生成 PDF 时，如包含中文内容，建议在支持中文字体的系统环境下运行。
- 仓库中包含示例报告和技能评测材料，可按需保留或清理。

## 许可证

当前仓库未声明统一许可证。若要公开复用或分发，请先补充 LICENSE 文件并确认各技能包来源与授权。
