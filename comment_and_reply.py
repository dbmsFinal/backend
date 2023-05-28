from ORM import app, db, User, Poll, Question, Options, Comment, Vote
from flask import request, jsonify
from flask_login import current_user
import re
from sqlalchemy.exc import SQLAlchemyError

'''
評論和討論：
用戶可以對公投發表評論，與其他用戶進行互動和討論。
用戶可以查看公投已發表的評論
'''
@app.route('/poll/<poll_id>/comments', methods=['GET', 'POST'])
def poll_comments(poll_id):
    poll = Poll.query.get(poll_id)

    if request.method == 'POST':
        content = request.form.get('comment')  # Assuming the comment is provided through a form field with the name 'comment'
        parent_id = request.form.get('parent_id')  # Assuming the parent comment ID is provided through a form field with the name 'parent_id'

        if parent_id:
            # Reply to an existing comment
            parent_comment = Comment.query.get(parent_id)
            if parent_comment:
                comment = Comment(poll_id=poll_id, content=content, parent=parent_comment)
                db.session.add(comment)
        else:
            # Comment to the poll
            comment = Comment(poll_id=poll_id, content=content)
            db.session.add(comment)

        db.session.commit()
        return "Comment submitted successfully"

    comments = Comment.query.filter_by(poll_id=poll_id).all()
    
    return jsonify({
        'poll': {
            'poll_id': poll.poll_id,
            # Include other relevant attributes of the poll
        },
        'comments': [
            {
                'comment_id': comment.comment_id,
                'user_id': comment.user_id,
                'content': comment.content,
                # Include other relevant attributes of the comment
            }
            for comment in comments
        ]
    })
if __name__ == '__main__':
    app.run(debug = True)