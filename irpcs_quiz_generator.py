import random
import json
from typing import List, Dict, Tuple, Optional

class IRPCSQuizGenerator:
    def __init__(self):
        self.question_templates = {
            "collision_avoidance": [
                {
                    "type": "Multiple Choice",
                    "difficulty": "easy",
                    "template": "According to Rule 8 (Action to avoid collision), what is the basic rule for avoiding collisions?",
                    "choices": [
                        "A. Keep going at the same speed",
                        "B. Take early action to avoid collision",
                        "C. Wait until you get close to change course",
                        "D. Sound five short blasts"
                    ],
                    "answer": "B. Take early action to avoid collision"
                },
                {
                    "type": "Image Question",
                    "difficulty": "medium",
                    "template": "According to Rule 18 (Responsibilities between vessels), when you see this vessel constrained by draft ahead, what is the minimum safe distance you must keep from it?",
                    "choices": [
                        "A. 500 meters",
                        "B. 200 meters",
                        "C. 100 meters",
                        "D. 1000 meters"
                    ],
                    "answer": "A. 500 meters",
                    "image": "images/vessel_distance.jpg"
                }
            ],
            "navigation_marks": [
                {
                    "type": "Image Question",
                    "difficulty": "easy",
                    "template": "According to Rule 20 (Application), what does this red buoy with a cone shape on top mean?",
                    "choices": [
                        "A. Keep this buoy on your left when going into port",
                        "B. Keep this buoy on your right when going into port",
                        "C. Danger area - stay away",
                        "D. Safe to pass on either side"
                    ],
                    "answer": "A. Keep this buoy on your left when going into port",
                    "image": "images/red_buoy.jpg"
                },
                {
                    "type": "Image Question",
                    "difficulty": "easy",
                    "template": "According to Rule 20 (Application), what does this green buoy with a cylinder shape on top mean?",
                    "choices": [
                        "A. Keep this buoy on your left when going into port",
                        "B. Keep this buoy on your right when going into port",
                        "C. Danger area - stay away",
                        "D. Safe to pass on either side"
                    ],
                    "answer": "B. Keep this buoy on your right when going into port",
                    "image": "images/green_buoy.jpg"
                }
            ],
            "lights_shapes": [
                {
                    "type": "Image Question",
                    "difficulty": "easy",
                    "template": "According to Rule 28 (Vessels constrained by their draft), what type of vessel shows these three red lights in a vertical line?",
                    "choices": [
                        "A. A large ship that needs deep water",
                        "B. A fishing boat",
                        "C. A stopped vessel",
                        "D. A broken down vessel"
                    ],
                    "answer": "A. A large ship that needs deep water",
                    "image": "images/three_red_lights.jpg"
                },
                {
                    "type": "Image Question",
                    "difficulty": "medium",
                    "template": "According to Rule 30 (Anchored vessels), what does this black ball shape mean when shown by a vessel during the day?",
                    "choices": [
                        "A. The vessel is stopped at anchor",
                        "B. The vessel is fishing",
                        "C. The vessel is broken down",
                        "D. The vessel needs deep water"
                    ],
                    "answer": "A. The vessel is stopped at anchor",
                    "image": "images/black_ball.jpg"
                }
            ],
            "sound_signals": [
                {
                    "type": "Multiple Choice",
                    "difficulty": "easy",
                    "template": "According to Rule 34 (Maneuvering and warning signals), what does one short blast of the horn mean?",
                    "choices": [
                        "A. I am turning right",
                        "B. I am turning left",
                        "C. I am going backwards",
                        "D. I am stopping"
                    ],
                    "answer": "A. I am turning right"
                },
                {
                    "type": "Multiple Choice",
                    "difficulty": "medium",
                    "template": "According to Rule 34 (Maneuvering and warning signals), what does it mean when you hear five short blasts?",
                    "choices": [
                        "A. The vessel is turning right",
                        "B. The vessel is turning left",
                        "C. The vessel is warning you that your intentions are unclear",
                        "D. The vessel is stopping"
                    ],
                    "answer": "C. The vessel is warning you that your intentions are unclear"
                }
            ],
            "restricted_visibility": [
                {
                    "type": "Image Question",
                    "difficulty": "easy",
                    "template": "According to Rule 19 (Conduct of vessels in restricted visibility), in fog like this, what should you do first?",
                    "choices": [
                        "A. Keep going at the same speed",
                        "B. Slow down and sound your horn",
                        "C. Stop completely",
                        "D. Go faster to get out of the fog"
                    ],
                    "answer": "B. Slow down and sound your horn",
                    "image": "images/fog.jpg"
                },
                {
                    "type": "Multiple Choice",
                    "difficulty": "medium",
                    "template": "According to Rule 35 (Sound signals in restricted visibility), how often should you sound your horn in fog?",
                    "choices": [
                        "A. Every minute",
                        "B. Every two minutes",
                        "C. Every five minutes",
                        "D. Every ten minutes"
                    ],
                    "answer": "B. Every two minutes"
                }
            ],
            "vessel_priorities": [
                {
                    "type": "Image Question",
                    "difficulty": "easy",
                    "template": "According to Rule 18 (Responsibilities between vessels), which vessel should give way in this situation?",
                    "choices": [
                        "A. The small boat",
                        "B. The large cargo ship",
                        "C. Both vessels",
                        "D. Neither vessel"
                    ],
                    "answer": "A. The small boat",
                    "image": "images/vessel_priority.jpg"
                },
                {
                    "type": "Multiple Choice",
                    "difficulty": "medium",
                    "template": "According to Rule 18 (Responsibilities between vessels), when should you stay at least 500 meters away from a large ship constrained by draft?",
                    "choices": [
                        "A. Only at night",
                        "B. Only in fog",
                        "C. At all times",
                        "D. Only when the ship signals"
                    ],
                    "answer": "C. At all times"
                }
            ]
        }
        
        self.vessel_types = [
            "Combat Support Boat",
            "Army Work Boat",
            "Small Boat",
            "Large Ship"
        ]

    def generate_question(self) -> Dict:
        """Generate a single random question from the templates."""
        category = random.choice(list(self.question_templates.keys()))
        template = random.choice(self.question_templates[category])
        
        question = {
            "type": template["type"],
            "difficulty": template["difficulty"],
            "question": template["template"].format(
                vessel=random.choice(self.vessel_types)
            ) if "{vessel}" in template["template"] else template["template"],
            "answer": template["answer"]
        }
        
        if "choices" in template:
            question["choices"] = template["choices"]
        if "image" in template:
            question["image"] = template["image"]
            
        return question

    def generate_quiz(self, num_questions: int = 20) -> List[Dict]:
        """Generate a complete quiz with the specified number of questions."""
        print("Starting quiz generation...")
        quiz = []
        used_questions = set()  # Track used questions to avoid duplicates
        
        while len(quiz) < num_questions:
            question = self.generate_question()
            # Create a unique identifier for the question
            question_id = f"{question['question']}_{question['answer']}"
            
            if question_id not in used_questions:
                quiz.append(question)
                used_questions.add(question_id)
                if len(quiz) % 5 == 0:  # Print progress every 5 questions
                    print(f"Generated {len(quiz)} questions...")
        
        print(f"Quiz generation complete. Total questions: {len(quiz)}")
        random.shuffle(quiz)
        return quiz

    def save_quiz(self, quiz: List[Dict], filename: str = "irpcs_quiz.json"):
        """Save the generated quiz to a JSON file."""
        print(f"Saving quiz to {filename}...")
        with open(filename, 'w') as f:
            json.dump(quiz, f, indent=2)
        print("Quiz saved successfully!")

def main():
    print("Starting main function...")
    try:
        print("Creating quiz generator...")
        generator = IRPCSQuizGenerator()
        print("Generating quiz...")
        quiz = generator.generate_quiz(num_questions=20)
        print("Saving quiz...")
        generator.save_quiz(quiz)
        print("Process complete!")
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    print("Script started")
    main()
    print("Script finished") 