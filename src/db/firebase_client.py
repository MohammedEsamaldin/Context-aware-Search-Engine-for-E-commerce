import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import firebase_admin
from firebase_admin import credentials, firestore
from config.config import FIREBASE_CREDENTIALS_PATH

## =========================================================================
#   Initialise Connection
## =========================================================================
# Initialise Firebase with credentials from the config and create Firestore instance
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client() 

# HELPER FUNCTION - Test the connection by listing available collections
def test_connection():
    try:
        collections = list(db.collections())
        print("Connected to Firestore successfully!")
        print("Collections found:", [col.id for col in collections])
    except Exception as e:
        print("Error connecting to Firestore:", e)
