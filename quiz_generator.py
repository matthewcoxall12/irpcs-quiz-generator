import random
import json
from typing import List, Dict, Any

# Load questions from irpcs_quiz.json
try:
    with open('irpcs_quiz.json', 'r') as f:
        IRPCS_QUESTIONS = json.load(f)
except:
    IRPCS_QUESTIONS = []

# Sample question templates and data
MULTIPLE_CHOICE_TEMPLATES = [
    {
        "type": "Multiple Choice",
        "question": "In restricted visibility, a power-driven vessel making way through the water shall sound:",
        "choices": [
            "One prolonged blast at intervals of not more than 2 minutes",
            "Two prolonged blasts at intervals of not more than 2 minutes",
            "One short blast at intervals of not more than 1 minute",
            "Five short blasts at intervals of not more than 1 minute"
        ],
        "answer": "One prolonged blast at intervals of not more than 2 minutes",
        "difficulty": "hard",
        "rule_reference": "Rule 35(a)"
    },
    {
        "type": "Multiple Choice",
        "question": "When two power-driven vessels are crossing, which vessel shall keep out of the way?",
        "choices": [
            "The vessel which has the other on her own port side",
            "The vessel which has the other on her own starboard side",
            "The larger vessel",
            "The vessel with the higher speed"
        ],
        "answer": "The vessel which has the other on her own port side",
        "difficulty": "medium",
        "rule_reference": "Rule 15"
    },
    {
        "type": "Multiple Choice",
        "question": "A vessel engaged in underwater operations, when restricted in her ability to maneuver, shall display:",
        "choices": [
            "Three all-round lights in a vertical line, the highest and lowest being red and the middle one being white",
            "Three all-round lights in a vertical line, all being red",
            "Two all-round lights in a vertical line, the upper being red and the lower being white",
            "Two all-round lights in a vertical line, both being red"
        ],
        "answer": "Three all-round lights in a vertical line, the highest and lowest being red and the middle one being white",
        "difficulty": "hard",
        "rule_reference": "Rule 27(d)"
    },
    {
        "type": "Multiple Choice",
        "question": "In restricted visibility, a vessel engaged in towing, when making way through the water, shall sound:",
        "choices": [
            "One prolonged blast followed by two short blasts at intervals of not more than 2 minutes",
            "One prolonged blast followed by three short blasts at intervals of not more than 2 minutes",
            "One prolonged blast followed by two short blasts at intervals of not more than 1 minute",
            "One prolonged blast followed by three short blasts at intervals of not more than 1 minute"
        ],
        "answer": "One prolonged blast followed by three short blasts at intervals of not more than 2 minutes",
        "difficulty": "extreme",
        "rule_reference": "Rule 35(e)"
    }
]

FILL_IN_THE_GAP_QUESTIONS = [
    {
        "type": "Fill in the Gap",
        "question": "A vessel engaged in fishing, when at anchor, shall sound _____ blasts every two minutes. A vessel restricted in her ability to maneuver, when at anchor, shall sound _____ blasts every two minutes. A vessel engaged in underwater operations, when at anchor, shall sound _____ blasts every two minutes.",
        "answer": "one prolonged followed by two short, one prolonged followed by two short, one prolonged followed by two short",
        "difficulty": "hard",
        "rule_reference": "Rule 35(g), (h), (i)"
    },
    {
        "type": "Fill in the Gap",
        "question": "In restricted visibility, a vessel engaged in fishing, when making way through the water, shall sound _____ blasts every two minutes. A vessel restricted in her ability to maneuver shall sound _____ blasts every two minutes. A vessel engaged in towing shall sound _____ blasts every two minutes.",
        "answer": "one prolonged followed by two short, one prolonged followed by two short, one prolonged followed by two short",
        "difficulty": "hard",
        "rule_reference": "Rule 35(c), (d), (e)"
    },
    {
        "type": "Fill in the Gap",
        "question": "A vessel engaged in fishing, when underway, shall show: _____ sidelights and _____ sternlight. A vessel engaged in trawling shall show: _____ sidelights, _____ sternlight, and _____ all-round lights in a vertical line.",
        "answer": "red and green, white, red and green, white, two",
        "difficulty": "hard",
        "rule_reference": "Rule 26"
    },
    {
        "type": "Fill in the Gap",
        "question": "A vessel engaged in underwater operations, when restricted in her ability to maneuver, shall exhibit: _____ all-round lights in a vertical line where they can best be seen. The highest and lowest of these lights shall be _____ and the middle light shall be _____. She shall also exhibit _____ shapes for a vessel restricted in her ability to maneuver.",
        "answer": "three, red, white, the appropriate",
        "difficulty": "extreme",
        "rule_reference": "Rule 27(d)"
    }
]

WRITTEN_ANSWER_QUESTIONS = [
    {
        "type": "Written Answer",
        "question": "Explain the correct procedure for a power-driven vessel when encountering a vessel engaged in fishing in restricted visibility.",
        "answer": "A power-driven vessel shall, when possible, avoid crossing ahead of a vessel engaged in fishing. When crossing ahead of a vessel engaged in fishing, the power-driven vessel shall alter course to starboard. The vessel engaged in fishing shall maintain her course and speed. Both vessels shall sound the appropriate sound signals for restricted visibility.",
        "difficulty": "hard",
        "rule_reference": "Rule 19(d)"
    },
    {
        "type": "Written Answer",
        "question": "Describe the lights and shapes that must be exhibited by a vessel engaged in underwater operations when restricted in her ability to maneuver.",
        "answer": "A vessel engaged in underwater operations, when restricted in her ability to maneuver, shall exhibit three all-round lights in a vertical line where they can best be seen. The highest and lowest of these lights shall be red and the middle light shall be white. She shall also exhibit the appropriate shapes for a vessel restricted in her ability to maneuver.",
        "difficulty": "hard",
        "rule_reference": "Rule 27(d)"
    },
    {
        "type": "Written Answer",
        "question": "Explain the responsibilities of a vessel overtaking another vessel according to the IRPCS.",
        "answer": "A vessel overtaking another vessel shall keep out of the way of the vessel being overtaken. A vessel shall be deemed to be overtaking when coming up with another vessel from a direction more than 22.5 degrees abaft her beam. When in doubt, she shall assume that this is the case. A vessel coming up with another vessel from a direction more than 22.5 degrees abaft her beam shall be deemed to be an overtaking vessel.",
        "difficulty": "medium",
        "rule_reference": "Rule 13"
    },
    {
        "type": "Written Answer",
        "question": "Explain the complete procedure for a power-driven vessel when encountering a vessel engaged in fishing in restricted visibility, including all required sound signals, lights, and shapes that must be exhibited by both vessels.",
        "answer": "A power-driven vessel shall, when possible, avoid crossing ahead of a vessel engaged in fishing. When crossing ahead of a vessel engaged in fishing, the power-driven vessel shall alter course to starboard. The vessel engaged in fishing shall maintain her course and speed. Both vessels shall sound the appropriate sound signals for restricted visibility. The power-driven vessel shall sound one prolonged blast at intervals of not more than 2 minutes. The vessel engaged in fishing shall sound one prolonged followed by two short blasts at intervals of not more than 2 minutes. The vessel engaged in fishing shall exhibit two all-round lights in a vertical line, the upper being red and the lower being white, and the appropriate shapes for a vessel engaged in fishing.",
        "difficulty": "extreme",
        "rule_reference": "Rule 19(d), 35(a), 35(c), 26"
    }
]

# Combine all questions
ALL_QUESTIONS = MULTIPLE_CHOICE_TEMPLATES + FILL_IN_THE_GAP_QUESTIONS + WRITTEN_ANSWER_QUESTIONS + IRPCS_QUESTIONS

def calculate_answer_similarity(student_answer: str, correct_answer: str) -> float:
    """
    Calculate the similarity between student's answer and correct answer.
    Returns a percentage between 0 and 100.
    """
    # Convert both answers to lowercase and split into words
    student_words = set(student_answer.lower().split())
    correct_words = set(correct_answer.lower().split())
    
    # Calculate word overlap
    overlap = len(student_words.intersection(correct_words))
    total_words = len(correct_words)
    
    # Calculate percentage
    if total_words == 0:
        return 0.0
    
    return (overlap / total_words) * 100

def generate_quiz(num_questions: int, difficulty: str = 'all', question_types: List[str] = None) -> List[Dict[str, Any]]:
    """
    Generate a quiz with the specified number of questions, difficulty level, and question types.
    
    Args:
        num_questions: Number of questions to generate (max 500)
        difficulty: Difficulty level ('easy', 'medium', 'hard', 'extreme', 'mixed', or 'all')
        question_types: List of question types to include
        
    Returns:
        List of question dictionaries
    """
    # Enforce maximum limit of 500 questions
    num_questions = min(num_questions, 500)
    
    if question_types is None:
        question_types = ['Multiple Choice', 'Fill in the Gap', 'Written Answer']
    
    # Filter questions by type
    available_questions = [q for q in ALL_QUESTIONS if q.get('type', 'Multiple Choice') in question_types]
    
    # Filter by difficulty if specified
    if difficulty != 'all' and difficulty != 'mixed':
        available_questions = [q for q in available_questions if q.get('difficulty', 'medium') == difficulty]
    elif difficulty == 'mixed':
        # For mixed difficulty, ensure a good distribution of difficulties
        difficulties = ['easy', 'medium', 'hard', 'extreme']
        questions_per_difficulty = num_questions // len(difficulties)
        selected_questions = []
        
        for diff in difficulties:
            diff_questions = [q for q in available_questions if q.get('difficulty', 'medium') == diff]
            if len(diff_questions) < questions_per_difficulty:
                # If we don't have enough questions for this difficulty, use what we have
                selected_questions.extend(diff_questions)
            else:
                selected_questions.extend(random.sample(diff_questions, questions_per_difficulty))
        
        # If we need more questions to reach num_questions, add them randomly
        while len(selected_questions) < num_questions:
            remaining = [q for q in available_questions if q not in selected_questions]
            if not remaining:
                break
            selected_questions.append(random.choice(remaining))
        
        return selected_questions[:num_questions]
    
    # Randomly select questions
    if len(available_questions) < num_questions:
        # If we don't have enough questions, we'll need to duplicate some
        selected_questions = []
        while len(selected_questions) < num_questions:
            selected_questions.extend(random.sample(available_questions, min(len(available_questions), num_questions - len(selected_questions))))
        selected_questions = selected_questions[:num_questions]
    else:
        selected_questions = random.sample(available_questions, num_questions)
    
    # Ensure all questions have a type field
    for question in selected_questions:
        if 'type' not in question:
            if 'choices' in question:
                question['type'] = 'Multiple Choice'
            elif 'answer' in question and ',' in question['answer']:
                question['type'] = 'Fill in the Gap'
            else:
                question['type'] = 'Written Answer'
    
    return selected_questions 