from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_required, current_user
from werkzeug.urls import url_parse
from app import db
from app.main import bp
from app.models import Direction, Reference
from app.main.forms import DirectionForm, ChatMessageForm
from app.services.chat_service import create_chat_service
import logging
import json

logger = logging.getLogger('counsel_windsurf.main.routes')
growth_chat_service = create_chat_service("growth")  # Initialize the growth direction chat service
reference_chat_service = create_chat_service("idols")  # Initialize the reference chat service

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
            response, is_complete, full_response, short_summary = growth_chat_service.chat(user_message, messages)
            
            # Add AI response to history
            messages.append({"role": "assistant", "content": response})
            session['conversation_history'] = json.dumps(messages)
            
            if is_complete:
                # Store the direction data in session for confirmation
                session['pending_direction'] = {
                    'summary': response,
                    'raw_response': full_response,
                    'short_summary': short_summary
                }
                return render_template('chat_direction.html',
                                    title='New Growth Direction',
                                    form=form,
                                    conversation_history=messages,
                                    is_complete=True,
                                    direction_summary=response,
                                    raw_response=full_response,
                                    short_summary=short_summary)
            
            # Continue conversation
            return redirect(url_for('main.create_direction'))
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            flash('Error processing chat message. Please try again.', 'error')
            return redirect(url_for('main.create_direction'))
    
    # Load conversation history for template
    try:
        messages = json.loads(conversation_history)
        # Check if there's a pending direction to confirm
        pending = session.get('pending_direction')
        if pending:
            return render_template('chat_direction.html',
                                title='New Growth Direction',
                                form=form,
                                conversation_history=messages,
                                is_complete=True,
                                direction_summary=pending['summary'],
                                raw_response=pending['raw_response'],
                                short_summary=pending['short_summary'])
    except (json.JSONDecodeError, TypeError):
        logger.error("Invalid conversation history in session, resetting")
        messages = []
        session['conversation_history'] = '[]'
    
    return render_template('chat_direction.html', 
                         title='New Growth Direction',
                         form=form,
                         conversation_history=messages)

@bp.route('/confirm_direction', methods=['POST'])
@login_required
def confirm_direction():
    if 'pending_direction' not in session:
        flash('No pending direction to confirm.')
        return redirect(url_for('main.create_direction'))
    
    pending = session['pending_direction']
    direction = Direction(
        title=pending.get('short_summary', 'Growth Direction'),
        description=pending['summary'],
        raw_response=pending['raw_response'],
        author=current_user
    )
        
    logger.info(f"Creating confirmed direction with title: {direction.title}")
    db.session.add(direction)
    db.session.commit()
    logger.info(f"Direction saved to database with id: {direction.id}")
        
    # Clear conversation history and pending direction
    session.pop('conversation_history', None)
    session.pop('pending_direction', None)
        
    flash('Your growth direction has been recorded!')
    return redirect(url_for('main.index'))
        
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

@bp.route('/create_reference', methods=['GET', 'POST'])
@login_required
def create_reference():
    logger.debug("Accessing create reference page")
    form = ChatMessageForm()
    
    # Get conversation history
    conversation_history = session.get('reference_conversation_history', '[]')
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
            
            # Get AI response using the reference chat service
            response, is_complete, full_response, short_summary = reference_chat_service.chat(user_message, messages)
            
            # Add AI response to history
            messages.append({"role": "assistant", "content": response})
            session['reference_conversation_history'] = json.dumps(messages)
            
            if is_complete:
                # Store the reference data in session for confirmation
                session['pending_reference'] = {
                    'summary': response,
                    'raw_response': full_response,
                    'short_summary': short_summary
                }
                return render_template('chat_reference.html',
                                    title='New Reference',
                                    form=form,
                                    conversation_history=messages,
                                    is_complete=True,
                                    reference_summary=response,
                                    raw_response=full_response,
                                    short_summary=short_summary)
            
            # Continue conversation
            return redirect(url_for('main.create_reference'))
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
            flash('Error processing chat message. Please try again.', 'error')
            return redirect(url_for('main.create_reference'))
    
    # Load conversation history for template
    try:
        messages = json.loads(conversation_history)
        # Check if there's a pending reference to confirm
        pending = session.get('pending_reference')
        if pending:
            return render_template('chat_reference.html',
                                title='New Reference',
                                form=form,
                                conversation_history=messages,
                                is_complete=True,
                                reference_summary=pending['summary'],
                                raw_response=pending['raw_response'],
                                short_summary=pending['short_summary'])
    except (json.JSONDecodeError, TypeError):
        logger.error("Invalid conversation history in session, resetting")
        messages = []
        session['reference_conversation_history'] = '[]'
    
    return render_template('chat_reference.html', 
                         title='New Reference',
                         form=form,
                         conversation_history=messages)

@bp.route('/reset_reference_conversation', methods=['POST'])
@login_required
def reset_reference_conversation():
    session['reference_conversation_history'] = '[]'
    if 'pending_reference' in session:
        del session['pending_reference']
    return redirect(url_for('main.create_reference'))

@bp.route('/confirm_reference', methods=['POST'])
@login_required
def confirm_reference():
    if 'pending_reference' not in session:
        flash('No pending reference to save.', 'error')
        return redirect(url_for('main.create_reference'))
        
    try:
        pending = session['pending_reference']
        reference = Reference(
            title=pending['short_summary'],
            description=pending['summary'],
            raw_response=pending['raw_response'],
            author=current_user
        )
        db.session.add(reference)
        db.session.commit()
        
        # Clear session data
        del session['pending_reference']
        session['reference_conversation_history'] = '[]'
        
        flash('Your reference has been saved!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        logger.error(f"Error saving reference: {str(e)}", exc_info=True)
        flash('Error saving reference. Please try again.', 'error')
        return redirect(url_for('main.create_reference'))

@bp.route('/reference/<int:id>')
@login_required
def reference(id):
    reference = Reference.query.get_or_404(id)
    return render_template('reference.html', title=reference.title, reference=reference)

@bp.route('/delete_reference/<int:id>', methods=['POST'])
@login_required
def delete_reference(id):
    reference = Reference.query.get_or_404(id)
    if reference.author != current_user:
        flash('You cannot delete this reference.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        db.session.delete(reference)
        db.session.commit()
        flash('Reference deleted.', 'success')
    except Exception as e:
        logger.error(f"Error deleting reference: {str(e)}", exc_info=True)
        flash('Error deleting reference.', 'error')
        
    return redirect(url_for('main.index'))
