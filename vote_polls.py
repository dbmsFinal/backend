from ORM import app, db, User, Poll, Question, Options, Comment, Vote
from flask import jsonify, request
from flask_login import login_required, current_user
@app.route('/polls/<int:poll_id>/vote', methods=['POST'])
@login_required
def vote_poll(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error": "Poll not found."}), 404

    # Check if the poll is ongoing
    if poll.start_date > db.func.current_date() or poll.end_date < db.func.current_date():
        return jsonify({"error": "The poll is not ongoing."}), 400

    # Get the selected options for each question
    data = request.get_json()
    answers = data.get("answers")
    if not answers:
        return jsonify({"error": "No answers provided."}), 400

    # Vote in the poll by saving the user's selected options
    for answer in answers:
        question_id = answer.get("question_id")
        option_text = answer.get("option_text")

        if not question_id or option_text is None:
            return jsonify({"error": "Invalid answer format."}), 400

        # Check if the question and options exist
        question = Question.query.get(question_id)

        if not question:
            return jsonify({"error": "Question not found."}), 404

        # Find the matching options based on the question ID
        options = Options.query.filter_by(poll_id=poll_id, question_id=question_id).all()

        if not options:
            return jsonify({"error": "Options not found."}), 404

        # Find the selected option by comparing the option_text with the text field of options
        selected_option = next((option for option in options if str(option.text) == option_text), None)

        if not selected_option:
            return jsonify({"error": "Selected option not found."}), 404

        # Save the user's vote
        vote = Vote(user_id=current_user.user_id, poll_id=poll_id, question_id=question_id, option_id=selected_option.option_id)
        db.session.add(vote)

    db.session.commit()

    return jsonify({"message": "Vote recorded successfully."}), 200
