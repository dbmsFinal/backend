from ORM import app, db, User, Poll, Question, Options, Comment, Vote
from flask import jsonify

@app.route('/polls/ongoing')
def view_ongoing_polls():
    ongoing_polls = Poll.query.filter(Poll.start_date <= db.func.current_date(), Poll.end_date >= db.func.current_date()).all()

    if len(ongoing_polls) == 0:
        return jsonify({"error" : "No ongoing polls available."}), 404

    response = {
        'ongoing_polls': [poll_to_dict(poll) for poll in ongoing_polls]
    }

    return jsonify({"message" : response}), 200


@app.route('/polls/completed')
def view_completed_polls():
    completed_polls = Poll.query.filter(Poll.end_date < db.func.current_date()).all()

    if len(completed_polls) == 0:
        return jsonify({"error" : "No completed polls available."}), 404

    response = {
        'completed_polls': [poll_to_dict(poll) for poll in completed_polls]
    }

    return jsonify({"message" : response}), 200

@app.route('/polls')
def view_all_polls():
    ongoing_polls = Poll.query.filter(Poll.start_date <= db.func.current_date(), Poll.end_date >= db.func.current_date()).all()
    completed_polls = Poll.query.filter(Poll.end_date < db.func.current_date()).all()

    response = {}

    if len(ongoing_polls) > 0:
        response['ongoing_polls'] = [poll_to_dict(poll) for poll in ongoing_polls]

    if len(completed_polls) > 0:
        response['completed_polls'] = [poll_to_dict(poll) for poll in completed_polls]

    if len(response) == 0:
        return jsonify({"error" : "No polls available."}), 404

    return jsonify({"message" : response}), 200

@app.route('/polls/<path:poll_id>', methods=['GET'])
def get_poll(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error" : "Poll not found."}), 404  # ??
    if poll is None:
        return jsonify({"error" : "Poll not found."}), 404

    creator = User.query.get(poll.creator_id)
    if creator is None:
        return jsonify({"error": "Poll creator not found."}), 400
    

    questions = Question.query.filter_by(poll_id=poll_id).all()
    poll_data = poll_to_dict(poll)
    poll_data['creator'] = {
        'user_id': creator.user_id,
        'username': creator.username,
        'email': creator.email
    }
    poll_data['questions'] = []

    for question in questions:
        options = Options.query.filter_by(poll_id=poll_id, question_id=question.question_id).all()
        question_data = {
            'question_id': question.question_id,
            'text': question.text,
            'options': [option.text for option in options]
        }
        poll_data['questions'].append(question_data)

    comments = Comment.query.filter_by(poll_id=poll_id).all()
    poll_data['comments'] = [{'comment_id': comment.comment_id, 'content': comment.content} for comment in comments]

    return jsonify({"message" : poll_data}), 200

def poll_to_dict(poll):
    return {
        'poll_id': poll.poll_id,
        'title': poll.title,
        'description': poll.description,
        'creator_id': poll.creator_id,
        'start_date': poll.start_date.strftime('%Y-%m-%d'),
        'end_date': poll.end_date.strftime('%Y-%m-%d'),
        'is_approved': poll.is_approved
    }

if __name__ == '__main__':
    app.run(debug = True)