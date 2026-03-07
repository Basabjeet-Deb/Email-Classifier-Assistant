"""
Retrain email classification model using combined datasets.
Run this script to retrain the model with latest data.
"""
from backend.models.tfidf_classifier import get_tfidf_classifier

def main():
    """Retrain the TF-IDF classifier."""
    print("\n" + "="*80)
    print("RETRAINING EMAIL CLASSIFICATION MODEL")
    print("="*80)
    
    classifier = get_tfidf_classifier()
    success = classifier.train_model()
    
    if success:
        print("\n✓ Model retrained successfully!")
        print("  The new model is now active and ready to use.")
    else:
        print("\n✗ Model retraining failed!")
        print("  Please check the error messages above.")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
