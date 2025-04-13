import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import traceback
from tqdm import tqdm

from src.models.user import UserProfile
from src.modules.preprocessor.preprocessor import QueryPreprocessor
from src.services.embedding_service import EmbeddingService

def process_all_users():
    """Batch process all users to generate and store embeddings"""
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        processed_count = 0
        error_count = 0
        
        # Load all products
        users = UserProfile.get_all()
        print(f"Loaded {len(users)} users for processing")
        
        # Create progress bar
        with tqdm(total=len(users), desc="Processing users") as pbar:
            for user in users:
                try:
                    # Skip products with existing embeddings
                    if user.embedding:
                        pbar.update(1)
                        continue
                    
                    # Prepare text components with structured formatting
                    text_components = [
                        user.preferences.favorite_brands,
                        user.preferences.interests
                    ]
                    
                    # Clean and combine text
                    clean_text = " ".join(
                        QueryPreprocessor.normalize_tokenize(str(part))
                        for part in text_components
                        if part is not None
                    )
                    
                    # Generate and store embedding
                    if clean_text.strip():
                        embedding = embedding_service.embed_sentences([clean_text])[0]
                        user.update_embedding(embedding)
                        processed_count += 1
                    else:
                        print(f"\nWarning: Empty text for user {user.id}")
                    
                    pbar.update(1)
                    
                except Exception as e:
                    error_count += 1
                    print(f"\nError processing {user.id}: {str(e)}")
                    traceback.print_exc()
                    continue

        # Print final report
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed to process: {error_count}")
        print(f"Skipped (existing embeddings): {len(users) - processed_count - error_count}")

    except Exception as e:
        print(f"Fatal error in processing pipeline: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    process_all_users()