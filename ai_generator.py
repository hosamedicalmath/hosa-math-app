# ai_generator.py
import os
import json
import time
import random
import requests
from config import OPENROUTER_API_KEY, MODEL, API_URL, EXAM_SIZE

# Strict JSON schema required from the model:
# {
#   "question": string (the word problem, multi-step),
#   "answer": number (final numeric answer before rounding),
#   "rounding": "normal" | "pediatric" | "tenth" | "hundredth",
#   "solution": string (step-by-step explanation showing intermediate calculations),
#   "category": "math"|"conversion"|"drug"|"dilution"|"interpret"
# }

# The HOSA text is included verbatim in the prompt below.
HOSA_GUIDELINES_TEXT = r"""
HOSA Medical Math ILC Guidelines (August 2025) Page 1 of 4
The expectation is that competitors read and are aware of all content within these guidelines and associated links. Successful competitors will
study all links for detailed information.
Medical Math
Health Science Event ..……………………………………………………………………………….……………….….
Eligible Divisions: Secondary & Postsecondary / Collegiate Round 1: 50 Q test in 90 minutes Digital Upload: NO
Solo Event: 1 competitor
New for 2025 – 2026
DHO: Health Science resource has been updated to latest edition. Editorial updates have been made.
Event Summary
Medical Math allows members to gain the knowledge and skills required to identify, solve, and apply mathematical
principles. This competitive event consists of a written test. In the event of a tie, the tie-breaker questions will be
judged to break the tie. It aims to inspire members to learn about the integration of mathematics in health care,
including temperature, weights, and measures used in the health community.
Dress Code
Proper business attire or official HOSA uniform. Bonus points will be awarded for proper dress.
Competitor Must Provide:
● Photo ID
● Two #2 lead pencils (not mechanical) with erasers
HOSA Conference Staff will provide equipment and supplies as listed in Appendix I.
General Rules
1. Competitors must be familiar with and adhere to the General Rules and Regulations.
Official References
2. The references below are used in developing the test questions:
a. Simmers, L., Simmers-Nartker, K., Simmers-Kobelak, S., Morris, L. DHO: Health Science. Cengage
Learning, Latest edition
b. Kennamer, Michael, Math for Health Care Professionals. Cengage, Latest edition.
c. Craig, Gloria P., Dosage Calculations Made Easy. Wolters Kluwer, Latest edition.
Written Test
3. Test Instructions: The written test will consist of 50 fill-in-the-blank items in a maximum of 90
 minutes.
4. A series of ten (10) complex, multi-step tiebreaker questions will be administered
 with the original test.
5. Time Remaining Announcements: There will be NO verbal announcements for time remaining
 during ILC testing. All ILC testing will be completed in the Testing Center and competitors are
 responsible for monitoring their own time.
6. At the International Leadership Conference, HOSA will provide basic handheld calculators (no graphing
 calculators) for addition, subtraction, division, multiplication, and square root calculations.
7. Test Plan:
 The test plan for the Medical Math Test is:
● Mathematical essentials - 5%
● Measurement and conversion problems - 20%
● Drug dosages and intravenous solutions - 35%
● Dilutions, solutions, and concentrations - 25%
● Interpreting medical information - 15%
○ Charts, graphs, tables
○ Basic statistics: mean, median, mode
8. Abbreviations will be used in the written problems. In addition, the test will use standard medical
abbreviations as designated in the Simmers DHO: Health Science reference.

9. At least half of the computation and calculation problems involve conversions.
10. The medical math “Reference Materials Summary” included in these guidelines (page 4) will be used
 as the official reference for the test for uniformity. Competitors may NOT use this summary page or
 any conversion chart or resource during the test.
11. When a Scantron form is used – the Scantron form for this event will require
 competitors to grid their responses with pencils. Numbers must be written with
 the last number of the answer in the far right box. (See sample to the right). When
 a paper/pencil test is used or administered on a computer, the competitor will write in
or key in their response to each question.
12. ROUNDING: Converting between measurement systems will often render a
 different answer depending on which systems and conversions are used. The
 answer to a calculation problem will be the same after appropriate rounding. When
 determining a solution, round only the final answer after completing all the
 calculation steps.
When rounding decimal numbers to the nearest tenths, hundredths, or thousandths place, look to the
immediate right of the digit located in the position to be rounded. If the number to the direct right is 5 or
larger, round up one number and drop everything that follows. If the number to the direct right is 4 or smaller,
leave the position being rounded as is and drop everything that follows.
In specific situations, answers will be rounded per medical protocol. For example, pediatric dosage is always
rounded DOWN to avoid potential overdose. Unless otherwise indicated, all answers should be rounded to
the nearest whole number. (Examples: 31.249 (rounded down) = 31 and 23.75 (rounded up) = 24).
13. USE OF ZERO: Decimal expressions of less than 1 should be preceded by a zero – “leading zero”. A
whole number should never be followed by a decimal point and a zero – “trailing zero”.
14. Sample Test Questions
*Competitors will grid-in (or write-in) their answers to the test problems.
 1. An IV bag of 500 mL solution is started at 1900. The flow rate is 38 gtts per minute, and the
 drop factor is 10 gtts per mL. At what time (24-hour clock) will this infusion finish?
 Craig pp 174-178
 Solution 38 gtts/1 min x 1 mL/10 gtts = 3.8 mL/min
3.8 mL/1 min x 60 min/1 hr = 228 mL/hr
 500 mL x 1 hr/228 mL = 2.1929824 hr
 0.1929824 hr x 60 min/1 hr = 11.578944 minutes
 1900 hr + 2 hrs 11.578944 min (Rounded = 12 minutes)
 1900 hours + 2hrs 12 min = 2112 hours
2112 hours
 2. A patient with an eating disorder weighs 95½ lbs. What is the patient’s weight in kg?
 Round to the nearest tenth.
 Simmers pp 383
 Solution 95.5 lb x 1 kg/2.2 lbs = 43.40909 kg Rounded = 43.4 kg
 3. How many grams of sodium chloride are needed to prepare 500 mL of a 5% solution?
 Kennamer pp235
 Solution 5% = 5 g/100 mL = 0.05 g/1 mL
 0.05 g/1 mL x 500 mL = 25 g
Final Scoring
15. In the event of a tie, successive tiebreaker questions will be judged until a winner is determined. Correct
spelling is required for an item to be considered correct in the tiebreaker.
...
Medical Math – SS/PSC
Reference Materials Summary
METRIC EQUIVALENTS
Length Temperature
1 meter (m) = 100 centimeters (cm) = 1000 millimeters
(mm)
1 centimeters (cm) = 10 millimeters (mm)
oC (Degrees Celsius) = (oF - 32) 5/9
oF (Degrees Fahrenheit) = (oC) 9/5 + 32
Weight Weight Conversion
1 kilogram (kg) = 1000 grams (g) 1 kilogram (kg) = 2.2 pounds (lb)
1 gram (g) = 1000 milligrams (mg) 1 pound (lb) = 16 ounces (oz)
1 milligram (mg) = 1000 micrograms (mcg)
Volume for Solids Volume for Fluids
1000 cubic decimeters (dm) = 1 cubic meter (m3
) 1 liter (L) = 1000 milliliters (mL)
1000 cubic centimeters (cm3
) = 1 cubic decimeter (dm3
) 10 centiliters (cL) = 1 deciliter (dL)
1000 cubic millimeters (mm3
)= 1 cubic centimeter (cm3
or cc)
10 deciliters (dL) = 1 liter (L)
1 cubic centimeters (cm3 or cc) = 1 milliliter
(mL)
APPROXIMATE EQUIVALENTS AMONG SYSTEMS
Metric Household/English
240 milliliters (mL) 1 cup = 8 ounces (oz) = 16 tablespoons (tbsp)
30 milliliters (mL) 1 ounce (oz) = 2 tablespoons (tbsp) = 6 teaspoons (tsp)
15 milliliters (mL) 1 tablespoon (tbsp) = 3 teaspoons (tsp)
5 milliliters (mL) 1 teaspoon (tsp)
1 milliliter (mL) 15 drops (gtts)
0.0667 milliliters (mL) 1 drop (gtt)
1 meter (m) 39.4 inches (in)
2.54 centimeters (cm) 1 inch (in)
1 foot (ft) = 12 inches (in)
Formulas
Standard Deviation Formula
 for Sample Data
Body Surface Area
BSA (m2
) = √([height (cm) x weight(kg)]/3,600)
BSA (m2
) = √([height (in) x weight(lb)]/3,131)
NOTE: This reference may NOT be used during testing.
"""

AI_PROMPT_PREFIX = f"""
You are an expert item-writer for HOSA Medical Math (ILC level). Use the following rules and reference material EXACTLY as given.

INSTRUCTIONS:
1) Read the HOSA guidelines below (verbatim) and ensure every generated item follows them.
2) Produce one extremely challenging, multi-step word problem that tests the rubric categories stated in the HOSA Test Plan:
   - Mathematical essentials,
   - Measurement & conversion,
   - Drug dosages & IV solutions,
   - Dilutions/solutions/concentrations,
   - Interpreting medical info (charts/tables/basic stats).
3) The item MUST be multi-step (>=3 arithmetic steps), realistic and clinical, and require at least one conversion for >=50% of items.
4) Always compute exact intermediate numeric values in the solution. Round ONLY the final numeric answer according to the HOSA rounding rules below.
5) Enforce rounding behavior: pediatric → round DOWN at end; otherwise default to nearest whole unless prompt says nearest tenth/hundredth; leading zero required for decimals < 1; trailing zeros forbidden (e.g., 5 not 5.0).
6) Output JSON ONLY. No prose. Strict schema:

{{
  "question": string,
  "answer": number,
  "rounding": "normal" | "pediatric" | "tenth" | "hundredth",
  "solution": string,
  "category": "math"|"conversion"|"drug"|"dilution"|"interpret"
}}

HOSA GUIDELINES:
{HOSA_GUIDELINES_TEXT}

Additional constraints:
- Use the "Reference Materials Summary" conversions where needed (include units explicitly).
- If including time (e.g., infusion finish time) provide answer as 24-hour numeric time (e.g., 2112).
- If the problem needs BSA, include formula and compute it.
- Make problems long (3-6 steps), require unit conversions, and be unambiguous.
- Make the numeric answer a plain number (no commas). If final answer is less than 1, include leading zero (0.x).
- Tag category appropriately.
- Assume competitor uses only simple calculator functionality; avoid trig or calculus.

Return the JSON object and nothing else.
"""

def call_model(prompt_text, retries=2, timeout=20):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": 800
    }
    for attempt in range(retries+1):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
            r.raise_for_status()
            j = r.json()
            # Many providers return structure with choices -> message -> content
            content = j["choices"][0]["message"]["content"]
            return content
        except Exception as e:
            # wait and retry
            if attempt < retries:
                time.sleep(1 + attempt)
                continue
            else:
                return None

def parse_json_str(s):
    try:
        return json.loads(s)
    except:
        # Try to extract first {...} block
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except:
                return None
        return None

def generate_question_ai(category):
    prompt = AI_PROMPT_PREFIX + f"\n\nCATEGORY: {category}\n\nProduce JSON now.\n"
    raw = call_model(prompt)
    if not raw:
        return None
    parsed = parse_json_str(raw)
    if parsed and validate_item(parsed):
        parsed['category'] = category
        return parsed
    return None

def validate_item(item):
    # Basic validation of required fields and types
    if not isinstance(item, dict):
        return False
    keys = {"question","answer","rounding","solution","category"}
    if not keys.issubset(set(item.keys())):
        return False
    if not isinstance(item['question'], str):
        return False
    if not (isinstance(item['answer'], (int,float))):
        return False
    if item['rounding'] not in ("normal","pediatric","tenth","hundredth"):
        return False
    if not isinstance(item['solution'], str):
        return False
    if item.get('category') not in (None, "math","conversion","drug","dilution","interpret"):
        return False
    return True

# Fallback local generators to ensure app always works
def fallback_generate(category):
    # Produce an item matching the category with multi-step solution.
    if category == "math":
        # mg/kg split
        weight = random.randint(50, 85)  # kg
        mgkg = random.randint(8, 15)
        doses = random.choice([2,3,4])
        total = weight * mgkg
        per = total / doses
        return {
            "question": f"A patient weighs {weight} kg. The physician orders {mgkg} mg/kg/day of Drug A. The dose is to be divided into {doses} equal doses. How many mg should be given per dose?",
            "answer": per,
            "rounding": "normal",
            "solution": f"{weight} kg × {mgkg} mg/kg = {total} mg/day → {total}/{doses} = {per} mg per dose (round final answer).",
            "category": "math"
        }
    if category == "conversion":
        ml = random.choice([95, 125, 240, 480])
        tsp = ml / 5.0
        return {
            "question": f"Convert {ml} mL to teaspoons (tsp). Use 1 tsp = 5 mL.",
            "answer": tsp,
            "rounding": "normal",
            "solution": f"{ml} mL ÷ 5 mL/tsp = {tsp} tsp. Round final answer.",
            "category": "conversion"
        }
    if category == "drug":
        # pediatric rounding example
        weight_lb = random.randint(40,80)
        weight_kg = round(weight_lb/2.2,3)
        mgkg = random.randint(5,12)
        doses = random.choice([2,3])
        total_mg = weight_kg * mgkg
        per_dose = total_mg / doses
        # assume tablet strength for conversion
        tab_mg = random.choice([50,100,125,250])
        tabs = per_dose / tab_mg
        return {
            "question": f"A pediatric patient weighs {weight_lb} lb. The order is {mgkg} mg/kg/day divided into {doses} doses. Medication is {tab_mg} mg per tablet. How many tablets per dose? (pediatric rounding applies — round down at the end.)",
            "answer": tabs,
            "rounding": "pediatric",
            "solution": f"Convert lb→kg: {weight_lb} ÷ 2.2 = {weight_kg} kg. Total mg/day = {weight_kg}×{mgkg} = {total_mg} mg. Per dose = {total_mg}/{doses} = {per_dose} mg. Tablets = {per_dose}/{tab_mg} = {tabs}. Round down at the end.",
            "category": "drug"
        }
    if category == "dilution":
        c1 = random.choice([20,50,80])
        c2 = random.choice([2,5,10])
        v2 = random.choice([250,500,750])
        v1 = (c2 * v2) / c1
        return {
            "question": f"Using C1V1 = C2V2: Stock solution {c1}% to make {v2} mL of {c2}% solution. How many mL of stock are needed?",
            "answer": v1,
            "rounding": "normal",
            "solution": f"V1 = ({c2}% × {v2} mL)/{c1}% = {v1} mL. Round final answer.",
            "category": "dilution"
        }
    # interpret
    vals = [random.randint(60,110) for _ in range(5)]
    mean = sum(vals)/len(vals)
    return {
        "question": f"Heart rate readings: {vals}. What is the mean heart rate?",
        "answer": mean,
        "rounding": "normal",
        "solution": f"Mean = sum({vals})/5 = {mean}. Round final answer.",
        "category": "interpret"
    }

def generate_exam():
    """
    Create EXAM_SIZE items by requested category distribution matching HOSA test plan.
    Distribution uses HOSA percentages but scaled to EXAM_SIZE.
    """
    # weights from guideline: math 5%, conversion 20%, drug 35%, dilution 25%, interpret 15%
    weights = {
        "math": 0.05,
        "conversion": 0.20,
        "drug": 0.35,
        "dilution": 0.25,
        "interpret": 0.15
    }
    # compute counts, ensure sum = EXAM_SIZE (adjust last category)
    counts = {}
    total_assigned = 0
    for i,(k,w) in enumerate(weights.items()):
        if i < len(weights)-1:
            counts[k] = max(1, int(round(w * EXAM_SIZE)))
            total_assigned += counts[k]
    # fix last
    last = list(weights.keys())[-1]
    counts[last] = EXAM_SIZE - total_assigned
    # generate items
    exam = []
    for cat, count in counts.items():
        for _ in range(count):
            item = generate_question_ai(cat)
            if not item:
                item = fallback_generate(cat)
            # Ensure answer is numeric and keep raw answer value (unrounded)
            # attach id later
            exam.append(item)
    # shuffle
    random.shuffle(exam)
    for idx,item in enumerate(exam):
        item['id'] = idx+1
    return exam

if __name__ == "__main__":
    # quick local test
    ex = generate_exam()
    print(json.dumps(ex[:3], indent=2))
