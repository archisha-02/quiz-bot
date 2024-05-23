
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if not current_question_id:
        return True, ""  # No question to record

    question = next((q for q in PYTHON_QUESTION_LIST if q["id"] == current_question_id), None)
    if not question:
        return False, "Invalid question ID."

    correct = answer.strip().lower() == question["answer"].strip().lower()
    
    if correct:
        session["correct_answers"] = session.get("correct_answers", 0) + 1
    else:
        session["wrong_answers"] = session.get("wrong_answers", 0) + 1

    if "answers" not in session:
        session["answers"] = []
    session["answers"].append({
        "question_id": current_question_id,
        "provided_answer": answer,
        "correct_answer": question["answer"],
        "correct": correct
    })
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_index is None or current_question_index < 0:
        next_question = PYTHON_QUESTION_LIST[0]
        return next_question["question"], 0  # Return the first question and its index
    elif current_question_index < len(PYTHON_QUESTION_LIST) - 1:
        next_question_index = current_question_index + 1
        next_question = PYTHON_QUESTION_LIST[next_question_index]
        return next_question["question"], next_question_index  # Return the next question and its index
    else:
        return "dummy question", -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    correct_answers = session.get("correct_answers", 0)
    total_questions = len(PYTHON_QUESTION_LIST)
    score_percentage = (correct_answers / total_questions) * 100

    if score_percentage >= 70:
        result_message = f"Congratulations! You scored {score_percentage}% in the quiz. Well done!"
    elif score_percentage >= 40:
        result_message = f"You scored {score_percentage}% in the quiz. Keep practicing to improve!"
    else:
        result_message = f"Oops! You scored {score_percentage}% in the quiz. Better luck next time!"

    return result_message if result_message else "dummy_result"
