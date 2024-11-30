import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Direction
from app.services.embedding_service import EmbeddingService

def update_all_embeddings():
    app = create_app()
    with app.app_context():
        embedding_service = EmbeddingService()
        directions = Direction.query.all()
        
        for direction in directions:
            if direction.embedding is None:
                print(f"Updating embedding for direction: {direction.title}")
                text_for_embedding = f"{direction.title} {direction.description}"
                embedding = embedding_service.create_embedding(text_for_embedding)
                if embedding is not None:
                    direction.set_embedding(embedding)
                    db.session.commit()
                    print("Embedding updated successfully")
                else:
                    print("Failed to create embedding")

if __name__ == '__main__':
    update_all_embeddings()
