from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.models import Direction
from app.main.forms import DirectionForm, EditDirectionForm
from app.services.embedding_service import EmbeddingService
import logging

logger = logging.getLogger('counsel_windsurf.main.routes')
embedding_service = EmbeddingService()

@bp.route('/')
@bp.route('/index')
def index():
    logger.debug("Accessing index page")
    if current_user.is_authenticated:
        directions = Direction.query.filter_by(author=current_user).order_by(Direction.timestamp.desc()).all()
        logger.info(f"Retrieved {len(directions)} directions for user {current_user.username}")
    else:
        directions = []
        logger.info("No user authenticated, showing empty directions list")
    return render_template('index.html', title='Home', directions=directions)

@bp.route('/create_direction', methods=['GET', 'POST'])
@login_required
def create_direction():
    logger.debug("Accessing create direction page")
    form = DirectionForm()
    if form.validate_on_submit():
        logger.info(f"Creating new direction with title: {form.title.data}")
        direction = Direction(title=form.title.data,
                            description=form.description.data,
                            author=current_user)
        
        # Create embedding from title and description
        text_for_embedding = f"{form.title.data} {form.description.data}"
        logger.debug("Generating embedding for new direction")
        embedding, raw_response = embedding_service.create_embedding(text_for_embedding)
        if embedding is not None:
            direction.set_embedding(embedding, raw_response)
            logger.info("Embedding and raw response stored successfully")
        else:
            logger.warning("Failed to generate embedding for direction")
        
        db.session.add(direction)
        db.session.commit()
        logger.info(f"Direction {direction.id} created successfully")
        flash('Your direction has been created!')
        return redirect(url_for('main.index'))
    return render_template('create_direction.html', title='Create Direction',
                         form=form)

@bp.route('/direction/<int:id>')
@login_required
def direction(id):
    logger.debug(f"Accessing direction page for id: {id}")
    direction = Direction.query.get_or_404(id)
    if direction.author != current_user:
        flash('You do not have permission to view this direction.', 'error')
        return redirect(url_for('main.index'))
    logger.info(f"Retrieved direction: {direction.title}")
    return render_template('direction.html', title=direction.title, direction=direction)

@bp.route('/delete_direction/<int:id>', methods=['POST'])
@login_required
def delete_direction(id):
    direction = Direction.query.get_or_404(id)
    if direction.author != current_user:
        flash('You cannot delete this direction.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        db.session.delete(direction)
        db.session.commit()
        flash('Direction has been deleted.', 'success')
    except Exception as e:
        logger.error(f"Error deleting direction: {str(e)}")
        flash('Error deleting direction.', 'error')
        db.session.rollback()
    
    return redirect(url_for('main.index'))

@bp.route('/edit_direction/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_direction(id):
    direction = Direction.query.get_or_404(id)
    if direction.author != current_user:
        flash('You cannot edit this direction.', 'error')
        return redirect(url_for('main.index'))
    
    form = EditDirectionForm()
    if form.validate_on_submit():
        content_changed = direction.description != form.description.data
        
        direction.title = form.title.data
        direction.description = form.description.data
        
        if content_changed:
            # Update embedding and raw_response only if content changed
            text_for_embedding = f"{direction.title} {direction.description}"
            logger.debug("Generating new embedding for updated direction")
            embedding, raw_response = embedding_service.create_embedding(text_for_embedding)
            if embedding is not None:
                direction.set_embedding(embedding, raw_response)
                logger.info("New embedding and raw response stored successfully")
            else:
                logger.warning("Failed to generate new embedding for direction")
        
        try:
            db.session.commit()
            flash('Your direction has been updated!', 'success')
            return redirect(url_for('main.direction', id=direction.id))
        except Exception as e:
            logger.error(f"Error updating direction: {str(e)}")
            flash('Error updating direction.', 'error')
            db.session.rollback()
    
    elif request.method == 'GET':
        form.title.data = direction.title
        form.description.data = direction.description
    
    return render_template('edit_direction.html', title='Edit Direction',
                         form=form, direction=direction)

@bp.route('/search_similar/<int:direction_id>')
@login_required
def search_similar(direction_id):
    logger.debug(f"Searching for similar directions to id: {direction_id}")
    direction = Direction.query.get_or_404(direction_id)
    
    if direction.author != current_user:
        return jsonify([])
    
    if direction.embedding is None:
        logger.warning(f"Direction {direction_id} has no embedding")
        return jsonify([])

    # Get all directions except the current one, but only for the current user
    other_directions = Direction.query.filter(
        Direction.id != direction_id,
        Direction.author == current_user,
        Direction.embedding.isnot(None)
    ).all()
    
    similar_directions = []
    
    logger.debug(f"Computing similarities with {len(other_directions)} directions")
    for other_direction in other_directions:
        target_embedding = other_direction.get_embedding()
        if target_embedding is not None:
            similarity = embedding_service.compute_similarity(direction.get_embedding(), target_embedding)
            similar_directions.append({
                'id': other_direction.id,
                'title': other_direction.title,
                'similarity': float(similarity)
            })
    
    # Sort by similarity score in descending order
    similar_directions.sort(key=lambda x: x['similarity'], reverse=True)
    top_similar = similar_directions[:5]
    logger.info(f"Found {len(top_similar)} similar directions")
    return jsonify(top_similar)
