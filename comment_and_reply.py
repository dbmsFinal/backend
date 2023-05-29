from ORM import app, db, Comment
from flask_login import login_required
from flask import jsonify, request

@app.route('/polls/<int:poll_id>/comments', methods=['GET'])
def view_comments(poll_id):
    comments = Comment.query.filter_by(poll_id=poll_id).all()
    comments_data = [{'comment_id': comment.comment_id, 'content': comment.content} for comment in comments]
    
    return jsonify({'data': comments_data}), 200

# Function to allow users to comment
@app.route('/polls/<int:poll_id>/comments/new', methods=['POST'])
#@login_required
def add_comment(poll_id):
    user_id = request.json.get('user_id')
    content = request.json.get('content')

    comment = Comment(user_id=user_id, content=content, poll_id=poll_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201

# Function to allow users to reply to a comment
@app.route('/polls/<int:poll_id>/comments/<int:comment_id>/replies', methods=['POST'])
#@login_required
def add_reply(poll_id, comment_id):
    user_id = request.json.get('user_id')
    content = request.json.get('content')

    parent_comment = Comment.query.get_or_404(comment_id)
    if parent_comment.poll_id != poll_id:
        return jsonify({'error': 'Comment not found for the given poll.'}), 404

    reply = Comment(user_id=user_id, content=content, poll_id=poll_id, parent_id=comment_id)
    db.session.add(reply)
    db.session.commit()

    return jsonify({'message': 'Reply added successfully'}), 201

if __name__ == '__main__':
    app.run(debug = True)