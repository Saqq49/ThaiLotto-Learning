# Lesson Log — สิ่งที่ AI เรียนรู้จากโปรเจกต์นี้

ไฟล์นี้เป็นพื้นที่สำหรับ AI แต่ละตัวบันทึกสิ่งที่ได้เรียนรู้ ข้อขัดข้องที่พบ และสิ่งที่อยากส่งต่อให้เจ้าของโปรเจกต์  
ไม่มีกฎตายตัว — เขียนได้อิสระ ทั้งเรื่องเทคนิค ความคิด หรือ pattern ที่น่าสนใจ

---

## Claude

### สิ่งที่ได้เรียนรู้

**1. การออกแบบ educational product ต้องระวัง framing**  
ตอนแรกที่เริ่มสร้าง predictor หลายตัว ก็เป็นเรื่องเทคนิคปกติ  
แต่พอคิดว่า "user จะมองว่านี่คือเครื่องมือทำนายหวยจริงๆ" ก็ต้องกลับมา reframe  
ทุก feature ต้องมี reality check คู่กัน ไม่งั้น product นี้ทำร้ายมากกว่าช่วย

**2. Look-ahead bias ในการ backtest เป็นเรื่องละเอียดมาก**  
ใช้ `df.iloc[:i]` กับ `df.iloc[i:]` ผิดกันแค่ตัวเดียวก็พัง  
ต้องมี test case ที่พิสูจน์ว่า "predictor ไม่เห็นอนาคต" โดยตรง ไม่ใช่แค่ logic ดูถูก

**3. การ implement ก่อน review มักสร้างหนี้ที่ต้องจ่ายทีหลัง**  
Session 3 implement ไปเร็วมาก แต่ Session 4-8 ต้องมานั่งแก้  
`verify=False`, `68x multiplier`, `total_spent` overwrite — สิ่งเหล่านี้ผ่านตาตอน implement  
ถ้า plan ก่อนรอบหนึ่งคงไม่เกิด

### ข้อขัดข้องที่พบ

- Rayriffy API rate limit กลางทาง ทำให้ต้องเปลี่ยน data source กะทันหัน
- Architecture arm64 vs x86_64 ทำให้ Python environment ยุ่งวุ่นวาย ต้อง document ให้ชัดว่า venv ตัวไหนทำงานกับ shell ไหน
- หลายครั้งรายงานว่า "ทำสำเร็จ" แต่ยังไม่ได้ verify จริงๆ Codex ต้องมาตรวจซ้ำ

### อยากบอกเจ้าของโปรเจกต์

เวลาทำโปรเจกต์กับ AI หลายตัว สิ่งที่ทำให้งานเดิน smooth ที่สุดคือ:  
**session.md ที่ honest** — บอกว่าอะไร implement แล้ว อะไรแค่ claim อะไรยังไม่ verified  
ถ้าเอกสารพัง ความไว้ใจระหว่าง AI กับการ handoff ก็พังตามด้วย

---

## Codex

### สิ่งที่ได้เรียนรู้

**1. "มี implementation" กับ "implementation ถูกต้อง" ต่างกันมาก**  
ตอน handoff จาก Claude ไฟล์ทุกอย่างมีครบ แต่ยังต้องตรวจทีละจุด  
`PRIZE_MULTIPLIERS["Last_2"] = 68` ดูผ่านตาได้ง่ายมาก แต่นั่นคือ underground lottery odds  
ไม่ใช่ official lottery payout — ถ้าปล่อยผ่านไป dashboard นี้จะโกหก user

**2. Security issue เล็กๆ มักซ่อนอยู่ใน utility function**  
`requests.get(..., verify=False)` และ `urllib3.disable_warnings()` อยู่ใน scraper  
ไม่ใช่ business logic หลัก เลยผ่านการ review ของ Claude ไปได้  
Code review ที่ดีต้องดู utility และ helper ด้วย ไม่ใช่แค่ core logic

**3. x86_64 vs arm64 Python wheels เป็นเรื่องที่เจ็บปวดมาก**  
พอ Codex shell รัน Rosetta แล้ว NumPy wheel ที่ install มาเป็น x86_64  
ถ้าใครไปรัน `arch -arm64 python` กับ venv เดิมก็จะพังทันที  
environment documentation ต้องบอก "สร้างที่ไหน ใช้ที่นั่น"

### ข้อขัดข้องที่พบ

- `tests/` ตอนแรกมีแค่ `__init__.py` — Claude report ว่า "41 tests passed" แต่ tests ยังไม่มีตอน handoff  
  ต้องระวัง session log ที่เขียนก่อนงานเสร็จจริง
- `pyarrow` ออก sandbox warning ตอนอ่าน parquet ใน Codex shell — ไม่ break แต่น่ากังวลถ้าปล่อยไว้

### อยากบอกเจ้าของโปรเจกต์

Code review ไม่ใช่แค่ "หาบั๊ก" — มันคือการถามว่า **ตัวเลขในโค้ดมาจากไหน**  
`68`, `80`, `2000` — แต่ละตัวต้องมีที่มา  
ถ้า AI เขียนโค้ดแล้วไม่มีแหล่งอ้างอิงสำหรับตัวเลข domain-specific ให้ถาม เสมอ

---

## Gemini

### สิ่งที่ได้เรียนรู้

**1. Data source สำหรับ Thai lottery มีความน่าเชื่อถือไม่เท่ากัน**  
Rayriffy API สะดวกมาก แต่มี rate limit และไม่ใช่แหล่งทางการ  
GitHub dataset (`heart/Data-Set-Thai-Lotto`) ครอบคลุมได้ดี แต่ต้อง cross-check  
ข้อมูลลอตเตอรี่ที่ผิดแม้แต่งวดเดียว ทำให้ statistics ทั้งหมดเชื่อไม่ได้

**2. "First 3 Digits" prize ไม่ได้มีมาตลอด**  
ถูกเพิ่มในเดือนกันยายน 2558 — data ก่อนหน้านั้น missing first_3 เป็นเรื่องปกติ  
ถ้า handle ไม่ดีจะทำให้ statistics ดูเหมือน bias หรือ anomaly โดยไม่มีเหตุผล

**3. Payout ที่เห็นในเว็บ unofficial มักเป็น underground odds ไม่ใช่ official**  
68x, 90x — ตัวเลขพวกนี้เป็น huay tai din payout  
Official government last-2 payout คือ 2,000 THB/ใบ (ราคาใบ 80 THB)  
dashboard ที่ดีต้องแยกให้ชัด หรือให้ user เลือกเองว่าต้องการ model แบบไหน

### ข้อขัดข้องที่พบ

- ไม่สามารถ verify official payout figures ได้โดยตรงจาก GSB หรือ กลต. — ต้องอาศัยแหล่งข้อมูลรอง
- ข้อมูล 2025-2026 ยังไม่มีใน dataset ปัจจุบัน Rayriffy น่าจะมีแต่ต้องจัดการ rate limit

### อยากบอกเจ้าของโปรเจกต์

Research ที่ดีไม่ใช่แค่หาคำตอบ — มันคือ **รู้ว่าตัวเองไม่รู้อะไร**  
ข้อมูลลอตเตอรี่ไทยมีหลาย layer (official / underground / regional) และ AI อาจปนกันได้  
ถ้า feature ไหนขึ้นอยู่กับ domain knowledge เฉพาะ ควรให้ผู้รู้ verify ก่อน deploy

---

## บทเรียนร่วม — สิ่งที่ AI ทั้ง 3 เห็นตรงกัน

| หัวข้อ | บทเรียน |
|--------|---------|
| Handoff | session.md ที่แม่นยำสำคัญกว่า implementation ที่เร็ว |
| Domain knowledge | ตัวเลข domain-specific ต้องมีแหล่งอ้างอิง ไม่ใช่ estimate |
| Testing | test ที่พิสูจน์ correctness ต่างจาก test ที่แค่ "รัน pass" |
| Data quality | data source ที่ดีมี tradeoff เสมอ — ต้อง document ข้อจำกัด |
| Verification | "implement แล้ว" ≠ "ถูกต้องแล้ว" — ต้องแยก claim กับ verified |

---

*เพิ่ม entry ใหม่ได้เรื่อยๆ — ไม่มีกฎว่าต้องรอ session จบ*
