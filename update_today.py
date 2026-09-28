#!/usr/bin/env python3
import datetime as dt, json, os, re, ssl, urllib.request

TODAY = dt.date.today()
BIRTH = dt.date(2026, 1, 9)
BASE = '/home/claw/.openclaw/workspace-niangao-edu/niangao-output'
SRC = os.path.join(BASE, 'gen_page.py')
if os.path.exists('/home/claw/.openclaw/workspace-niangao-edu/niangao-config.env'):
    for line in open('/home/claw/.openclaw/workspace-niangao-edu/niangao-config.env', encoding='utf-8'):
        if '=' in line and not line.lstrip().startswith('#'):
            k, v = line.strip().split('=', 1); os.environ.setdefault(k, v)
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

# Refresh all weight records from the separate 年糕Weight database.
weight_rows=[]; cursor=None
for _ in range(10):
    body={'page_size':100,'sorts':[{'property':'日期','direction':'ascending'}]}
    if cursor: body['start_cursor']=cursor
    res=api('databases/31854ae6-6704-80fb-9ba5-d32f012e7d72/query', body)
    for row in res.get('results',[]):
        p=row.get('properties',{}); date_prop=p.get('日期',{}).get('date') or {}; w=p.get('体重',{}).get('number')
        if date_prop.get('start') and w is not None: weight_rows.append((date_prop['start'][:10],w))
    if not res.get('has_more'): break
    cursor=res.get('next_cursor')

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
weights_literal=repr([(f'{dt.date.fromisoformat(d).month}/{dt.date.fromisoformat(d).day}',w) for d,w in sorted(weight_rows)])
src=re.sub(r'(?ms)^weight_records\s*=\s*\[.*?^\]\n', 'weight_records = '+weights_literal+'\n', src, count=1)
timeline={}; prev={}
for d in [TODAY-dt.timedelta(days=i) for i in range(4,-1,-1)]:
    arr=by.get(str(d),[])
    timeline[f'{d.month}/{d.day}']={'times':[x['time'] for x in arr], 'gaps':[x['gap'].replace(' ','').replace('小时','h').replace('分钟','m') for x in arr]}
    before=by.get(str(d-dt.timedelta(days=1)),[])
    prev[f'{d.month}/{d.day}']=before[-1]['time'] if before else '--:--'
src=re.sub(r'(?ms)^timeline_data\s*=\s*\{.*?^prev_last\s*=\s*.*?\n', 'timeline_data = '+repr(timeline)+'\nprev_last = '+repr(prev)+'\n', src, count=1)
weather_text = '天气数据暂不可用'
weather_humidity = '--'
try:
    import subprocess
    raw = subprocess.check_output(['curl','-s','--retry','3','--retry-delay','2','--retry-all-errors','https://wttr.in/Shanghai?format=%C+%t+%h+%w&lang=zh'], text=True, timeout=20).strip()
    if raw:
        import re
        temp = re.search(r'[+-]?\d+°[CF]', raw)
        hum = re.search(r'\d+%', raw)
        wind = re.search(r'(?:[←→↖↗↙↘↑↓]\s*)?\d+\s*(?:km/h|mph)', raw)
        condition = raw[:temp.start()].strip() if temp else raw
        # wttr.in may return Fahrenheit in this environment; normalize for the page.
        if temp and temp.group(0).endswith('°F'):
            f = int(re.search(r'[+-]?\d+', temp.group(0)).group(0))
            raw_c = round((f - 32) * 5 / 9)
            weather_text = (condition + ' ' if condition else '') + f'{raw_c}°C'
        else:
            weather_text = (condition + ' ' if condition else '') + (temp.group(0) if temp else '')
        if wind: weather_text += ' · 风 ' + wind.group(0)
        weather_humidity = hum.group(0) if hum else '--'
except Exception:
    pass
src=replace_var(src,'weather_text',weather_text)
src=replace_var(src,'weather_humidity',weather_humidity)
src=replace_var(src,'clothing','短袖薄款衣物，按体感增减')
src=replace_var(src,'clothing_extra','室内外温差大时备薄外套，避免捂汗')
src=src.replace('7月龄探索期','8月龄探索期').replace('7个月宝宝','8个月宝宝').replace('· 7月龄','· 8月龄')
# Refresh every human-facing date in the template, including dates from a prior run.
weekday_cn = '一二三四五六日'[TODAY.weekday()]
src = re.sub(r'2026-\d{2}-\d{2}', str(TODAY), src)
src = re.sub(r'\d{1,2}月\d{1,2}日 周[一二三四五六日]', f'{TODAY.month}月{TODAY.day}日 周{weekday_cn}', src)
exec(compile(src,'gen_page.py','exec'),{})
print('updated', TODAY, 'days', days, 'months', int(days/30.44), 'feeds', len(feeds))
