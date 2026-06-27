# Browser Mouse Control（鼠标控制）

## English

Browser Mouse Control（鼠标控制） is a Codex skill and companion toolkit for authorized browser automation with precise browser-side mouse control. It combines CloakBrowser, Playwright, Chrome DevTools Protocol, browser screenshots, DOM checks, network-aware validation, and speed-profiled mouse movement.

The main idea is simple: before running a full crawler or web task, Codex should first plan the browsing route, inspect the page visually and structurally, run a tiny end-to-end test, fix the fragile points, and only then scale into a complete script.

This project was built from hands-on tests around browser-side mouse precision. The result: for web pages, Playwright/CDP events inside CloakBrowser can be fast, precise, and repeatable. System-level desktop mouse control is more fragile because it depends on permissions, monitor scaling, focus, and operating-system coordinates.

### What It Is For

- Authorized web automation and browser task scripting.
- Internal tools, admin panels, local pages, and stable web applications.
- Crawler prototyping where the agent first observes, tests, corrects, and then scales.
- Workflows that depend on hover, mouse movement, drag, wheel scrolling, lazy loading, or visible page state.
- Automation that needs selectable speed profiles: fast, natural, and careful.

### What It Is Not For

This project is not intended to bypass login, CAPTCHA, access controls, paywalls, or website rules. If a site requires authorization, the user should complete the required login or verification manually in the browser. Codex can then continue from that authorized browser state.

### Features

- Launch CloakBrowser from Python.
- Connect to a Chrome DevTools Protocol endpoint such as `http://127.0.0.1:9222`.
- Control browser-side mouse movement, clicks, drag actions, hover states, and scrolling.
- Save screenshots at important phases.
- Validate state changes with DOM, URL, text, list counts, screenshots, or network results.
- Run a tiny proof loop before running a complete crawler.
- Keep logs, output JSON, screenshots, and recovery hints.
- Package the workflow as a Codex skill under `skill/browser-mouse-control`.

### Speed Profiles

#### `fast`

For owned sites, internal dashboards, local pages, and stable tools.

- Minimal mouse steps.
- Almost no pauses.
- Minimal screenshots.
- Fastest mode after the workflow is already proven.

#### `natural`

The default profile for ordinary web collection.

- Curved mouse paths.
- Short human-like pauses.
- Screenshots after key phases.
- DOM checks after clicks, drags, scrolls, and navigation.
- Retries for obvious transient failures.

#### `careful`

For complex, changing, or risk-sensitive flows where reliability matters more than raw speed.

- Slower mouse paths.
- More screenshots and DOM checks.
- Retry and recovery hints.
- Better audit trail for debugging and resuming.

### Repository Layout

```text
browser-mouse-control/
  README.md
  requirements.txt
  assets/
    mouse_precision_test.html
  examples/
    fast-result.example.json
    fast-final.example.png
  references/
    workflow.md
  scripts/
    run_mouse_precision_profile.py
    run_mouse_precision_fast.py
    run_mouse_precision_test.py
    save_google_sunset_images.py
    start_cloakbrowser_9222.py
  skill/
    browser-mouse-control/
      SKILL.md
      agents/openai.yaml
      assets/
      references/
      scripts/
```

### Install On macOS Or Linux

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cloakbrowser install
```

Verify:

```bash
python scripts/run_mouse_precision_profile.py --list-profiles
python scripts/run_mouse_precision_profile.py --profile fast
```

### Install On Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cloakbrowser install
```

If PowerShell blocks virtual environment activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then reopen PowerShell and verify:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\run_mouse_precision_profile.py --list-profiles
python scripts\run_mouse_precision_profile.py --profile fast
```

### Install As A Codex Skill

Copy `skill/browser-mouse-control` into your Codex user skills directory.

macOS:

```bash
mkdir -p ~/.codex/skills
cp -R skill/browser-mouse-control ~/.codex/skills/
```

Windows PowerShell when `CODEX_HOME` is set:

```powershell
New-Item -ItemType Directory -Force "$env:CODEX_HOME\skills"
Copy-Item -Recurse ".\skill\browser-mouse-control" "$env:CODEX_HOME\skills\"
```

Restart Codex after copying the skill.

### Launch CloakBrowser On CDP Port 9222

```bash
python scripts/start_cloakbrowser_9222.py
```

Keep that terminal running. Verify from another terminal:

```bash
curl http://127.0.0.1:9222/json/version
```

Windows PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:9222/json/version
```

Connect with Playwright:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.new_page()
    page.goto("https://example.com")
    print(page.title())
```

### Run The Mouse Precision Test

```bash
python scripts/run_mouse_precision_profile.py --profile fast
python scripts/run_mouse_precision_profile.py --profile natural
python scripts/run_mouse_precision_profile.py --profile careful
```

Expected pass criteria:

- All 8 click targets are hit.
- Drag reaches at least 85%.
- Scroll reaches at least 85%.
- Results are written to `output/mouse_precision_profiles/<profile>/`.

### Example: Save Three Sunset Images

```bash
python scripts/save_google_sunset_images.py
```

Custom output directory:

```bash
python scripts/save_google_sunset_images.py --output-dir "$HOME/Desktop/sunset"
```

Windows PowerShell:

```powershell
python scripts\save_google_sunset_images.py --output-dir "$env:USERPROFILE\Desktop\sunset"
```

### Recommended Workflow

1. Plan the browsing path and expected output.
2. Open the site in CloakBrowser or connect to a CDP endpoint.
3. Capture screenshots and inspect the DOM.
4. Build a tiny end-to-end loop.
5. Fix selectors, waits, mouse paths, and scroll targeting.
6. Run a small batch.
7. Add logs, screenshots, retries, and resume points.
8. Run the full job and hand off the output files.

See `references/workflow.md` for more practical guidance.

## 中文

Browser Mouse Control（鼠标控制）是一个给 Codex 使用的网页鼠标控制 Skill / 工具包。它把 CloakBrowser、Playwright、Chrome DevTools Protocol、截图、DOM 检查、网络状态校验和分档鼠标控制整合在一起。

核心思路是：真正执行完整任务之前，先规划浏览路径，观察网页截图和 DOM，跑一个最小闭环，修正脆弱点，然后再扩展成完整脚本。

这个项目来自一次实际测试：目标不是单纯下载图片，而是验证“浏览器层鼠标控制”能不能足够灵敏、精准、可复用。结论是：在网页端，通过 CloakBrowser + Playwright/CDP 可以做到很快、很稳定；而桌面系统层直接挪动 macOS/Windows 鼠标更容易受权限、坐标缩放、窗口焦点影响。

### 适合做什么

- 授权范围内的网页自动化、后台系统操作、内部工具批处理。
- 在写完整爬虫前，先让 Codex 自己观察页面、截图、读 DOM、测试一次小流程。
- 需要鼠标轨迹、hover、拖拽、滚动、懒加载触发的网页任务。
- 需要在“极速 / 自然 / 谨慎”三种节奏之间切换的采集或测试流程。
- 把一次手动浏览流程包装成可复跑、可校验、可恢复的脚本。

### 不适合做什么

这个 Skill 不用于绕过登录、验证码、付费墙、访问控制或网站规则。遇到需要授权的场景，应由用户在浏览器里手动完成登录、验证或授权，然后 Codex 再从已授权的浏览器状态继续执行。

### 核心功能

- **CloakBrowser 启动**：安装并启动真实 Chromium 环境。
- **Playwright/CDP 连接**：可直接通过 `cloakbrowser.launch()` 控制，也可连接 `http://127.0.0.1:9222` 这类调试端口。
- **浏览器层鼠标控制**：在页面内执行移动、点击、拖拽、滚轮和 hover，不依赖系统鼠标可见位置。
- **三档速度模式**：`fast`、`natural`、`careful`，分别对应极速、自然、谨慎。
- **截图与状态校验**：关键步骤保存截图，并用 DOM、URL、文本、列表数量或网络结果确认动作是否成功。
- **小循环优先**：先跑一个最小闭环，再扩展成完整任务。
- **失败处理**：失败时保存截图、状态、日志，并为重试和断点恢复留证据。
- **示例脚本**：包含鼠标精度测试、CDP 启动、Google 图片示例保存。

### 安装：macOS / Linux

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cloakbrowser install
```

验证安装：

```bash
python scripts/run_mouse_precision_profile.py --list-profiles
python scripts/run_mouse_precision_profile.py --profile fast
```

### 安装：Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cloakbrowser install
```

如果 PowerShell 不允许激活虚拟环境，先执行一次：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新打开 PowerShell，回到项目目录，再执行：

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\run_mouse_precision_profile.py --list-profiles
python scripts\run_mouse_precision_profile.py --profile fast
```

### 安装成 Codex Skill

把 `skill/browser-mouse-control` 这个文件夹复制到 Codex 的用户 Skills 目录。

macOS：

```bash
mkdir -p ~/.codex/skills
cp -R skill/browser-mouse-control ~/.codex/skills/
```

Windows PowerShell 中，如果设置了 `CODEX_HOME`：

```powershell
New-Item -ItemType Directory -Force "$env:CODEX_HOME\skills"
Copy-Item -Recurse ".\skill\browser-mouse-control" "$env:CODEX_HOME\skills\"
```

复制后重启 Codex 会话，看到 `browser-mouse-control` 即可使用。

### 三档速度模式

#### 极速档：`fast`

适合后台系统、自己的网站、本地页面、稳定工具页。它追求接近测试时看到的高速效果：

- 鼠标路径短，移动步数少。
- 点击和拖拽几乎不加等待。
- 只保留最终截图和必要状态。
- 适合已知页面、固定按钮、稳定表单、内部工具。

#### 自然档：`natural`

适合普通网站采集，是默认建议档位：

- 鼠标轨迹更像真人，有短暂停顿。
- 点击、滚动、拖拽后会检查页面状态。
- 每个关键阶段保存截图。
- 适合搜索、翻页、打开详情、提取列表等常规任务。

#### 谨慎档：`careful`

适合结构复杂、风控强、容易变化、需要审计证据的站点：

- 鼠标移动更慢，轨迹更完整。
- DOM 检查次数更多。
- 失败后会尝试重试。
- 保留截图、日志和恢复线索。
- 适合复杂下拉菜单、懒加载、分页、详情页、容易变化的页面。

### 启动 CloakBrowser CDP 端口

```bash
python scripts/start_cloakbrowser_9222.py
```

保持这个终端窗口运行。然后在另一个终端验证：

```bash
curl http://127.0.0.1:9222/json/version
```

Windows PowerShell：

```powershell
Invoke-RestMethod http://127.0.0.1:9222/json/version
```

### 鼠标精度测试

```bash
python scripts/run_mouse_precision_profile.py --profile fast
python scripts/run_mouse_precision_profile.py --profile natural
python scripts/run_mouse_precision_profile.py --profile careful
```

通过标准：

- 8 个点击目标全部命中。
- 拖拽进度达到 85% 以上。
- 滚动进度达到 85% 以上。
- 输出写入 `output/mouse_precision_profiles/<profile>/`。

### 示例：保存 3 张日落图片

```bash
python scripts/save_google_sunset_images.py
```

默认会保存到桌面。也可以指定输出目录：

```bash
python scripts/save_google_sunset_images.py --output-dir "$HOME/Desktop/sunset"
```

Windows PowerShell：

```powershell
python scripts\save_google_sunset_images.py --output-dir "$env:USERPROFILE\Desktop\sunset"
```

### 推荐工作流

1. 规划页面顺序：入口页、搜索页、列表页、详情页、导出页。
2. 打开 CloakBrowser，先手动或半自动走一遍页面。
3. 截图并读取 DOM，找稳定选择器、按钮、列表、分页和懒加载区域。
4. 写一个最小脚本，只完成一次搜索、一次点击、提取一条数据。
5. 根据失败点修正鼠标路径、等待条件、滚动位置和选择器。
6. 扩成小批量，并保留截图、日志、失败样本。
7. 通过后再跑完整脚本。
8. 完成后导出结果，再按需要上传云盘或发送邮件。

更多细节见 `references/workflow.md`。
