from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.main import bp
from app.models import Direction
from app.main.forms import DirectionForm, ChatMessageForm
from app.services.chat_service import ChatService
import logging
import json

logger = logging.getLogger('counsel_windsurf.main.routes')
chat_service = ChatService()

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    directions = Direction.query.filter_by(author=current_user, is_latest=True).order_by(Direction.timestamp.desc()).all()
    return render_template('index.html', title='Home', directions=directions)

@bp.route('/create_direction', methods=['GET', 'POST'])
@login_required
def create_direction():
    logger.debug("Accessing create direction page")
    form = ChatMessageForm()
    
    # Get conversation history
    conversation_history = session.get('conversation_history', '[]')
    # If it's already a list, convert it to string
    if isinstance(conversation_history, list):
        conversation_history = json.dumps(conversation_history)
    
    if form.validate_on_submit():
        try:
            user_message = form.message.data
            # Parse the conversation history
            messages = json.loads(conversation_history)
            
            # Add user message to history
            messages.append({"role": "user", "content": user_message})
            
            # Get AI response
            response, is_complete, full_response = chat_service.chat(user_message, messages)
            
            # Add AI response to history
            messages.append({"role": "assistant", "content": response})
            session['conversation_history'] = json.dumps(messages)
            
            if is_complete:
                # Create direction with the summary (response is already cleaned in chat service)
                direction = Direction(
                    title=f"Growth Direction: {response[:50]}...",
                    description=response,
                    author=current_user,
                    raw_response=full_response
                )
                
                logger.info(f"Creating direction with title: {direction.title}")
                db.session.add(direction)
                db.session.commit()
                logger.info(f"Direction saved to database with id: {direction.id}")
                
                # Clear conversation history
                session.pop('conversation_history', None)
                
                flash('Your growth direction has been recorded!')
                return redirect(url_for('main.index'))
            
            # Continue conversation
            return redirect(url_for('main.create_direction'))
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            flash('Error processing chat message. Please try again.', 'error')
            return redirect(url_for('main.create_direction'))
    
    # Load conversation history for template
    try:
        messages = json.loads(conversation_history)
    except (json.JSONDecodeError, TypeError):
        logger.error("Invalid conversation history in session, resetting")
        messages = []
        session['conversation_history'] = '[]'
    
    return render_template('chat_direction.html', 
                         title='New Growth Direction',
                         form=form,
                         conversation_history=messages)

@bp.route('/direction/<int:id>')
@login_required
def direction(id):
    direction = Direction.query.get_or_404(id)
    if direction.author != current_user:
        flash('You do not have permission to view this direction.')
        return redirect(url_for('main.index'))
    return render_template('direction.html', title='View Direction', direction=direction)

@bp.route('/delete_direction/<int:id>')
@login_required
def delete_direction(id):
    direction = Direction.query.get_or_404(id)
    if direction.author != current_user:
        flash('You do not have permission to delete this direction.')
        return redirect(url_for('main.index'))
    
    db.session.delete(direction)
    db.session.commit()
    flash('Direction deleted.')
    return redirect(url_for('main.index'))

@bp.route('/edit_direction/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_direction(id):
    direction = Direction.query.get_or_404(id)
    if direction.author != current_user:
        flash('You do not have permission to edit this direction.')
        return redirect(url_for('main.index'))
    
    form = DirectionForm()
    if form.validate_on_submit():
        try:
            # Create new version
            new_direction = Direction(
                title=form.title.data,
                description=form.description.data,
                author=current_user,
                original_id=direction.original_id or direction.id,
                version=direction.version + 1,
                raw_response=direction.raw_response
            )
            
            # Mark old version as not latest
            direction.is_latest = False
            
            db.session.add(new_direction)
            db.session.commit()
            
            flash('Your changes have been saved.')
            return redirect(url_for('main.direction', id=new_direction.id))
            
        except Exception as e:
            logger.error(f"Error saving direction changes: {str(e)}")
            flash('Error saving changes.', 'error')
            db.session.rollback()
    
    elif request.method == 'GET':
        form.title.data = direction.title
        form.description.data = direction.description
    
    return render_template('edit_direction.html', 
                         title='Edit Direction',
                         form=form,
                         direction=direction)

@bp.route('/reset_conversation', methods=['POST'])
@login_required
def reset_conversation():
    logger.info("Resetting conversation history")
    session.pop('conversation_history', None)
    flash('Conversation has been reset. You can start a new direction.')
    return redirect(url_for('main.create_direction'))
