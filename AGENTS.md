# AGENTS.md · AI 雷达（ai-radar）

给 Codex / Claude Code / 任何本地 AI 的交接说明。先读这页，再读 `docs/`：
- `docs/curation-rules.md`：收录规则（必须遵守）
- `docs/taste-profile.md`：Miya 想看的热点视频类型
- `docs/refresh-playbook.md`：每周刷新步骤 + 可直接粘贴的提示词
- `data/seeds.json`：待核实的线索（Miya 截图来的）

## 这是什么
- 线上：https://miyam4a1.github.io/ai-radar/ ，仓库 `miyam4a1/ai-radar`，GitHub Pages 从 `main` 分支根目录发布。
- 主人：Miya（TikTok Live PM，在找 C 端社交 / 内容 / AI PM 岗位）。网站是她的「趋势雷达」，用来积累产品灵感和面试素材。
- 两个 Tab：
  - **世界在 hi 什么**（`#trends`）：海外为主的爆款短视频趋势。「实时」= `data/live.json`，「周报」= `weeks/*.json`。
  - **Skills**（`#skills`）：GitHub 上 ≥10k 星的 Agent Skill 和 AI / 创作类开源项目，数据在 `data/skills.json`。
- 纯静态站：一个 `index.html`（CSS + JS 都在里面），运行时 `fetch` JSON。没有框架、没有 npm。

## 文件结构
| 路径 | 内容 |
|---|---|
| `index.html` | **生成文件**，不要手改。由 `scripts/build_index.py` 用模板 + skills 生成 |
| `src/index.template.html` | 页面模板（样式 + 渲染逻辑）。`__SKILLS__` 占位会被替换成 skills 数据 |
| `data/skills.json` | Skills Tab 的卡片（改完要跑 build） |
| `data/live.json` | 实时趋势卡片 `{updated, rule, items:[…]}`（改完直接提交，不用 build） |
| `assets/live/<k>.webp` | 趋势卡缩略图，360×640 竖图，≤40KB |
| `weeks/index.json` | 周报目录 `{issues:[{id,range,start,end,status}]}`，新一期放最前 |
| `weeks/<YYYY>-W<ww>.json` | 单期周报：`patterns`、`change`、`log`、`cards`、`thumbs` |
| `assets/weeks/<id>/<k>.webp` | 周报缩略图，240×427 |
| `assets/skills/<slug>.webp` | Skill 卡配图，640×400 |
| `data/seeds.json` | 待核实线索，不上页面 |
| `scripts/refresh_tiktok.py` | 刷新数字、检查链接、生成缩略图（yt-dlp） |
| `scripts/build_index.py` | 重新生成 `index.html` |
| `reports/` | 刷新脚本输出的检查报告 |

## 趋势卡片 schema（`data/live.json` → `items[]`）
| 字段 | 必填 | 说明 |
|---|---|---|
| `k` | ✓ | 唯一 key，也是锚点 `#t-<k>`，周报用它引用 |
| `n` | ✓ | 标题 |
| `p` | ✓ | 平台数组，筛选按钮用：`TikTok` `Instagram` `YouTube` `X` `B站` `抖音` `微博` |
| `ai` |  | `1` = AI 生成类（「AI 生成」筛选） |
| `what` / `why` / `pm` | ✓ | 是什么 / 为什么火 / PM 启发，各一句 |
| `kx` | ✓ | **可借鉴**：一句具体的产品功能或玩法（社交 / 创作 / 直播） |
| `rx` | ✓ | **二创证据** `[[文字, 链接, 说明]]`；链接可为空字符串 |
| `hot` | ✓ | 走红时间（展示文本） |
| `hs` | ✓ | 走红日期 `YYYY-MM-DD`，排序用 |
| `sd` | ✓ | 来源日期 = 代表视频发布日期 |
| `src` | ✓ | 来源文章 / 页面链接 |
| `m` | ✓ | 代表视频 `{t: tt|yt|ig|bili|dy, id, o: 原链接, label?, v?: 1=竖屏(yt/bili)}` |
| `st` | ✓ | 主数据 `{pl 播放, lk 赞, sh 分享, cm 评论, plat, rd 采集日期, u 数据链接, via? 非平台来源说明}` |
| `thumb` | ✓ | `assets/live/<k>.webp` |
| `pin` |  | 置顶序号（1 最前），显示「重点」徽标 |
| `vir` |  | 补充数据（文章 / 第三方数字）`[[文字, 链接, 说明]]` |
| `v` |  | 拿不准的点，页面显示「注」徽标 + 悬停文字 |
| `extra` |  | 附加链接 `[文字, 链接]` |
| `cn` |  | `1` = 放进折叠的「国内」区 |

真实例子（2026-10-23 的 `odie`）：
```json
{"k":"odie","n":"腊肠狗跳《Single Ladies》","p":["TikTok"],"ai":1,
 "what":"长毛腊肠 Odie 站 C 位，两位舞者在后面甩头发",
 "why":"一张狗照片 + 参考舞蹈视频，用 AI 动作迁移生成；主人公开了做法",
 "pm":"「照片 + 动作模板」已成标准生产方式：平台可直接把它做成模板工具",
 "kx":"「上传宠物照片 + 选一支舞」的动作迁移模板，生成后一键发起同款挑战",
 "hot":"2026-10-04 起","hs":"2026-10-04","sd":"2026-10-04",
 "src":"https://jumponthetrend.app/trends/single-ladies-dog-ai-trend/",
 "m":{"t":"tt","id":"7692606728323583246","o":"https://www.tiktok.com/@king_odiee/video/7692606728323583246"},
 "st":{"pl":45500000,"lk":5600000,"sh":1200000,"cm":13600,"plat":"TikTok","rd":"2026-10-23",
       "u":"https://www.tiktok.com/@king_odiee/video/7692606728323583246"},
 "rx":[["另一只狗跳同款","https://www.tiktok.com/@_uni_toro/video/7694964183477030151","@_uni_toro · 7.9 万 播放 · 10-10"]],
 "thumb":"assets/live/odie.webp"}
```
排序：页面先按 `pin` 升序，其余按 `hs` 倒序（用户可切「传播指数」「播放」，置顶不动）。

## 周报 schema（`weeks/2026-W44.json`）
`{id, range:"2026-10-26 ~ 10-30", start, end, status:"本周更新中"|"已定稿", patterns:[{t, d, ex:[k…]}], change:{up:[[文字,k]], down:[[文字,k]], note}, log:[最新一行在前], cards:{k:{n, s 短标题}}, thumbs:{k:"assets/weeks/<id>/<k>.webp"}}`。`ex` 和 `change` 里的 k 必须在 `live.json` 里。

## Skill 卡 schema（`data/skills.json`）
```json
{"n":"phuryn/pm-skills","u":"https://github.com/phuryn/pm-skills","s":27259,"cr":"2026-03-01",
 "c":"效率","t":"skill","l":"PM 技能市场：69 个技能 + 42 个工作流",
 "w":"内置 Teresa Torres、Marty Cagan 等框架：/discover、/strategy、/write-prd、/north-star 一路串起来。",
 "use":"和你的面试准备直接相关：用它练产品发现、定指标、写 PRD。","f":"","img":"assets/skills/pm-skills.webp"}
```
`s` 星数（`gh api repos/<owner>/<repo> --jq .stargazers_count` 实测）、`cr` 创建日期（页面用 星数÷天数 算「势头」）、`c` 分类、`t` = `skill` 或 `tool`、`l` 一句话、`w` 是什么、`use` 对 Miya 的用处、`f:"hot"` 标热门。没有图时用 `dg:["输入","过程","输出"]` 代替 `img`。

## 本地预览
```bash
cd ai-radar && python3 -m http.server 8765
# 打开 http://localhost:8765/#trends  （周报：#trends/week，Skills：#skills）
```
不要直接双击 `index.html`：`file://` 下 fetch JSON 会失败，YouTube 嵌入也会报错。

## 发布
```bash
python3 scripts/build_index.py        # 只有改了 src/ 或 data/skills.json 才需要
git add -A && git commit -m "radar: <改了什么>" && git push
gh api repos/miyam4a1/ai-radar/pages/builds/latest --jq '.status+" "+.commit[:7]'   # 等到 built
```
- Mac 上的 `gh` 必须登录为 **miyam4a1**（`gh auth status` 检查；没登录就 `gh auth login`）。云端 box 上的登录不会带过来。
- 推送后 1–2 分钟生效。验证：`curl -s https://miyam4a1.github.io/ai-radar/data/live.json | head -c 200`，再打开页面看实时、周报两页。

## 硬规则（细节见 docs/curation-rules.md）
- 不编造任何链接、数字、日期。第三方数字必须标来源和读数日期。
- 每张趋势卡：可播放的代表视频 + 平台数字 + 二创证据 + 可借鉴，走红在约 6 周内。
- 文案中文、简洁、具体；不写自我评价、不写「本站」「我们」之类的元话语。
- 不要改设计风格（深色高对比文字、左视频右分析）。
- 周末不安排任务；周五是例行更新日。
