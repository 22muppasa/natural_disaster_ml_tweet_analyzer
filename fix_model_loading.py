import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
import re

def preprocess_text(text):
    """Preprocess text for ML model"""
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove user mentions and hashtags
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def create_and_save_model():
    """Create and save the ML model with vectorizer"""
    print("Loading and preprocessing dataset...")
    
    # Load the dataset
    try:
        df = pd.read_csv('socialmedia-disaster-tweets-DFE.csv')
        print(f"Loaded dataset with {len(df)} tweets")
    except FileNotFoundError:
        print("Dataset file not found. Using sample data for model creation.")
        # Create sample data for demonstration
        sample_data = {
            'text': [
                'earthquake hits downtown area buildings collapsing',
                'fire spreading rapidly evacuation needed',
                'beautiful sunset tonight perfect weather',
                'flood warning issued water levels rising',
                'having lunch at restaurant',
                'tornado spotted emergency services responding',
                'great day for shopping',
                'hurricane approaching evacuations ordered',
                'traffic moving well today',
                'explosion reported emergency help needed'
            ],
            'choose_one': [
                'Relevant', 'Relevant', 'Not Relevant', 'Relevant', 'Not Relevant',
                'Relevant', 'Not Relevant', 'Relevant', 'Not Relevant', 'Relevant'
            ]
        }
        df = pd.DataFrame(sample_data)
    
    # Preprocess the data
    df['text_clean'] = df['text'].apply(preprocess_text)
    df['target'] = (df['choose_one'] == 'Relevant').astype(int)
    
    # Remove empty texts
    df = df[df['text_clean'].str.len() > 0]
    
    print(f"Preprocessed dataset: {len(df)} tweets")
    print(f"Disaster tweets: {df['target'].sum()}")
    print(f"Non-disaster tweets: {len(df) - df['target'].sum()}")
    
    # Split the data
    X = df['text_clean']
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create and fit TF-IDF vectorizer
    print("Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )
    
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    # Train the model
    print("Training logistic regression model...")
    model = LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight='balanced'
    )
    
    model.fit(X_train_vectorized, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_vectorized)
    f1 = f1_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"F1 Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model and vectorizer
    print("Saving model and vectorizer...")
    with open('disaster_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print("✅ Model and vectorizer saved successfully!")
    
    # Test the saved model
    print("\nTesting saved model...")
    with open('disaster_model.pkl', 'rb') as f:
        loaded_model = pickle.load(f)
    
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        loaded_vectorizer = pickle.load(f)
    
    # Test with sample texts
    test_texts = [
        "URGENT: Major earthquake hits downtown area, buildings collapsing!",
        "Beautiful sunset tonight, perfect weather for a walk",
        "Fire spreading rapidly near residential areas, evacuations ordered",
        "Having a great day at the beach with friends"
    ]
    
    for text in test_texts:
        text_clean = preprocess_text(text)
        text_vectorized = loaded_vectorizer.transform([text_clean])
        prediction = loaded_model.predict(text_vectorized)[0]
        confidence = max(loaded_model.predict_proba(text_vectorized)[0])
        
        print(f"Text: {text[:50]}...")
        print(f"Prediction: {'Disaster' if prediction else 'Normal'} (confidence: {confidence:.3f})")
        print()

if __name__ == "__main__":
    create_and_save_model()

