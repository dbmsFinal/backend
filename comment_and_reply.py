from ORM import app, db, Comment, Poll
from flask_login import login_required, current_user
from flask import jsonify, request

@app.route('/polls/<path:poll_id>/comments', methods=['GET'])
def view_comments(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error" : "Poll not found."}), 404 
    comments = Comment.query.filter_by(poll_id=poll.poll_id).all()
    comments_data = [{'comment_id': comment.comment_id, 'content': comment.content} for comment in comments]
    if len(comments_data) == 0:
        return jsonify({"message": "There are no comments on this poll."}), 200

    return jsonify({'data': comments_data}), 200

# Function to allow users to comment
@app.route('/polls/<path:poll_id>/comments/new', methods=['POST'])
@login_required
def add_comment(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error" : "Poll not found."}), 404 
    
    content = request.json.get('content')
    
    if not content or content.strip() == "":
        return jsonify({"error": "Comment cannot be empty"}), 400

    comment = Comment(user_id=current_user.user_id, content=content, poll_id=poll.poll_id)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201

# Function to allow users to reply to a comment
@app.route('/polls/<int:poll_id>/comments/<int:comment_id>/replies', methods=['POST'])
@login_required
def add_reply(poll_id, comment_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error" : "Poll not found."}), 404 
    
    try:
        parent = Comment.query.get_or_404(comment_id)
    except:
        return jsonify({"error" : "Parent comment not found."}), 404 
    
    content = request.json.get('content')

    reply = Comment(user_id=current_user.user_id, content=content, poll_id=poll.poll_id, parent_id=parent.comment_id)
    db.session.add(reply)
    db.session.commit()

    return jsonify({'message': 'Reply added successfully'}), 201

if __name__ == '__main__':
    app.run(debug = True)