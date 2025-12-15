# --- Quiz Configuration ---
GAME_STATE = "walking" # Options: "walking", "quiz", "success"
current_quiz = None    # Will hold the data of the active quiz
user_text = ""         # What the player is typing
completed_quizzes = [] # List of quiz IDs the player has already finished
collected_numbers = [] # The rewards

# The Dictionary of Questions (Keys must match Tiled properties!)
QUIZ_DATA = {
    "math_1": {
        "question": "5 * 5 + 2?",
        "answer": "27",
        "reward": "4"
    },
    "prog_1": {
        "question": "Python function keyword?",
        "answer": "def",
        "reward": "9"
    },
    # Add more here matching your Tiled properties...
}

# Font for the popup
font = pygame.font.Font(None, 40)