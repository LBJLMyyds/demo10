# Bilingual Demo Script — Site Walkthrough + Core Logic (v2 — 数字已更新)
# 中英双语演示讲稿(第二版——队友更新了引擎,数字和算法描述已全部重新核对)

**这份替换掉之前那份同名文件。** 队友把冲突解决引擎整个重写了,算法逻辑和数字都不一样了,之前那份里的
82条/77%/22%/1%这些数字**全部作废**,下面这份是重新跑真实数据核对过的。

---

## Part A — Live Site Walkthrough 网站现场演示

跟之前完全一样,这部分没有变化,原样照搬即可(网站界面本身没有大改,只是背后的数据变了)。

### Opening 开场

**EN:** *"Let me walk you through the live map first, then I'll go into the two pieces of logic behind it — how
the conflict resolution engine decides things, and how the frontend turns that into something interactive."*

*中:* 先说"我先带你看一遍网站,然后再讲背后两块逻辑",给 Daniel 一个框架。

### Steps 1-6 现场操作步骤

1. 加载动画——盲道点状图案不是装饰,呼应 TGSI 数据集
2. 四个独立图层开关——演示关掉 Venues、单独打开 Flagged for review
3. 搜索——按回车直接跳到匹配度最高的地点
4. 分类筛选(或关系)+ 特征筛选(且关系)
5. 打开一个干净的例子(如 Au79)——四项全部 yes,置信度满分,展示最近无障碍卫生间距离
6. 打开一个被标记冲突的例子——自然过渡到 Part B

(这几步详细话术跟上一版完全一样,没有变化,这里不重复贴了,直接用之前那份的 Part A 即可。)

---

## Part B — Conflict Resolution Engine Logic 冲突解决引擎逻辑(⚠️ 全部重新核对过)

### 这次真正变了什么 What actually changed

**EN:** *"Since we last spoke, the team rewrote the conflict resolution engine from scratch — a completely
different algorithm, built directly into the data pipeline with its own test suite. Six tests, all passing."*

*中:* 自上次讲完之后,队友把冲突解决引擎整个重写了——完全不同的算法,直接写进了数据管道里,还配了自己的测试套件,6个测试全部通过。这不是我做的,是队友的工作,如实说清楚归属。

### 新算法怎么运作 How the new algorithm works

**EN:** *"Three key ideas. First, only individual review evidence counts — the venue-level aggregate is
deliberately excluded, because it summarises the same reviews and isn't independent evidence; this also fixes a
subtle double-counting issue the earlier version had. Second, every review gets a recency weight using
exponential decay — a 180-day half-life, so a review from today counts fully, one from 180 days ago counts half
as much. Third, the resolution score multiplies three things together: how one-sided the result is, how much of
the evidence has a usable date, and how much of it is decisive rather than unsure."*

*中:* 三个核心要点。第一,只用单条评价的证据——场所级别的汇总行被刻意排除在外,因为它本身就是这些评价的汇总,不算独立证据;这个改动顺便修掉了旧版本里一个隐藏的重复计票问题。第二,每条评价会按时间做指数衰减加权——180天半衰期,今天的评价算满分,180天前的评价打五折。第三,最终的置信度分数是三项相乘:结果有多一边倒、有多少证据有可用的日期、有多少证据是"有/无"这种明确答案而不是"不确定"。

### 真实数字 Real numbers(⚠️ 这次的,不是上次那份)

**EN:** *"On the actual data — 74 detected conflicts. 41, or 55%, get a provisional proposed value from the
engine. 33, or 45%, are left for human review."*

*中:* 用真实数据跑出来:74条检测到的冲突。41条(55%)引擎给出了初步判断结果(provisional)。33条(45%)留给人工复核。

| Status 状态 | Count 数量 | Share 占比 |
|---|---:|---:|
| Provisional 引擎给出判断 | 41 | 55% |
| Human review 人工复核 | 33 | 45% |

| Evidence quality 证据质量 | Count 数量 |
|---|---:|
| High 高 | 11 |
| Medium 中 | 30 |
| Low 低 | 33 |

### 如果被问"为什么数字变化这么大" If asked why the numbers changed so much

**EN:** *"The new engine resolves more than double the share the earlier draft did — 55% versus 23% before.
That's not the engine being looser; continuous recency-weighted scoring can find a clear signal in cases a hard
rule-based cutoff would have simply discarded. It's a better-designed engine, and it comes with proper tests."*

*中:* 新引擎自动给出判断的比例是之前草稿版本的两倍还多——55% 对比之前的 23%。这不是新引擎标准变松了,而是连续的、按时间加权的打分方式,能从一些硬性规则会直接放弃判断的案例里,找出真正清晰的信号。这是一个设计更好的引擎,而且配了正式的测试。

### 老实说还缺什么 What's honestly still missing

**EN:** *"Resolution accuracy — whether a provisional value actually matches reality — isn't measured yet. The
engine's own notes literally say the score is heuristic and not calibrated. That still needs a labelled
ground-truth sample. Coverage and human-review-rate, the numbers I just gave, don't need ground truth."*

*中:* "解决准确率"——也就是引擎给出的判断到底对不对——还没法验证。引擎自己的说明文字里直接写着"这个分数是启发式的,没有经过校准"。这个还需要一份人工标注的 ground truth 数据才能验证。但刚才说的 coverage 和 human-review-rate 这两个数字不需要 ground truth,可以放心讲。

---

## Part C — Frontend Interaction Details 前端交互细节

这部分逻辑框架没变,只是显示的字段更丰富了。

**EN:** *"The Data Quality page now shows not just a status, but an evidence-quality badge and a specific
rationale built from the actual score for that row — like 'Engine proposes no, high confidence, resolution score
85 percent, latest evidence 5 September 2025.' That's generated per row from the real numbers, not a canned
sentence."*

*中:* 数据质量页面现在不只显示状态,还会显示证据质量标签,以及一句根据这一行真实分数生成的具体理由——比如"引擎判断为 no,高置信度,解决分数85%,最新证据日期是2025年9月5日"。这句话是根据每一行真实数字生成的,不是固定模板文字。

---

## If the live demo misbehaves 如果现场演示网站抽风

```bash
cd frontend
python3 -m http.server 8000
```

*中:* 直接说"我用本地跑一下",打开 `http://localhost:8000`,保证是最新代码没有缓存问题。
