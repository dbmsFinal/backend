from ORM import app, db, User, Poll, Question, Options, Comment, Vote
from flask import jsonify

'''
List all polls, categorizing them as ongoing or completed
'''
@app.route('/polls/')
def view_polls():
    ongoing_polls = Poll.query.filter(Poll.start_date <= db.func.current_date(), Poll.end_date >= db.func.current_date()).all()
    completed_polls = Poll.query.filter(Poll.end_date < db.func.current_date()).all()

    if len(ongoing_polls) == 0 and len(completed_polls) == 0:
        # No ongoing or completed polls available
        return jsonify(message="No polls available.")

    response = {}

    if len(ongoing_polls) == 0 and len(completed_polls) > 0:
        # No ongoing polls, but there are completed polls
        response['completed_polls'] = [poll_to_dict(poll) for poll in completed_polls]

    if len(ongoing_polls) > 0 and len(completed_polls) == 0:
        # Ongoing polls, but no completed polls
        response['ongoing_polls'] = [poll_to_dict(poll) for poll in ongoing_polls]

    if len(ongoing_polls) > 0 and len(completed_polls) > 0:
        # Both ongoing and completed polls available
        response['ongoing_polls'] = [poll_to_dict(poll) for poll in ongoing_polls]
        response['completed_polls'] = [poll_to_dict(poll) for poll in completed_polls]

    return jsonify(response)

'''
Display the Poll with poll_id.
'''
@app.route('/polls/<int:poll_id>', methods=['GET'])
def get_poll(poll_id):
    poll = Poll.query.get(poll_id)
    if poll is None:
        return jsonify(message="Poll not found.")

    creator = User.query.get(poll.creator_id)
    if creator is None:
        return jsonify(message="Poll creator not found.")

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

    return jsonify(poll_data)

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