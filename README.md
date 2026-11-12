# 留白 · 本地阅读与提问原型

一个可实际运行的最小闭环：**导入 → 阅读 → 选中原文 → 保存问题 → 继续追问 / 记录回答 → 追加新理解 → 导出 Obsidian 笔记与原件。**

## 启动（macOS / Linux / Windows）

需要 Python 3.10+。在此文件夹打开终端：

```sh
python3 -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell 改用：.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

浏览器打开 **http://127.0.0.1:8765**。Windows 可用 `python` 替换 `python3`。已装 PyMuPDF 时可直接运行 `./run.sh`。

数据在 `data/`（SQLite + 原文件），退出终端只停止服务，不删除内容。备份时停止程序后复制整个 `data/`。不依赖浏览器缓存保存笔记；浏览器仅记住上次打开的书和页。移动数据库与原件时须一并移动。

可用环境变量 `PORT=8766` 更改端口，`READING_DATA=/你的路径` 更改存储目录。默认只监听本机，**不应直接部署至公网或多用户环境**。原型没有账户系统，任何能使用此电脑 / 此目录的人都可能访问这些数据。

## 三分钟体验

1. 点击「导入 PDF / EPUB」，选择 `samples/带着问题读书.epub` 或 `samples/A-small-reading-experiment.pdf`。
2. 在正文拖选一句话，点击「围绕这段提问」，输入问题并保存。
3. 在右侧同一条摘录下继续输入，分别点击「追问」「记录回答」「追加理解」。最初的问题不会被新问题覆盖。
4. 点击「回到原文」，返回正确章节 / 页，并高亮该摘录。关闭浏览器、重启服务后仍可定位。
5. 点击「导出」，解压 ZIP 后把**整个文件夹**放到 Obsidian 仓库。打开「阅读笔记.md」。包含原件、问答、理解、SHA-256、位置记录、可离线打开的 `source.html`。

「回到原文位置」指向导出阅读副本的精确摘录锚点；PDF 原件链接带 `#page=N`。EPUB 原文件也附带，但不同外部阅读器不统一支持深链接，因此不承诺外部阅读器跳转；导出的 HTML 始终是无服务器依赖的定位副本。

## AI：真实可配置，没有假回答

默认**没有联网 AI**，问题和追问会照常保存，回答可手动记录。点击 AI 按钮会明确提示未配置，不会返回预置答案。

若你决定使用自己的 OpenAI API 账户，可仅在本地终端设置：

```sh
export OPENAI_API_KEY='你的密钥'
export OPENAI_MODEL='gpt-4.1-mini'
python app.py
```

PowerShell 使用 `$env:OPENAI_API_KEY = '你的密钥'`。不要把密钥写进源码或笔记。模型名可换成账户可用的 Chat Completions 模型。密钥不发送到浏览器，也不入库。每次点击 AI 都先确认：**将当前摘录及该摘录的整条问答记录发送给 OpenAI `api.openai.com`**；不会自动上传整本书。可能产生 API 费用。接口失败时已有问题保留，可重试。书籍内容作为待分析资料处理，答案可能出错。

本次交付未配置密钥，因此 **未验证真实模型请求、额度、质量或计费**，只验证了缺少密钥的诚实失败和本地问答保存流程。

## 默认选择与取舍

| 路线 | 优点 | 本次选择 |
|---|---|---|
| 现成阅读器 + 独立聊天 + 笔记软件 | 最少开发，原书展示成熟 | 多次复制粘贴、问题演化和原文位置容易断开，不作为闭环原型 |
| Electron + PDF.js + epub.js | 完整版式、EPUB CFI、桌面体验更强 | 后续产品化候选，首版安装和构建更重 |
| 本地 Python 服务 + 浏览器 + SQLite | 安装轻、无账号、可离线、数据可备份 | **本次采用**。PDF 复用成熟的 PyMuPDF，EPUB 按标准 spine 读取正文 |

位置以「原文件 SHA-256 + PDF 页 / EPUB spine 章节 + Unicode 字符范围 + 引用及前后文」保存。导入相同字节的文件不会重复创建书籍。换版或修改原文件会作为新书，不把旧锚点静默套到新版本。

## 已知边界

- 阅读是**提取文字的重排视图**，不是原书排版复刻。复杂多栏 PDF、数学公式、脚注顺序可能不完美；可「打开原文件」对照。EPUB 图片、音视频、复杂表格、交互内容未展示。
- 不支持 DRM / 密码 PDF；扫描 PDF 返回明确提示。纸书 OCR 留待后续，不包括微信读书抓取或自动同步。
- 标准 UTF-8 EPUB 可读；非常规路径、旧编码和特殊出版社文件可能不兼容。文件限制 30 MB，PDF 2000 页，EPUB 解压 100 MB。
- 锚点是本原型的不可变提取文本定位，**不是 EPUB CFI、PDF 字形坐标**。暂不跨版本自动重定位。
- 一台电脑上的个人原型：无同步、多人协作、完整搜索、笔记删除/编辑、撤销、自动整理主题或整书检索增强。
- 导出是快照，不会后台写入 Obsidian；追加内容后需再次导出。某些 Obsidian 配置可能把 HTML 链接交给外部浏览器，这是预期的降级方式。
- EPUB/PDF 是不可信输入；设有尺寸限制，但这不是经过安全审计的文档沙箱。只导入可信来源文件。

## 文件与测试

- `app.py`：本地 API、解析、SQLite、导出、可选真实 AI。
- `static/`：中文阅读与摘录问答界面。
- `samples/`：为此原型创作的 CC0 试读文本，无第三方版权内容。`make_samples.py` 仅用于再生成样本，需要额外安装 reportlab；正常运行不需要。
- `tests/`：端到端验证脚本与报告（依赖 Python Playwright 和 Chromium，仅测试需要）。
- `requirements.txt`：运行依赖。PyMuPDF 有 AGPL / 商业许可，若产品化分发，应评估许可或选择合适替代方案。

此交付未发布网站、未上传你的书、未创建外部账号。

### 本次验证结果

已运行 `python tests/qa_api.py`：两种格式的导入、选区定位、问答保存、并发写入、导出完整性和异常输入全部通过。该脚本调用真实 HTTP handler / 解析 / SQLite / 导出实现，但在进程内运行，**不等同于浏览器端到端测试**。

`node --check static/app.js` 和 Python 编译检查通过。提供 `tests/qa_browser.py` 供有 Chromium 的本机运行（先启动 app，再安装 Playwright Python 包）。此环境的 Chromium 因 socket 权限失败，备用云浏览器也无法访问执行环境的 localhost；因此没有声称已完成 UI 点击、视觉布局、真实 Obsidian 打开或真实 AI 调用验证。详细覆盖见 `tests/QA_REPORT.md`。
