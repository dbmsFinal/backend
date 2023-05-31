from ORM import app, db, Poll, Question, Vote, Options
from flask import jsonify, request
from flask_login import login_required #, current_user
import datetime

'''
{
  "votes": [
    {
      "question_id": 1,
      "option_id": 2
    },
    {
      "question_id": 2,
      "option_id": 1
    }
  ]
}
'''
@app.route('/polls/<int:poll_id>/vote', methods=['POST'])
#@login_required
def vote(poll_id):
    try:
        poll = Poll.query.get_or_404(poll_id)
    except:
        return jsonify({"error" : "Poll not found."}), 404 
    
    
    # Check if the poll is currently active
    current_date = datetime.date.today()
    if current_date < poll.start_date or current_date > poll.end_date:
        return jsonify({'message': 'Poll is not active'}), 400
    
    #current_date = db.func.current_date()
    if not Poll.is_approved:
        return jsonify({'message': 'Poll is not approved'}), 400
    
    current_user = 1
    
    # Check if the user has already voted for this poll
    existing_vote = Vote.query.filter_by(user_id=current_user, poll_id=poll.poll_id).first()
    if existing_vote:
        return jsonify({'message': 'User has already voted for this poll'}), 400
    
    votes = request.json.get('votes')
    
    for vote in votes:
        question_id = vote['question_id']
        option_id = vote['option_id']
        
        try:
            question_id = Question.query.get_or_404(question_id)
        except:
            return jsonify({"error" : "Question not found."}), 404 
    
              
        # Create a new vote object
        new_vote = Vote(user_id=current_user, poll_id=poll.poll_id, question_id=question_id, option_id=option_id)
        db.session.add(new_vote)
        
        # Increment the vote count for the selected option
        selected_option = Options.query.get((option_id, poll.poll_id, question_id))
        if selected_option:
                selected_option.vote_count += 1
    
    db.session.commit()
    
    return jsonify({'message': 'Vote recorded successfully'}), 200

if __name__ == '__main__':
    app.run(debug = True)