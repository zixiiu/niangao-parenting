#!/usr/bin/env python3
import datetime as dt, json, os, re, ssl, urllib.request

TODAY = dt.date(2026, 9, 7)
BIRTH = dt.date(2026, 1, 9)
BASE = '/home/claw/.openclaw/workspace-niangao-edu/niangao-output'
SRC = os.path.join(BASE, 'gen_page.py')
key = os.environ['NOTION_API_KEY']
headers = {'Authorization': 'Bearer '+key, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
ctx = ssl.create_default_context()

def api(path, body):
    req = urllib.request.Request('https://api.notion.com/v1/'+path, data=json.dumps(body).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req, context=ctx, timeout=40) as r: return json.load(r)

def rich(props, name):
    return ''.join(x.get('plain_text','') for x in props.get(name,{}).get('rich_text',[]))

feeds=[]; cursor=None
for _ in range(10):
    body={'filter':{'property':'喂养时间','date':{'on_or_after':str(TODAY-dt.timedelta(days=11))}},'page_size':100,'sorts':[{'property':'喂养时间','direction':'descending'}]}
    if cursor: body['start_cursor']=cursor
    res=api('databases/30c54ae6-6704-8090-9432-d17e4665c395/query', body)
    for row in res.get('results',[]):
        p=row['properties']; s=p['喂养时间']['date']['start']
        feeds.append({'date':s[:10],'time':s[11:16],'ml':p['量(ml)']['number'] or 0,'gap':rich(p,'喂养间隔')})
    if not res.get('has_more'): break
    cursor=res.get('next_cursor')
feeds.sort(key=lambda x:(x['date'],x['time']))
by={}
for x in feeds: by.setdefault(x['date'],[]).append(x)

def replace_var(src, name, value):
    return re.sub(r'(?m)^'+re.escape(name)+r'\s*=\s*.*$', name+' = '+repr(value), src, count=1)

src=open(SRC,encoding='utf-8').read()
days=(TODAY-BIRTH).days
src=replace_var(src,'days_old',days)
src=replace_var(src,'months_old',int(days/30.44))
src=replace_var(src,'month_days',days%30)
y=by.get(str(TODAY-dt.timedelta(days=1)),[])
src=replace_var(src,'yesterday_milk',sum(x['ml'] for x in y))
src=replace_var(src,'yesterday_feeds',len(y))
gaps=[]
for a,b in zip(y,y[1:]):
    gaps.append((dt.datetime.fromisoformat(b['date']+'T'+b['time'])-dt.datetime.fromisoformat(a['date']+'T'+a['time'])).seconds//60)
avg=round(sum(gaps)/len(gaps)) if gaps else 0
src=replace_var(src,'yesterday_avg_gap',f'~{avg//60}h{avg%60:02d}m')
src=replace_var(src,'yesterday_per_feed',round(sum(x['ml'] for x in y)/len(y)) if y else 0)
dates=[TODAY-dt.timedelta(days=i) for i in range(9,-1,-1)]
src=replace_var(src,'milk_dates',[f'{d.month}/{d.day}' for d in dates])
src=replace_var(src,'milk_data',[sum(x['ml'] for x in by.get(str(d),[])) for d in dates])
timeline={}; prev={}
for d in [TODAY-dt.timedelta(days=i) for i in range(4,-1,-1)]:
    arr=by.get(str(d),[])
    timeline[f'{d.month}/{d.day}']={'times':[x['time'] for x in arr], 'gaps':[x['gap'].replace(' ','').replace('小时','h').replace('分钟','m') for x in arr]}
    before=by.get(str(d-dt.timedelta(days=1)),[])
    prev[f'{d.month}/{d.day}']=before[-1]['time'] if before else '--:--'
src=re.sub(r'(?ms)^timeline_data\s*=\s*\{.*?^prev_last\s*=\s*.*?\n', 'timeline_data = '+repr(timeline)+'\nprev_last = '+repr(prev)+'\n', src, count=1)
src=replace_var(src,'weather_text','附近有阵雨 23°C')
src=replace_var(src,'weather_humidity','82%')
src=replace_var(src,'clothing','短袖薄款衣物')
src=replace_var(src,'clothing_extra','有雨备薄外套，室内注意防凉')
src=src.replace('2026-09-06','2026-09-07').replace('9月6日 周日','9月7日 周一')
src=src.replace('</body>', '<div style="position:fixed;top:1.2vh;right:1.2vw;padding:.6vh 1vw;border:1px solid rgba(125,211,252,.35);border-radius:999px;background:rgba(8,47,73,.55);color:#bae6fd;font-size:1.4vh;z-index:5;animation:pulse 3s ease-in-out infinite">🌫️ 白露 · 秋意初现</div></body>')
exec(compile(src,'gen_page.py','exec'),{})
print('updated', TODAY, 'days', days, 'months', int(days/30.44), 'feeds', len(feeds))
