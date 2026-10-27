#!/usr/bin/env python3
"""Refresh platform numbers in data/live.json and check that every video / remix link is alive.

Uses yt-dlp (TikTok, YouTube, Instagram) and Bilibili's public API. Run from the repo root:

  pip3 install -U yt-dlp pillow
  python3 scripts/refresh_tiktok.py                 # refresh main numbers (st) of every card + check rx links
  python3 scripts/refresh_tiktok.py --dry-run       # print what would change, write nothing
  python3 scripts/refresh_tiktok.py --keys odie,fan # only these cards
  python3 scripts/refresh_tiktok.py --no-rx         # skip remix links (faster)
  python3 scripts/refresh_tiktok.py --probe URL [URL...]          # print numbers for candidate videos (no write)
  python3 scripts/refresh_tiktok.py --thumb KEY URL               # save assets/live/KEY.webp (360x640) from the video cover

What it writes (unless --dry-run):
  - card.st.pl/lk/sh/cm  <- platform numbers, only when st is the platform's own number (no `via`)
  - card.st.rd           <- today (collection date)
  - rx notes in the auto format "@user · 7.9 万 播放 · 10-10" are re-written with fresh plays
  - data/live.json "updated" <- today
  - reports/refresh-YYYY-MM-DD.json  <- every check, with status ok / dead / error
It NEVER deletes a card. Dead videos are listed in the report and printed as DEAD; a person (or the
agent following docs/curation-rules.md) decides whether to replace the representative video or drop the card.

Works best from a home / residential IP (e.g. Miya's Mac). From cloud IPs TikTok often returns 429 or
empty data; the script backs off and retries, then marks the item `error` (not `dead`).
"""
import argparse, datetime, json, pathlib, re, sys, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = ROOT / 'data/live.json'
TODAY = datetime.date.today().isoformat()
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'
DEAD_PAT = re.compile(r'unavailable|removed|private|not available|status_self_see|10204|10216|deleted|does not exist|404', re.I)

try:
    import yt_dlp
except ImportError:
    sys.exit('yt-dlp missing: pip3 install -U yt-dlp')


def fw(n):
    """Chinese short number used on the site: 79000 -> '7.9 万', 1.2e8 -> '1.2 亿'."""
    if n >= 1e8: return f'{n/1e8:.1f}'.rstrip('0').rstrip('.') + ' 亿'
    if n >= 1e4: return f'{n/1e4:.1f}'.rstrip('0').rstrip('.') + ' 万'
    return f'{n:,}'


def ytdlp_info(url, tries=3):
    opts = {'quiet': True, 'no_warnings': True, 'skip_download': True, 'http_headers': {'User-Agent': UA}}
    last = None
    for a in range(tries):
        try:
            with yt_dlp.YoutubeDL(opts) as y:
                d = y.extract_info(url, download=False)
            return {'status': 'ok', 'pl': d.get('view_count'), 'lk': d.get('like_count'), 'cm': d.get('comment_count'),
                    'sh': d.get('repost_count'), 'user': d.get('uploader') or d.get('channel'),
                    'date': (lambda s: s and f'{s[:4]}-{s[4:6]}-{s[6:]}')(d.get('upload_date')),
                    'track': d.get('track'), 'thumb': d.get('thumbnail'), 'title': (d.get('title') or '')[:120]}
        except Exception as e:
            last = str(e)
            if DEAD_PAT.search(last) and '429' not in last:
                return {'status': 'dead', 'err': last[:200]}
            time.sleep(8 * (a + 1))
    return {'status': 'error', 'err': (last or '')[:200]}


def bili_info(bv):
    req = urllib.request.Request(f'https://api.bilibili.com/x/web-interface/wbi/view?bvid={bv}',
                                 headers={'User-Agent': UA, 'Referer': 'https://www.bilibili.com/', 'Cookie': 'buvid3=infoc'})
    try:
        d = json.loads(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e:
        return {'status': 'error', 'err': str(e)[:200]}
    if d.get('code') != 0:
        return {'status': 'dead' if d.get('code') in (-404, 62002, 62004) else 'error', 'err': str(d.get('message'))}
    v = d['data']; s = v['stat']
    return {'status': 'ok', 'pl': s['view'], 'lk': s['like'], 'sh': s['share'], 'cm': s['reply'], 'user': v['owner']['name'],
            'date': datetime.date.fromtimestamp(v['pubdate']).isoformat(), 'thumb': v['pic'].replace('http://', 'https://'), 'title': v['title']}


def info(url):
    m = re.search(r'bilibili\.com/video/(BV\w+)', url)
    return bili_info(m[1]) if m else ytdlp_info(url)


def video_url(m):
    t, i = m['t'], m['id']
    if t == 'bili': return f'https://www.bilibili.com/video/{i}/'
    if t == 'yt': return f'https://www.youtube.com/watch?v={i}'
    if t == 'ig': return f'https://www.instagram.com/reel/{i}/'
    return m.get('o') or f'https://www.tiktok.com/@_/video/{i}'


def save_thumb(key, url):
    from PIL import Image, ImageOps
    import io
    data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'}), timeout=30).read()
    im = Image.open(io.BytesIO(data)).convert('RGB')
    out = ROOT / f'assets/live/{key}.webp'
    ImageOps.fit(im, (360, 640), Image.LANCZOS).save(out, 'WEBP', quality=72, method=6)
    return out


AUTO_NOTE = re.compile(r'^(?P<pre>(?:B站 )?@[^·]+· )[\d.,]+ ?[万亿]? 播放(?P<post> · .*)$')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--keys')
    ap.add_argument('--no-rx', action='store_true')
    ap.add_argument('--sleep', type=float, default=2.5)
    ap.add_argument('--probe', nargs='+')
    ap.add_argument('--thumb', nargs=2, metavar=('KEY', 'URL'))
    a = ap.parse_args()

    if a.probe:
        for u in a.probe:
            print(json.dumps({'url': u, **info(u)}, ensure_ascii=False)); time.sleep(a.sleep)
        return
    if a.thumb:
        k, u = a.thumb; r = info(u)
        if r['status'] != 'ok' or not r.get('thumb'): sys.exit(f'no cover: {r}')
        print('saved', save_thumb(k, r['thumb'])); return

    d = json.loads(LIVE.read_text())
    keys = set(a.keys.split(',')) if a.keys else None
    report, changed = [], 0
    for x in d['items']:
        if keys and x['k'] not in keys: continue
        u = video_url(x['m']); r = info(u)
        report.append({'k': x['k'], 'kind': 'video', 'url': u, **{k: v for k, v in r.items() if k != 'thumb'}})
        st = x.get('st') or {}
        tag = r['status'].upper()
        if r['status'] == 'ok' and not st.get('via'):
            new = {f: r[f] for f in ('pl', 'lk', 'sh', 'cm') if r.get(f) is not None}
            diff = {f: (st.get(f), v) for f, v in new.items() if st.get(f) != v}
            if diff: print(f"  {x['k']:12} {diff}"); changed += 1
            st.update(new); st['rd'] = TODAY; x['st'] = st
        elif r['status'] == 'ok':
            print(f"  {x['k']:12} st uses a third-party source ({st.get('via')}); video alive, numbers left as is")
        print(f"{tag:5} {x['k']:12} {u}" + (f"  <- {r.get('err')}" if r['status'] != 'ok' else ''))
        time.sleep(a.sleep)
        if a.no_rx: continue
        for rx in x.get('rx', []):
            if not rx[1] or not re.search(r'tiktok\.com/@.+/video/|bilibili\.com/video/|youtube\.com/|youtu\.be/|instagram\.com/(reel|p)/', rx[1]):
                continue
            rr = info(rx[1])
            report.append({'k': x['k'], 'kind': 'rx', 'url': rx[1], **{k: v for k, v in rr.items() if k != 'thumb'}})
            if rr['status'] == 'ok' and rr.get('pl'):
                m = AUTO_NOTE.match(rx[2] or '')
                if m: rx[2] = f"{m['pre']}{fw(rr['pl'])} 播放{m['post']}"
            if rr['status'] != 'ok': print(f"  rx {rr['status'].upper()}: {rx[1]}  <- {rr.get('err')}")
            time.sleep(a.sleep)

    dead = [r for r in report if r['status'] == 'dead']; err = [r for r in report if r['status'] == 'error']
    print(f'\n{len(report)} checked, {changed} cards with new numbers, {len(dead)} dead, {len(err)} errors')
    if a.dry_run:
        print('dry run: nothing written'); return
    d['updated'] = TODAY
    LIVE.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    (ROOT / 'reports').mkdir(exist_ok=True)
    rp = ROOT / f'reports/refresh-{TODAY}.json'
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print('wrote data/live.json and', rp.relative_to(ROOT))


if __name__ == '__main__':
    main()
