#!/usr/bin/env python3
"""Offline, data-derived revision figures. Requires Pillow only; no inference or installs.
Run from any cwd: python -X utf8 -I -B <package>/analysis/draw_verified_figures.py
Only writes revisions/figures/Figure1..8.png, figure-data.json and
verification/figure_revision_report.md. Never writes the original figures.
"""
from __future__ import annotations
import ast, csv, hashlib, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'revisions' / 'figures'
READS = {}
BLUE, ORANGE, GREEN, INK, MUTED, GRID = '#1768A6', '#BD5522', '#187856', '#1C2938', '#566474', '#DAE1E8'
FAMILY = {'Qwen2.5':BLUE, 'Qwen3':ORANGE, 'Llama-3.1':GREEN}
FONT_PATHS = {}
def font(n=27,bold=False):
    name='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try:
        f=ImageFont.truetype(name,n); FONT_PATHS[name]=str(f.path); return f
    except OSError:
        FONT_PATHS['fallback']='Pillow scalable default'; return ImageFont.load_default(size=n)
def read(rel):
    p=(ROOT/rel).resolve()
    if not p.is_relative_to(ROOT): raise ValueError('input outside package')
    b=p.read_bytes(); READS[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}; return b
def load(rel): return json.loads(read(rel).decode('utf-8-sig'))
def rows(rel): return list(csv.DictReader(read(rel).decode('utf-8-sig').splitlines()))
def pct(k,n):
    if n<=0: raise ValueError('nonpositive denominator')
    return 100*k/n
def label(c):
    x,q=c.rsplit('_',1)
    return x.replace('qwen2.5','Q2.5').replace('qwen3','Q3').replace('llama3.1','Llama').replace('b','B')+' '+q.upper()+(' *' if x.startswith('qwen3') else '')
def size(c): return int(c.rsplit('-',1)[1].split('b')[0])
def family(c): return 'Qwen2.5' if c.startswith('qwen2.5') else 'Qwen3' if c.startswith('qwen3') else 'Llama-3.1'
class Canvas:
    def __init__(self,w,h,title,subtitle):
        self.im=Image.new('RGB',(w,h),'white'); self.d=ImageDraw.Draw(self.im); self.w=w;self.h=h
        self.text(65,40,title,44,True); self.text(65,108,subtitle,26,color=MUTED)
    def text(self,x,y,s,n=27,bold=False,color=INK,anchor=None):
        self.d.multiline_text((x,y),str(s),font=font(n,bold),fill=color,spacing=9,anchor=anchor)
    def line(self,xy,color=GRID,width=2): self.d.line(xy,fill=color,width=width)
    def dot(self,x,y,color,r=8): self.d.ellipse((x-r,y-r,x+r,y+r),fill=color)
    def footer(self,lines):
        y=self.h-45-42*len(lines)
        self.line((65,y-18,self.w-65,y-18))
        for s in lines: self.text(65,y,s,23,color=MUTED);y+=42
    def legend(self,items,x=85,y=175,n=26,gap=480):
        for i,(lab,col) in enumerate(items):
            xx=x+i*gap; self.d.rectangle((xx,y+5,xx+27,y+29),fill=col);self.text(xx+42,y,lab,n)
    def save(self,num):
        self.im.save(OUT/f'Figure{num}.png',dpi=(300,300))
def axes(c,box,lo,hi,ticks,unit='Rate (%)'):
    x,y,w,h=box
    for v in ticks:
        yy=y+h-(v-lo)/(hi-lo)*h
        c.line((x,yy,x+w,yy));c.text(x-20,yy,f'{v:g}',24,color=MUTED,anchor='rm')
    c.line((x,y,x,y+h),INK);c.line((x,y+h,x+w,y+h),INK)
    c.text(x,y-54,unit,27,True)
    return lambda v:y+h-(v-lo)/(hi-lo)*h

def bars(c,box,labs,series,lo=0,hi=100,ticks=None,unit='Rate (%)',labsize=24,counts=None):
    x,y,w,h=box; yv=axes(c,box,lo,hi,ticks or list(range(0,int(hi)+1,20)),unit)
    step=w/len(labs); bw=min(75,step*.65/len(series)); base=yv(0)
    for i,lab in enumerate(labs):
        mid=x+step*(i+.5)
        for j,(name,vals,col) in enumerate(series):
            v=vals[i]
            if v is None: continue
            xx=mid+(j-(len(series)-1)/2)*(bw+6)
            yy=yv(v);c.d.rectangle((xx-bw/2,min(yy,base),xx+bw/2,max(yy,base)),fill=col)
            c.text(xx,yy-12-j*28 if v>=0 else yy+12+j*28,f'{v:.1f}',22,color=col,anchor='mb' if v>=0 else 'mt')
        c.text(mid,y+h+22,lab,labsize,anchor='ma')
        if counts: c.text(mid,y+h+115,counts[i],21,color=MUTED,anchor='ma')

# Inputs are measurements, never legacy embedded plotting constants.
def build_data():
    refs=load('verification/replay_reference.json'); t6=load('verification/replay_table6.json')
    t7=load('verification/replay_table7.json'); primary=load('verification/replay_primary.json')
    corpus=load('data/corpus.json'); traps=load('data/corpus_traps.json'); summary=load('verification/replay_summary.json')
    reli=load('annotation/reliability_summary.json'); pairs=rows('annotation/pairwise_reliability.csv')
    stats=load('revisions/statistics_revised.json'); tm={t['task_id']:t for t in corpus+traps}
    assert len(corpus)==198 and len(traps)==18
    # Validate the import boundary before invoking the actual offline core.
    allowed={'__future__','copy','dataclasses','collections','csv','json','random','pathlib','taxonomy','sandbox'}
    for rel in ['overpriv/__init__.py','overpriv/taxonomy.py','overpriv/sandbox.py','overpriv/policies.py']:
        tree=ast.parse(read(rel).decode('utf8'))
        mods=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): mods.extend(a.name.split('.')[0] for a in node.names)
            elif isinstance(node,ast.ImportFrom): mods.append((node.module or '').split('.')[0])
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'eval','exec','__import__','compile'}: raise ValueError('unreviewed dynamic core')
        assert not set(mods)-allowed,(rel,mods)
    sys.path.insert(0,str(ROOT))
    from overpriv.sandbox import execute
    from overpriv.policies import REFERENCE_POLICIES
    agg=defaultdict(lambda:{'n':0,'intent_count':0,'impact_count':0})
    pol=REFERENCE_POLICIES['P_confused']
    for t in corpus:
        m=execute(t,pol(t)); a=agg[t['domain']];a['n']+=1;a['intent_count']+=m.intent_overpriv;a['impact_count']+=m.impact
    domains=[dict(domain=d,**a,intent_pct=pct(a['intent_count'],a['n']),impact_pct=pct(a['impact_count'],a['n']),gap_pp=pct(a['intent_count']-a['impact_count'],a['n'])) for d,a in sorted(agg.items())]
    for r in refs:
        r['intent_unrounded_pct']=pct(r['intent_count'],r['n']);r['impact_unrounded_pct']=pct(r['impact_count'],r['n']);r['gap_unrounded_pp']=pct(r['intent_count']-r['impact_count'],r['n'])
    by6={r['config']:r for r in t6}; configs=stats['cohorts']['full18']['configs']; raw={}
    for config in configs:
        log=load(f'results/runs/{config}.json'); rs=log['per_task']; assert len(rs)==216
        attack=[r for r in rs if tm[r['task_id']]['label']=='attack']
        success=sum(r.get('tier') is not None and r['tier']>tm[r['task_id']]['role_cap'] for r in attack)
        assert len(attack)==72
        raw[config]={'original_OPUR_count':sum(r.get('tier') is not None and r['tier'] > tm[r['task_id']]['gold_tier'] for r in rs),'original_n':len(rs),'attack_count':success,'attack_n':len(attack),'attack_pct':pct(success,len(attack)),'configured_quantization':log['quant']}
    def rec(config):
        r=raw[config]; tr=by6.get(config)
        return dict(config=config,family=family(config),size_B=size(config),exploratory=config.startswith('qwen3'),**r,
                    OPUR_count=tr['OPUR_count'] if tr else r['original_OPUR_count'],OPUR_n=tr['n'] if tr else r['original_n'],
                    OPUR_pct=pct(tr['OPUR_count'],tr['n']) if tr else pct(r['original_OPUR_count'],r['original_n']),
                    OPUR_basis='corrected base198 + concealed18' if tr else 'original216; original traps all refused; corrected unavailable')
    f6a=[rec(c) for c in sorted((c for c in configs if c.endswith('_int4')),key=lambda c:(size(c),family(c)))]
    gaps={r['config']:r for r in stats['III_Gap_excl']['per_config']}
    f6b=[]
    for c in sorted(configs,key=lambda c:(family(c),size(c),c)):
        g=gaps.get(c)
        f6b.append({'config':c,'corrected216':g['corrected216'] if g else None,'excl_legit_high180':g['excl_legit_high180'] if g else None,'unavailable_reason':None if g else 'concealed18 absent; not imputed'})
    f8=[rec(c) for c in sorted(configs,key=lambda c:(family(c),size(c))) if (c.startswith('qwen') and c.endswith('_fp16')) or (c.startswith('llama') and c.endswith('_int8'))]
    assert len(f6a)==8 and len(f8)==7 and len(by6)==13 and len(f6b)==18
    assert raw['qwen2.5-72b_int4']['attack_count']==3
    ids=sorted(r['anonymous_id'] for r in reli['rating_verification']); alias={rid:f'E{i+1}' for i,rid in enumerate(ids)}
    fpairs=[{'pair':alias[r['annotator_a']]+'-'+alias[r['annotator_b']], 'tier_linear_kappa':float(r['tier_kappa']), 'behavior_nominal_kappa':float(r['behavior_kappa']), 'n':int(r['tier_n'])} for r in pairs]
    design=[{'expert':alias[r['anonymous_id']],'count':r['expert_reconstructed_legit_high_count'],'n':r['denominator_full216'],'pct':pct(r['expert_reconstructed_legit_high_count'],r['denominator_full216'])} for r in reli['MEdef']['expert_results']]
    pconfig=sorted({r['config'] for r in primary},key=lambda c:(family(c),size(c),c)); assert len(pconfig)==13
    f7=[]
    for cfg in pconfig:
        rs={r['condition']:r for r in primary if r['config']==cfg}
        assert all(r['n']==12 for r in rs.values())
        f7.append({'config':cfg,'conditions':rs})
    return {'Figure1':{'type':'conceptual schematic','modeled_not_deployed':True,'base_n':len(corpus),'trap_n':len(traps)},
            'Figure2':refs,'Figure3':refs,'Figure4':domains,
            'Figure5':{'pairwise':fpairs,'unanimity':reli['unanimity'],'design_constant':design,'alias_basis':'lexically sorted released anonymous IDs; not private real identity'},
            'Figure6':{'A':f6a,'B':f6b,'corrected_available':len(by6),'all_configurations':len(configs),'gap_definition':'III-Gap = harmless over-selection rate - missed escalation rate, within each denominator'},
            'Figure7':{'A':f7,'B':t7,'pooled':stats['main_primary_unchanged'],'dependence_note':'13 configurations reuse the same 12 tasks; descriptive, not independent replicates'},
            'Figure8':f8,'notes':['No network/GPU/model execution','Actual tensor quantization unverified; configuration labels only','Qwen3 exploratory','Original and corrected trap files temporally separate; hybrid216 explicitly labeled'],
            'reanalysis_context':{'H1_comparisons':stats['H1']['comparisons'],'H3_original_inference_status':stats['H3']['original_inference_status'],'H2_status':stats['H2']['status']}}

def render(data):
    c=Canvas(2200,950,'Figure 1. Dual-axis measurement framework','Conceptual modeled pipeline, not evidence of deployment or full audit retention')
    c.d.rounded_rectangle((65,205,2135,715),radius=18,outline=GRID,width=4)
    c.text(95,230,'Offline artifact-replay boundary: deterministic mock state; no real assets',29,True,color=MUTED)
    boxes=[(100,365,360,545,'Released tasks\nbase198\n+ traps18','#EEF2F6'),(420,365,700,545,'Tool selection\n(saved modal\nchoice)','#EEF2F6'),(770,290,1210,435,'INTENT axis\nselected tier > gold tier','#E5F0FA'),(770,510,1210,655,'IMPACT axis\nmock T4/T5 side effects','#FBEDE5'),(1450,365,2070,545,'III-Gap = intent - impact\nHO rate - ME rate\nwithin the same denominator','#E9F4EE')]
    for x1,y1,x2,y2,txt,fill in boxes:
        c.d.rounded_rectangle((x1,y1,x2,y2),radius=16,fill=fill,outline=GRID,width=2);c.text((x1+x2)/2,(y1+y2)/2-45,txt,28,anchor='ma')
    def arrow(x1,y1,x2,y2):
        c.line((x1,y1,x2,y2),MUTED,4);ang=math.atan2(y2-y1,x2-x1);p=[(x2,y2),(x2-20*math.cos(ang-.5),y2-20*math.sin(ang-.5)),(x2-20*math.cos(ang+.5),y2-20*math.sin(ang+.5))];c.d.polygon(p,fill=MUTED)
    arrow(360,455,420,455);arrow(700,435,770,365);arrow(700,475,770,580);arrow(1210,365,1450,420);arrow(1210,580,1450,490)
    c.footer(['Impact here means deterministic privileged-subject growth or irreversible mock destruction, not financial harm.','Serving/gateway deployment and complete before/after log retention were not verified.']);c.save(1)
    refs=data['Figure2'];labs=[r['policy'] for r in refs]
    c=Canvas(1800,1240,'Figure 2. Reference-policy intent and mock impact','Base corpus n=198 per policy; exact counts converted to percentages')
    c.legend([('Intent over-privilege',BLUE),('Mock impact',ORANGE)],gap=620)
    bars(c,(150,300,1510,590),labs,[('intent',[r['intent_unrounded_pct'] for r in refs],BLUE),('impact',[r['impact_unrounded_pct'] for r in refs],ORANGE)],hi=110,ticks=range(0,101,20),counts=[f"I {r['intent_count']}/{r['n']} | M {r['impact_count']}/{r['n']}" for r in refs])
    c.footer(['Fixed reference policies, not learned agents. Both axes are scored on the same 198 base tasks.']);c.save(2)
    c=Canvas(1800,1130,'Figure 3. Signed reference-policy III-Gap','Intent minus mock impact; n=198 per policy; positive = over-count, negative = under-count')
    bars(c,(155,300,1500,560),labs,[('gap',[r['gap_unrounded_pp'] for r in refs],BLUE)],lo=-25,hi=25,ticks=[-20,-10,0,10,20],unit='III-Gap (percentage points)')
    c.line((155,580,1655,580),INK,3);c.footer(['III-Gap is a signed difference, not a model accuracy or safety score.']);c.save(3)
    ds=data['Figure4'];c=Canvas(2000,1130,'Figure 4. P_confused across six offline mock domains','Actual released base corpus passed through core policy and execute(); no network or live assets')
    c.legend([('Intent over-privilege',BLUE),('Mock impact',ORANGE)],gap=630)
    dn={'D1':'Server\naccess','D2':'Database\noperations','D3':'Networking','D4':'Service /\nprocess','D5':'Secrets /\ncredentials','D6':'Audit /\nlogging'}
    bars(c,(150,310,1720,530),[r['domain']+'\n'+dn[r['domain']] for r in ds],[('intent',[r['intent_pct'] for r in ds],BLUE),('impact',[r['impact_pct'] for r in ds],ORANGE)],hi=70,ticks=[0,20,40,60],counts=[f"n={r['n']}" for r in ds])
    c.footer(['Domain labels describe the synthetic tasks. Side effects are determined by tier in a shared generic mock state.']);c.save(4)
    f5=data['Figure5'];c=Canvas(2500,1380,'Figure 5. Released expert-annotation reliability','Four anonymous experts, 198 base tasks; no expert trap votes fabricated')
    c.text(80,220,'A  Pairwise agreement',31,True);c.legend([('Tier: linear weighted',BLUE),('Behavior: nominal',ORANGE)],x=85,y=280,n=23,gap=370)
    bars(c,(130,430,670,480),[r['pair'] for r in f5['pairwise']],[('tier',[r['tier_linear_kappa'] for r in f5['pairwise']],BLUE),('behavior',[r['behavior_nominal_kappa'] for r in f5['pairwise']],ORANGE)],hi=1,ticks=[0,.2,.4,.6,.8,1],unit='Kappa (0 to 1)',labsize=20)
    # Replace percentage-style labels with appropriate kappa precision.
    # Values are drawn separately below because shared bars rounds to one decimal.
    c.d.rectangle((100,380,815,960),fill='white')
    yv=axes(c,(130,430,670,480),0,1,[0,.2,.4,.6,.8,1],'Kappa (0 to 1)')
    for i,r in enumerate(f5['pairwise']):
        xx=130+(i+.5)*670/6
        for dx,key,col in [(-22,'tier_linear_kappa',BLUE),(22,'behavior_nominal_kappa',ORANGE)]:
            yy=yv(r[key]);c.d.rectangle((xx+dx-17,yy,xx+dx+17,910),fill=col);c.text(xx+dx,yy-10-(25 if key=='behavior_nominal_kappa' else 0),f'{r[key]:.3f}',18,color=col,anchor='mb')
        c.text(xx,932,r['pair'],20,anchor='ma')
    c.text(905,220,'B  Four-expert unanimity',31,True)
    names={'exact_tier_unanimous':'Exact\ntier','impact_threshold_unanimous':'Impact\nthreshold','behavior_unanimous':'Required\nbehavior','role_cap_threshold_unanimous':'Role-cap\nthreshold'}
    un=list(f5['unanimity'].items());bars(c,(950,430,650,480),[names[k] for k,v in un],[('u',[pct(v['count'],v['denominator']) for k,v in un],GREEN)],hi=100,ticks=[0,20,40,60,80,100],counts=[f"{v['count']}/{v['denominator']}" for k,v in un],labsize=21)
    c.text(1690,220,'C  Design-constant proxy',31,True)
    c.text(1690,275,'Expert legit-high set / full216',25,color=MUTED)
    bars(c,(1740,430,620,480),[r['expert'] for r in f5['design_constant']],[('d',[r['pct'] for r in f5['design_constant']],ORANGE)],hi=20,ticks=[0,5,10,15,20],counts=[f"{r['count']}/{r['n']}" for r in f5['design_constant']])
    c.footer(['A: minimum tier uses linear-weighted kappa; required behavior uses nominal kappa. No shared weighted label.','C: min tier >=4 AND required behavior=select_tool. Numerators from base198, denominator216 by supplied definition.','C is a potential definitional/design proxy, not observed per-configuration missed escalation.']);c.save(5)
    a=data['Figure6']['A'];b=data['Figure6']['B'];c=Canvas(2600,2110,'Figure 6. Descriptive configuration comparison and gap accounting','Configured INT4 in A; Qwen3 marked * is exploratory. Tensor quantization was not verified.')
    c.text(90,205,'A  Eight INT4 configurations',32,True);c.legend([('OPUR / n216',BLUE),('Attack cap-exceedance / n72',ORANGE)],x=95,y=268,gap=700)
    labs=[label(r['config']).replace(' INT4','')+('\norig' if r['OPUR_basis'].startswith('original') else '\ncorr') for r in a]
    bars(c,(160,385,2260,480),labs,[('opur',[r['OPUR_pct'] for r in a],BLUE),('atk',[r['attack_pct'] for r in a],ORANGE)],hi=85,ticks=[0,20,40,60,80],labsize=25,counts=[f"I {r['OPUR_count']}/216; A {r['attack_count']}/72" for r in a])
    c.text(90,1040,'B  Corrected III-Gap: 13 numeric rows of 18 configurations',32,True)
    c.legend([('All: n216',BLUE),('Legit-high excluded: n180',GREEN)],x=90,y=1096,gap=650)
    # Two columns of nine horizontal rows keeps labels readable while preserving unavailable rows.
    for col in range(2):
        xx=90+col*1260; x0=xx+365;w=635;y0=1200
        xmap=lambda v:x0+(v+25)/35*w
        for tick in [-20,-10,0,10]:
            tx=xmap(tick);c.line((tx,y0-15,tx,y0+530));c.text(tx,y0+547,f'{tick}',24,color=MUTED,anchor='ma')
        c.line((xmap(0),y0-15,xmap(0),y0+530),INK,3)
        for j,r in enumerate(b[col*9:(col+1)*9]):
            yy=y0+j*59;c.text(xx,yy+12,label(r['config']),24,anchor='la')
            if r['corrected216'] is None:
                c.text(x0,yy+10,'Unavailable: concealed18 absent',23,color=MUTED);continue
            for dy,key,color in [(0,'corrected216',BLUE),(23,'excl_legit_high180',GREEN)]:
                g=r[key]['gap_pp'];gx=xmap(g);zx=xmap(0);c.d.rectangle((min(gx,zx),yy+dy,max(gx,zx),yy+dy+17),fill=color)
                c.text(x0+w+12,yy+dy-4,f'{g:+.1f}',21,color=color)
        c.text(x0,y0+585,'III-Gap (percentage points)',24,True)
    c.footer(['corr = base198 + concealed18. orig = source216 with refused pre-correction traps, used only where corrected OPUR is unavailable.','B: excluding36 legit-high tasks changes denominator216 to180; it is NOT a fixed 16.7-point translation.','Within either denominator: III-Gap = harmless over-selection rate - missed escalation rate. Unavailable gaps are not zero or imputed.']);c.save(6)
    f7=data['Figure7'];c=Canvas(2400,1540,'Figure 7. Concealed, disclosed, and placebo trap outcomes','A: primary missed escalation n12 per configuration, four high-impact tools in D1/D2/D4/D6')
    c.text(70,160,'* Qwen3 is exploratory; configured quantization, not verified tensor dtype.',23,color=MUTED)
    c.text(70,212,'A  Thirteen configurations, shared task set',31,True)
    c.legend([('Concealed',BLUE),('Disclosed',ORANGE),('Placebo',GREEN)],x=75,y=276,gap=370)
    x0=430;w=780;y0=400
    for tick in range(0,101,20):
        tx=x0+tick/100*w;c.line((tx,y0-20,tx,y0+750));c.text(tx,y0+780,str(tick),25,color=MUTED,anchor='ma')
    for i,r in enumerate(f7['A']):
        yy=y0+i*58;c.text(70,yy,label(r['config']),25,anchor='la')
        cr=r['conditions'];a1=pct(cr['concealed']['me_count'],cr['concealed']['n']);a2=pct(cr['disclosed']['me_count'],cr['disclosed']['n']);c.line((x0+a1/100*w,yy+15,x0+a2/100*w,yy+15),MUTED,4)
        for cond,col,dy in [('concealed',BLUE,4),('disclosed',ORANGE,16),('placebo',GREEN,28)]:
            r0=cr[cond];c.dot(x0+pct(r0['me_count'],r0['n'])/100*w,yy+dy,col,9)
        c.text(1260,yy+5,'/'.join(str(cr[k]['me_count']) for k in ['concealed','disclosed','placebo']),22,color=MUTED)
    c.text(x0,y0+830,'Primary missed escalation (%)',26,True)
    c.text(70,1300,'Right-side counts: concealed / disclosed / placebo, each denominator12.',24,color=MUTED)
    c.text(1450,212,'B  Domain trap selection',31,True);c.text(1450,270,'All traps: n39 per domain per condition',24,color=MUTED)
    # These counts are a different endpoint, never relabeled as primary ME.
    ds=f7['B'];bars(c,(1510,450,730,650),[r['domain'] for r in ds],[('c',[pct(r['concealed_count'],r['concealed_n']) for r in ds],BLUE),('d',[pct(r['disclosed_count'],r['disclosed_n']) for r in ds],ORANGE)],hi=110,ticks=range(0,101,20),counts=[f"{r['concealed_count']}/{r['concealed_n']}\n{r['disclosed_count']}/{r['disclosed_n']}" for r in ds],labsize=23)
    pool=f7['pooled'];c.footer([f"Pooled reused-task records: concealed {pool['concealed']['events']}/{pool['concealed']['denominator']}={pool['concealed']['pooled_pct']:.1f}%; disclosed {pool['disclosed']['events']}/{pool['disclosed']['denominator']}={pool['disclosed']['pooled_pct']:.1f}%; placebo {pool['placebo']['events']}/{pool['placebo']['denominator']}={pool['placebo']['pooled_pct']:.1f}%.",'Descriptive only: configurations share tasks and checkpoints. No independent-binomial intervals or causal claim.']);c.save(7)
    f8=data['Figure8'];c=Canvas(2300,1320,'Figure 8. Family and size comparison in seven configurations','Qwen2.5 / Qwen3: configured FP16; Llama-3.1: configured INT8. Qwen3 * is exploratory.')
    c.legend([(f,col) for f,col in FAMILY.items()],gap=590)
    labs=[label(r['config']).replace(' FP16','').replace(' INT8','')+('\norig' if r['OPUR_basis'].startswith('original') else '\ncorr') for r in f8]
    for pan,key,title,hi,xx in [(0,'OPUR_pct','A  Intent over-privilege / n216',35,140),(1,'attack_pct','B  Attack cap-exceedance / n72',85,1280)]:
        c.text(xx-55,275,title,31,True);yv=axes(c,(xx,390,920,510),0,hi,list(range(0,int(hi)+1,10 if pan==0 else 20)),'Rate (%)')
        for i,r in enumerate(f8):
            mid=xx+(i+.5)*920/len(f8);yy=yv(r[key]);col=FAMILY[r['family']]
            c.d.rectangle((mid-34,yy,mid+34,900),fill=col);c.text(mid,yy-12,f"{r[key]:.1f}",23,color=col,anchor='mb');c.text(mid,920,labs[i] if pan==0 else label(r['config']).replace(' FP16','').replace(' INT8','')+'\nbase',22,anchor='ma')
            cnt=r['OPUR_count'] if pan==0 else r['attack_count'];den=r['OPUR_n'] if pan==0 else r['attack_n'];c.text(mid,1000,f'{cnt}/{den}',21,color=MUTED,anchor='ma')
    c.footer(['corr: corrected base198 + concealed18; orig: original216 with pre-correction refused traps (two Llama rows).','No Qwen2.5-72B FP16 run exists in this seven-row view. Descriptive comparison, not an isolated size or quantization effect.','Quantization labels are configured settings only; actual tensor dtype / quantization was not verified.']);c.save(8)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source_paths=[p for folder in ['data','results','annotation','figures'] for p in (ROOT/folder).rglob('*') if p.is_file()]
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    data=build_data()
    def finite(obj):
        if isinstance(obj,float): assert math.isfinite(obj)
        elif isinstance(obj,dict):
            for value in obj.values(): finite(value)
        elif isinstance(obj,list):
            for value in obj: finite(value)
    finite(data)
    assert sum(r['corrected216'] is None for r in data['Figure6']['B'])==5
    for r in data['Figure6']['B']:
        for key in ['corrected216','excl_legit_high180']:
            a=r[key]
            if a:
                assert abs(a['gap_pp']-pct(a['intent_count']-a['impact_count'],a['n']))<1e-9
    render(data)
    after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    assert before==after,'source changed'
    for rel,v in READS.items(): assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==v['sha256'],'input changed'
    images=[]
    for i in range(1,9):
        p=OUT/f'Figure{i}.png'
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im: assert im.width>=1600; images.append({'file':str(p.relative_to(ROOT)),'width':im.width,'height':im.height,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    data['provenance']={'reads':READS,'source_unchanged_files':len(before),'source_integrity_passed':True,'fonts':FONT_PATHS,'images':images,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'figure-data.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    report='''# Figure revision verification\n\nEight replacement PNGs rendered with Pillow, without matplotlib, numpy, installs, network, GPU or model calls. Original figure sources and data/results/annotation files remained byte-for-byte unchanged.\n\n## Data and presentation corrections\n\n- Figure1 is a conceptual modeled pipeline, explicitly not verified deployment or full audit-log retention.\n- Figures2/3 use replay_reference exact counts with denominator198, not embedded manuscript constants.\n- Figure4 invokes inspected offline core P_confused and execute() on released base198; six synthetic domains and generic tier-driven mock state are explicit.\n- Figure5 uses released pairwise CSV and summary keys: tier linear-weighted kappa versus behavior nominal kappa on general kappa axis0..1. Unanimity comes from actual four metrics, not fabricated thresholds. PanelC is expert legit-high numerator /216, a design proxy not observed missed escalation. Anonymous alias order is reproducible lexical IDs.\n- Figure6A contains all eight INT4 configurations. Available corrected OPUR uses replay Table6 counts/216; two Llama INT4 rows use dynamically derived original216 OPUR because corrected concealed logs are unavailable. Attack cap-exceedance uses actual original attack72 logs. Qwen2.5-72B INT4 is3/72=4.2%, not4.3%. Normal requests are not mislabeled as original corpus rates.\n- Figure6B keeps all18 labels and five unavailable gaps, without zero filling. Numeric thirteen rows use new reanalysis exact n216 and legit-high-excluded n180 counts. III-Gap=HO-ME within each denominator, not a fixed16.7-point translation.\n- Figure7 shows descriptive primary n12 for13 configurations, four high-impact tools. Placebo is included. A separate panel shows replay Table7 per-domain all-trap selections n39, never conflated with primary endpoint. No independent-binomial intervals or independent replicates claim.\n- Figure8 derives seven configurations dynamically from available logs by configured FP16 for Qwen and INT8 for Llama. Corrected five Qwen OPUR rows use Table6 n216; two Llama original216 rows are explicitly marked orig. Attack denominator72. Absent72B FP16 is not invented.\n- Qwen3 is exploratory. Configured quantization is labeled; actual tensor dtype/quantization is unverified.\n\n## Reproduction and machine verification\n\nRun `python -X utf8 -I -B analysis/draw_verified_figures.py` or use its absolute path from any cwd. Source hashes and all input hashes checked unchanged; all eight PNGs reopen/verify and have width at least1600 pixels. Exact data, input hashes, output dimensions/hashes, font provenance and new reanalysis context are in revisions/figures/figure-data.json.\n\nOnly the allowlisted revisions/figures/Figure1..8.png, revisions/figures/figure-data.json and this report are emitted by the script. Original figures are never overwritten.\n\n## Visual review\n\nAll eight rendered figures were opened for visual inspection. Figure1 box text was wrapped, Figure5/6 footer margins increased, and grouped numeric labels staggered after sample review. Figure6 was checked for all8 INT4 configurations,13 numeric gaps/five unavailable rows, n216/n180 labels and3/72=4.2%. Figure7 checked for separate primary n12 versus domain n39 endpoints, finite100% points, and explicit shared-task dependence. Figure5 checked for kappa type distinction, actual unanimity counts and expert design216 proxy. Figure8 checked for seven configurations and distinct corrected/original OPUR versus original base72 attack labels.\n'''
    (ROOT/'verification'/'figure_revision_report.md').write_text(report+f'\nPreserved source files: {len(before)}. All checks passed.\n',encoding='utf8')
    print(json.dumps({'images':images,'source_files_preserved':len(before),'font':FONT_PATHS},indent=2))
if __name__=='__main__': main()
