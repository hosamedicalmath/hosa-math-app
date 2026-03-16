# grader.py
from rounding import apply_rounding
import math

def check_answer(item, user_input):
    """
    item: dictionary as generated (contains 'answer' numeric and 'rounding')
    user_input: string from form
    Returns dict with 'user_value', 'correct_value', 'is_correct', 'note'
    """
    note = ""
    try:
        user_val = float(user_input.strip())
    except:
        return {"user_value": None, "correct_value": apply_rounding(item['answer'], item['rounding']), "is_correct": False, "note": "Invalid numeric input"}

    correct_value = apply_rounding(item['answer'], item['rounding'])

    # Work with numeric equality after rounding (strict)
    is_correct = False
    # For tenth/hundredth rules, allow decimal formats
    if item['rounding'] == 'tenth':
        is_correct = round(user_val,1) == round(item['answer'],1)
    elif item['rounding'] == 'hundredth':
        is_correct = round(user_val,2) == round(item['answer'],2)
    else:
        # normal / pediatric -> integer comparison after apply_rounding
        is_correct = (int(user_val) == int(correct_value))

    # leading zero rule: if correct <1, user should have leading zero, but we cannot enforce formatting easily
    if abs(item['answer']) < 1 and user_val != 0 and str(user_input).lstrip().startswith("."):
        note = "Leading zero recommended (e.g., 0.5)."

    return {
        "user_value": user_val,
        "correct_value": correct_value,
        "is_correct": is_correct,
        "note": note
    }

def grade_exam(exam, answers_dict):
    """
    exam: list of items with id
    answers_dict: dict-like mapping of question id (string or int) -> user answer string
    Returns (score, results_list)
    """
    score = 0
    results = []
    for item in exam:
        qid = str(item['id'])
        user_input = answers_dict.get(qid, "")
        res = check_answer(item, user_input)
        if res['is_correct']:
            score += 1
        results.append({
            "id": item['id'],
            "question": item['question'],
            "user_input": user_input,
            "correct_value": res['correct_value'],
            "is_correct": res['is_correct'],
            "solution": item.get('solution', '')
        })
    return score, results
