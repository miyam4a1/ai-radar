# 刷新手册（refresh playbook）

## 0. 一次性准备（Miya 的 Mac，M3）
```bash
git clone https://github.com/miyam4a1/ai-radar.git && cd ai-radar
python3 -m pip install -U yt-dlp pillow     # 或 brew install yt-dlp
gh auth status                              # 必须是 miyam4a1；否则 gh auth login
```
- 在家里网络（住宅 IP）跑效果最好。云服务器上 TikTok 常返回 429、「Your IP address is blocked」或空数据。
- yt-dlp 每隔几周要更新一次（`pip install -U yt-dlp`），TikTok 改版后旧版会失效。

## 1. 刷新数字 + 查死链
```bash
python3 scripts/refresh_tiktok.py --dry-run     # 先看会改什么
python3 scripts/refresh_tiktok.py               # 写入 data/live.json + reports/refresh-<日期>.json
```
- 更新每张卡的 `st`（播放 / 赞 / 分享 / 评论）和 `st.rd`（采集日期），以及 `rx` 里 `@账号 · N 播放 · 日期` 格式的播放数。
- `st.via` 有值（第三方数字，如 Instagram 赞数）的卡不改数字，只查视频是否还在。
- 输出 `DEAD`：视频被删 / 设为私密。换一条同趋势的代表视频，或删卡（同步删周报引用）。
- 输出 `ERROR`：多半是限流或 IP 被拦，隔几分钟重跑；私密视频在 yt-dlp 里有时也显示为「IP blocked」，用浏览器打开确认。
- 脚本不会删卡、不会改文案。

## 2. 核实候选视频
```bash
python3 scripts/refresh_tiktok.py --probe <URL> [<URL> ...]   # 打印播放、赞、分享、评论、发布日期、音频名
python3 scripts/refresh_tiktok.py --thumb <k> <URL>            # 生成 assets/live/<k>.webp
```
新卡的 `st.rd` 写当天；`sd` 用 probe 出来的发布日期。

## 3. 找新候选
按 `docs/taste-profile.md` 的 8 个类型找，每类至少看 2 个来源；先处理 `data/seeds.json` 里的线索。每个候选都要过 `docs/curation-rules.md`：真火 + 2–3 条不同账号的二创（或第三方视频数）+ 写得出具体的「可借鉴」+ 6 周内走红。

## 4. 粘贴给 Codex 的提示词
```
你在 ai-radar 仓库里工作。先完整阅读 AGENTS.md 和 docs/ 下全部文件（curation-rules.md、taste-profile.md、refresh-playbook.md），以及 data/seeds.json、data/live.json、weeks/index.json 和当前这一期 weeks/*.json。然后按顺序做：

1. 刷新：运行 python3 scripts/refresh_tiktok.py --dry-run，再正式运行。列出 DEAD / ERROR 的条目；DEAD 的为它找替代代表视频或删卡（同步删当期周报引用）。
2. 核实线索：逐条处理 data/seeds.json，找到真实链接（创作者主页、caption、音频），用 --probe 读数字，找 2–3 条不同账号的二创。更新每条 seed 的 status（verified / added: k / rejected: 原因）。
3. 找新候选：按 taste-profile 的类型，找 10–20 个最近 6 周内走红的候选（TikTok 为主，IG / YouTube Shorts / X 次之，国内最多 1–2 条），列一张表：类型、链接、播放 / 赞 / 分享、发布日期、二创证据、可借鉴、是否通过规则、原因。
4. 只把通过全部规则的加进 data/live.json（字段齐全：what、why、pm、kx、rx、hot、hs、sd、src、m、st、thumb；thumb 用 --thumb 生成）。不要编造任何链接、数字、日期；第三方数字要标来源和读数日期。不改置顶（pin），除非我明确要求。目标保持 20–30 条，删掉退潮或不再满足规则的。
5. 更新当前这一期周报：patterns 只引用 live.json 里的卡；更新 change（升温 / 降温）和 log（最新一行在前，写清增删和原因）；补 cards 和 240×427 的 thumbs。如果今天是周五，按 curation-rules 第 8 节定稿本期并开下一期。
6. 预览：python3 -m http.server 8765，检查 #trends 和 #trends/week 能正常显示、视频能播放。
7. git add -A && git commit -m "radar: refresh <日期>" && git push，等 GitHub Pages 构建完成后确认线上 data/live.json 已更新。
8. 最后给我一个简短报告：新增（附链接和数字来源）、删除（附原因）、seeds 状态、拿不准的点、commit hash。
```

## 5. 只更新 Skills 区（可选，每月一次就够）
```
读 AGENTS.md 和 docs/curation-rules.md 第 6 节。用 gh api 找最近新出现的 ≥10k 星的 Agent Skill 和 AI 创作类项目，实测星数；更新 data/skills.json 已有条目的 s（星数）；新增 3–5 张符合规则的卡并配图（assets/skills/<slug>.webp，640×400）；运行 python3 scripts/build_index.py，预览，提交并推送。
```
