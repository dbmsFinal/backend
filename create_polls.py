from ORM import app, db, Poll, Question, Options
from datetime import datetime
from flask import request, jsonify
from flask_login import login_required, current_user

@app.route('/create_poll', methods=['POST'])
@login_required
def create_poll():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    questions = data.get('questions')

    # 確認每個欄位是否都有輸入值
    if not title or not description or not start_date or not end_date:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD."}), 400

    if start_date > end_date:
        return jsonify({"error": "Start date cannot be later than end date."}), 400
    
    poll = Poll.query.filter_by(title=title).first()
    if poll:
        return jsonify({"error": "The Poll already exists."}), 400

    new_poll = Poll(title=title, description=description, start_date=start_date, end_date=end_date, creator_id=current_user.user_id)
    db.session.add(new_poll)
    db.session.flush()

    if questions:
        # Create new questions for the poll
        for question in questions:
            max_question = Question.query.filter_by(poll_id=new_poll.poll_id).order_by(Question.question_id.desc()).first()
            if max_question is None:
                new_question_id = 1
            else:
                new_question_id = max_question.question_id + 1

            question_text = Question.query.filter_by(poll_id=new_poll.poll_id, text=question['text']).first()
            if question_text:
                return jsonify({"error": "The question already exists in the poll."}), 400

            new_question = Question(question_id=new_question_id, text=question['text'], poll_id=new_poll.poll_id)
            db.session.add(new_question)
            db.session.commit()

            for i in range(2): 
                new_option = Options(text=bool(i), poll_id=new_poll.poll_id, question_id=new_question.question_id, option_id=i+1)
                db.session.add(new_option)
                db.session.commit()
    else:
        db.session.commit()

    return jsonify({"message": "Poll created successfully", "poll_id": new_poll.poll_id}), 201

if __name__ == "__main__":
    app.run(debug=True)