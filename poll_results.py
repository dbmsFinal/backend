
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime
from ORM import Poll, Options, Vote, Question

app = Flask(__name__)
# 設定資料庫連線地址
DB_URI = 'mysql+pymysql://bochiao:qwerty@140.112.211.104:3306/DBFINAL'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# 是否追蹤資料庫修改，一般不開啟，會影響效能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 是否顯示底層執行的 SQL 語句
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

manager = LoginManager()
manager.init_app(app)

@app.route('/poll_results/<int:poll_id>', methods=['GET'])
def getPollResult(poll_id):
    poll = db.session.get(Poll, poll_id)

    if not poll :
        return jsonify({'message': 'Poll-{:d} does not exist.'.format(poll_id)}), 400
    if not poll.is_approved :
        return jsonify({'message': 'Poll-{:d} has not been approved yet.'.format(poll_id)}), 400
    else:        
        if poll.start_date > datetime.now().date():
            return jsonify({'message': 'Poll-{:d} has not started yet.'.format(poll_id)}), 400
        if poll.end_date > datetime.now().date():
            return jsonify({'message': 'Poll-{:d} has not ended yet.'.format(poll_id)}), 400
    
    questions = Question.query.filter_by(poll_id=poll_id).all()
    results = []
    for question in questions:
        question_result = {
            'question_id': question.question_id,
            'options': []
        }
        options = Options.query.filter_by(poll_id=poll_id, question_id=question.question_id).all()
        total_cnt = Vote.query.filter_by(poll_id=poll, question_id=question.question_id).count()
        for option in options:
            vote_cnt = option.vote_count
            if total_cnt==0 :
                percentage = 0
            else:
                percentage = 100 * vote_cnt/total_cnt
            option_result = {
                'option_id': option.option_id,
                'percentage': percentage,
                'vote_cnt': vote_cnt
            }
            question_result['options'].append(option_result)
        results.append(question_result)
    
    return jsonify({'poll_id': poll_id, 'results': results}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # user = User(username='chang', email='a85948533@gmail.com', password='tt')
        # db.session.add(user)
        # poll = Poll(title='ended', description='Poll has ended.', creator_id=1, start_date=datetime.strptime('2020-3-3', '%Y-%m-%d'), end_date=datetime.strptime('2021-4-23', '%Y-%m-%d'))
        # db.session.add(poll)
        # q = Question(poll_id=11, question_id=1, text='test')
        # qq = Question(poll_id=11, question_id=2, text='testtest')
        # qqq = Question(poll_id=11, question_id=3, text='testtesttest')
        # db.session.add_all([q, qq, qqq])
        # for i in range(1, 4):
        #     option1 = Options(option_id=1, question_id=i, poll_id=11, text=True, vote_count=10)
        #     option2 = Options(option_id=2, question_id=i, poll_id=11, text=False, vote_count=6)
        #     db.session.add_all([option1, option2])
        # db.session.commit()

    app.run(debug=True)