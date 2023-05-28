from ORM import app, db, Poll, Question, Options
from flask import request, jsonify
from flask_login import login_required, current_user

@app.route('/add_question/<int:poll_id>', methods=['POST'])
@login_required
def add_question(poll_id):
    poll = Poll.query.filter_by(poll_id=poll_id, creator_id=current_user.user_id, is_approved=False).first()
    if poll:
        data = request.get_json()
        questions = data.get("questions")
        if questions:
            for question in questions:
                max_question = Question.query.filter_by(poll_id=poll.poll_id).order_by(Question.question_id.desc()).first()
                if max_question is None:
                    new_question_id = 1
                else:
                    new_question_id = max_question.question_id + 1

                question_text = Question.query.filter_by(poll_id=poll.poll_id, text=question['text']).first()
                if question_text:
                    return jsonify({"error": "The question already exists in the poll."}), 400

                new_question = Question(question_id=new_question_id, text=question['text'], poll_id=poll.poll_id)
                db.session.add(new_question)
                db.session.commit()

                for i in range(2): 
                    new_option = Options(text=bool(i), poll_id=poll.poll_id, question_id=new_question.question_id, option_id=i+1)
                    db.session.add(new_option)
                    db.session.commit()
            return jsonify({"message": "Question added successfully"}), 201
        return jsonify({"error": "No question provided"}), 400
    else:
        return jsonify({"error": "Poll not found or has been approved, cannot add question"}), 404
    
if __name__ == "__main__":
    app.run(debug=True)