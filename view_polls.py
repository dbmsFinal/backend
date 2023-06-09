from ORM import app, db, User, Poll, Question, Comment, login_manager
from flask import jsonify, Blueprint
from flask_login import login_required, current_user
bp = Blueprint('view_polls', __name__)

# View ongoning polls


@bp.route('/polls/ongoing')
@login_required
def view_ongoing_polls():
    ongoing_polls = Poll.query.filter(Poll.start_date <= db.func.current_date(
    ), Poll.end_date >= db.func.current_date(), Poll.is_approved == 1).all()

    if len(ongoing_polls) == 0:
        return jsonify({"message": "No ongoing polls available."}), 204

    response = {
        'ongoing_polls': [poll_to_dict(poll) for poll in ongoing_polls]
    }

    return jsonify({"message": response}), 200

# View completed polls


@bp.route('/polls/completed')
@login_required
def view_completed_polls():
    completed_polls = Poll.query.filter(
        Poll.end_date < db.func.current_date(), Poll.is_approved == 1).all()

    if len(completed_polls) == 0:
        return jsonify({"message": "No completed polls available."}), 204

    response = {
        'completed_polls': [poll_to_dict(poll) for poll in completed_polls]
    }

    return jsonify({"message": response}), 200

# View all polls


@bp.route('/polls/unapproved')
@login_required
def view_unapproved_polls():

    if current_user.email != 'admin@nccu.edu.tw':
        return jsonify({"error": "You are not admin."}), 401
    ongoing_polls = Poll.query.filter(Poll.start_date <= db.func.current_date(
    ), Poll.end_date >= db.func.current_date(), Poll.is_approved == 0).all()

    response = {}
    if len(ongoing_polls) > 0:
        response['ongoing_polls'] = [
            poll_to_dict(poll) for poll in ongoing_polls]
    if len(response) == 0:
        return jsonify({"error": "No polls available."}), 404

    return jsonify({"message": response}), 200


@bp.route('/polls')
@login_required
def view_all_polls():
    ongoing_polls = Poll.query.filter(Poll.start_date <= db.func.current_date(
    ), Poll.end_date >= db.func.current_date()).all()
    completed_polls = Poll.query.filter(
        Poll.end_date < db.func.current_date()).all()

    response = {}

    if len(ongoing_polls) > 0:
        response['ongoing_polls'] = [
            poll_to_dict(poll) for poll in ongoing_polls]

    if len(completed_polls) > 0:
        response['completed_polls'] = [
            poll_to_dict(poll) for poll in completed_polls]

    if len(response) == 0:
        return jsonify({"error": "No polls available."}), 404

    return jsonify({"message": response}), 200

# View specific poll


@bp.route('/polls/<path:poll_id>', methods=['GET'])
@login_required
def get_poll(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error": "Poll not found."}), 404

    creator = User.query.get(poll.creator_id)
    if creator is None:
        return jsonify({"error": "Poll creator not found."}),    404

    questions = Question.query.filter_by(poll_id=poll_id).all()
    poll_data = poll_to_dict(poll)
    poll_data['creator'] = {
        'user_id': creator.user_id,
        'username': creator.username,
        'email': creator.email
    }
    poll_data['questions'] = []

    for question in questions:
        question_data = {
            'question_id': question.question_id,
            'text': question.text
        }
        poll_data['questions'].append(question_data)
    # sort by question_id and inplace
    poll_data['questions'].sort(key=lambda x: x['question_id'])
    print(poll_data['questions'])
    comments = Comment.query.filter_by(poll_id=poll_id).all()
    poll_data['comments'] = [{'comment_id': comment.comment_id,
                              'content': comment.content} for comment in comments]

    return jsonify({"message": poll_data}), 200


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


if __name__ == '__main__':
    app.run(debug=True)
