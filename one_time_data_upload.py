import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
from pathlib import Path
from tqdm import tqdm
from google.cloud.firestore import Client
from src.db.firebase_client import db  # Make sure Firebase is initialized here
from src.models.product import Product

def upload_products(json_path: Path, batch_size: int = 500):
    # Load products from JSON
    with open(json_path, "r") as f:
        products_data = json.load(f)

    # Initialize Firestore client
    firestore_client: Client = db
    products_ref = firestore_client.collection("Products")
    
    batch = firestore_client.batch()
    processed = 0
    total = len(products_data)
    failed_uploads = []

    with tqdm(total=total, desc="Uploading products") as pbar:
        for idx, entry in enumerate(products_data):
            try:
                # Directly create Product instance from JSON entry
                product = Product(**entry)
                
                # Prepare Firestore data WITH ALIASES
                firestore_data = product.dict(by_alias=False)
                
                # Use product.id (class field) as document ID
                doc_ref = products_ref.document(product.id)
                batch.set(doc_ref, firestore_data)
                processed += 1

                if processed % batch_size == 0:
                    batch.commit()
                    batch = firestore_client.batch()

            except Exception as e:
                failed_uploads.append({
                    "index": idx,
                    "error": str(e),
                    "data": entry
                })
            
            pbar.update(1)

        if processed % batch_size != 0:
            batch.commit()

    print(f"Successfully uploaded {processed}/{total}")
    if failed_uploads:
        print("\nFailed entries:")
        for error in failed_uploads:
            print(f"Index {error['index']}: {error['error']}")
            print(f"Data: {error['data']}\n")

if __name__ == "__main__":
    # Path to your products JSON file
    products_json = Path("data/processed/products.json")  # Update this path
    
    # Run the upload
    upload_products(products_json)