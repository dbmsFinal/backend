from ORM import app, db, Poll, Question, Vote
from flask import jsonify, request, Blueprint
from flask_login import login_required, current_user
import datetime


bp = Blueprint('vote_polls', __name__)
# Vote to every question of the poll


@bp.route('/polls/<path:poll_id>/vote', methods=['POST'])
@login_required
def vote(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error": "Poll not found."}), 404

    # Check if the poll is currently active
    current_date = datetime.date.today()
    if current_date < poll.start_date or current_date > poll.end_date:
        return jsonify({'error': 'Poll is not active'}), 400

    if not Poll.is_approved:
        return jsonify({'error': 'Poll is not approved'}), 400

    # Check if the user has already voted for this poll
    existing_vote = Vote.query.filter_by(
        user_id=current_user.user_id, poll_id=poll.poll_id).first()
    if existing_vote:
        return jsonify({'error': 'User has already voted for this poll'}), 400

    votes = request.json.get('votes')

    if len(votes) == 2:
        # Check if the user has voted for every question of the poll
        question_ids = {vote['question_id'] for vote in votes}
        poll_question_ids = {question.question_id for question in Question.query.filter_by(
            poll_id=poll.poll_id).all()}
        if question_ids != poll_question_ids:
            return jsonify({'error': 'Please vote for every question of the poll'}), 400

    for vote in votes:
        question_id = vote['question_id']
        option_id = vote['option_id']

        # Create a new vote object
        new_vote = Vote(user_id=current_user.user_id, poll_id=poll.poll_id,
                        question_id=question_id, option=option_id)
        db.session.add(new_vote)

        # Increment the vote count for the selected option
        question_voted = Question.query.get(
            (poll.poll_id, question_id))
        if question_voted:
            if option_id == 1:
                question_voted.count_support += 1 
            else:
                question_voted.count_oppose += 1

    db.session.commit()

    return jsonify({'message': 'Vote recorded successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
