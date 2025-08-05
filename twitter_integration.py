import requests
import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pickle
import os

class TwitterIntegrationService:
    """
    Twitter integration service that supports both real API and simulation modes.
    For production use with real Twitter API, set TWITTER_API_KEY environment variable.
    For demonstration, uses simulation mode with realistic disaster tweet patterns.
    """
    
    def __init__(self, api_key: Optional[str] = None, simulation_mode: bool = True):
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.simulation_mode = simulation_mode or not self.api_key
        self.base_url = "https://api.twitterapi.io/v2"
        self.is_streaming = False
        self.stream_thread = None
        self.tweet_callback = None
        
        # Load the trained model for classification
        self.load_model()
        
        # Disaster-related keywords for filtering
        self.disaster_keywords = [
            'earthquake', 'fire', 'flood', 'tornado', 'hurricane', 'wildfire',
            'emergency', 'disaster', 'evacuation', 'rescue', 'urgent', 'help',
            'explosion', 'collapse', 'storm', 'tsunami', 'landslide', 'avalanche',
            'accident', 'crash', 'incident', 'alert', 'warning', 'danger'
        ]
        
        # Sample locations for simulation
        self.sample_locations = [
            {"name": "San Francisco, CA", "coords": [37.7749, -122.4194]},
            {"name": "Los Angeles, CA", "coords": [34.0522, -118.2437]},
            {"name": "New York, NY", "coords": [40.7128, -74.0060]},
            {"name": "Houston, TX", "coords": [29.7604, -95.3698]},
            {"name": "Chicago, IL", "coords": [41.8781, -87.6298]},
            {"name": "Miami, FL", "coords": [25.7617, -80.1918]},
            {"name": "Seattle, WA", "coords": [47.6062, -122.3321]},
            {"name": "Denver, CO", "coords": [39.7392, -104.9903]},
            {"name": "Atlanta, GA", "coords": [33.7490, -84.3880]},
            {"name": "Phoenix, AZ", "coords": [33.4484, -112.0740]}
        ]
        
        # Disaster tweet templates for simulation
        self.disaster_templates = [
            "URGENT: Major {disaster_type} hits {location}, {action_needed}!",
            "{disaster_type} spreading rapidly near {location}, {action_needed}",
            "Emergency: {disaster_type} reported in {location}, {action_needed}",
            "Breaking: {disaster_type} warning issued for {location}",
            "{disaster_type} spotted moving towards {location}",
            "ALERT: {disaster_type} in {location}, emergency services responding",
            "Massive {disaster_type} affecting {location} area",
            "{disaster_type} evacuation ordered for {location}",
            "Critical: {disaster_type} emergency in {location}",
            "Live: {disaster_type} situation developing in {location}"
        ]
        
        self.disaster_types = [
            "earthquake", "wildfire", "flood", "tornado", "hurricane",
            "building fire", "explosion", "storm", "landslide", "gas leak"
        ]
        
        self.action_phrases = [
            "evacuations ordered", "buildings collapsing", "emergency services responding",
            "immediate evacuation needed", "roads blocked", "power outages reported",
            "water levels rising", "winds reaching dangerous speeds", "smoke visible",
            "residents advised to shelter", "multiple injuries reported", "rescue operations underway"
        ]
        
        # Non-disaster tweet templates for realistic simulation
        self.normal_templates = [
            "Beautiful sunset tonight in {location}",
            "Great weather today in {location}",
            "Having lunch at a nice restaurant in {location}",
            "Traffic is moving well in {location} today",
            "Enjoying the weekend in {location}",
            "New coffee shop opened in {location}",
            "Concert was amazing last night in {location}",
            "Perfect day for a walk in {location}",
            "Local farmers market busy in {location}",
            "Sports game was exciting in {location}"
        ]
    
    def load_model(self):
        """Load the trained disaster classification model"""
        try:
            with open('disaster_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open('tfidf_vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            print("✅ Loaded trained disaster classification model")
        except FileNotFoundError:
            print("⚠️ Model files not found, will use basic keyword matching")
            self.model = None
            self.vectorizer = None
    
    def classify_tweet(self, text: str) -> Dict:
        """Classify a tweet as disaster-related or not"""
        if self.model and self.vectorizer:
            # Use trained ML model
            try:
                text_vectorized = self.vectorizer.transform([text])
                prediction = self.model.predict(text_vectorized)[0]
                confidence = max(self.model.predict_proba(text_vectorized)[0])
                
                return {
                    'is_disaster': bool(prediction),
                    'confidence': float(confidence),
                    'method': 'ml_model'
                }
            except Exception as e:
                print(f"Error using ML model: {e}")
        
        # Fallback to keyword matching
        text_lower = text.lower()
        disaster_score = sum(1 for keyword in self.disaster_keywords if keyword in text_lower)
        is_disaster = disaster_score > 0
        confidence = min(0.5 + (disaster_score * 0.1), 0.95) if is_disaster else 0.3
        
        return {
            'is_disaster': is_disaster,
            'confidence': confidence,
            'method': 'keyword_matching'
        }
    
    def search_tweets_real(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search for tweets using real Twitter API"""
        if not self.api_key:
            raise ValueError("Twitter API key required for real API access")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'query': query,
            'max_results': min(max_results, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,geo,lang',
            'user.fields': 'location,verified',
            'expansions': 'author_id,geo.place_id'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = []
                
                for tweet in data.get('data', []):
                    processed_tweet = self.process_tweet(tweet, data.get('includes', {}))
                    tweets.append(processed_tweet)
                
                return tweets
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return []
    
    def generate_simulated_tweet(self, force_disaster: bool = None) -> Dict:
        """Generate a realistic simulated tweet"""
        location = random.choice(self.sample_locations)
        
        # Determine if this should be a disaster tweet
        if force_disaster is None:
            is_disaster = random.random() < 0.3  # 30% chance of disaster tweet
        else:
            is_disaster = force_disaster
        
        if is_disaster:
            template = random.choice(self.disaster_templates)
            disaster_type = random.choice(self.disaster_types)
            action = random.choice(self.action_phrases)
            
            text = template.format(
                disaster_type=disaster_type,
                location=location['name'],
                action_needed=action
            )
        else:
            template = random.choice(self.normal_templates)
            text = template.format(location=location['name'])
        
        # Generate realistic tweet metadata
        tweet_id = f"sim_{int(time.time())}_{random.randint(1000, 9999)}"
        created_at = datetime.now() - timedelta(minutes=random.randint(0, 60))
        
        return {
            'id': tweet_id,
            'text': text,
            'created_at': created_at.isoformat(),
            'author_id': f"user_{random.randint(100000, 999999)}",
            'location': location['name'],
            'coordinates': location['coords'],
            'public_metrics': {
                'retweet_count': random.randint(0, 100),
                'like_count': random.randint(0, 500),
                'reply_count': random.randint(0, 50)
            },
            'lang': 'en',
            'simulation': True
        }
    
    def search_tweets_simulation(self, query: str, max_results: int = 5000) -> List[Dict]:
        """Generate simulated tweets for demonstration"""
        tweets = []
        
        # Generate a mix of disaster and normal tweets
        disaster_count = int(max_results * 0.4)  # 40% disaster tweets
        normal_count = max_results - disaster_count
        
        # Generate disaster tweets
        for _ in range(disaster_count):
            tweet = self.generate_simulated_tweet(force_disaster=True)
            tweets.append(tweet)
        
        # Generate normal tweets
        for _ in range(normal_count):
            tweet = self.generate_simulated_tweet(force_disaster=False)
            tweets.append(tweet)
        
        # Shuffle to make it realistic
        random.shuffle(tweets)
        
        # Process tweets through classification
        processed_tweets = []
        for tweet in tweets:
            processed_tweet = self.process_tweet(tweet)
            processed_tweets.append(processed_tweet)
        
        return processed_tweets
    
    def process_tweet(self, tweet: Dict, includes: Dict = None) -> Dict:
        """Process a raw tweet into our standardized format"""
        # Extract location information
        location = None
        coordinates = None
        
        if 'coordinates' in tweet:
            coordinates = tweet['coordinates']
        elif 'location' in tweet:
            location = tweet['location']
        elif includes and 'users' in includes:
            # Try to get location from user data
            author_id = tweet.get('author_id')
            for user in includes['users']:
                if user['id'] == author_id and 'location' in user:
                    location = user['location']
                    break
        
        # Classify the tweet
        classification = self.classify_tweet(tweet['text'])
        
        # Calculate priority score (reuse existing logic)
        priority_score = self.calculate_priority_score(
            tweet['text'], 
            location, 
            classification['confidence']
        )
        
        return {
            'id': tweet['id'],
            'text': tweet['text'],
            'created_at': tweet.get('created_at', datetime.now().isoformat()),
            'author_id': tweet.get('author_id'),
            'location': location,
            'coordinates': coordinates,
            'public_metrics': tweet.get('public_metrics', {}),
            'lang': tweet.get('lang', 'en'),
            'is_disaster': classification['is_disaster'],
            'confidence': classification['confidence'],
            'priority_score': priority_score,
            'classification_method': classification['method'],
            'simulation': tweet.get('simulation', False)
        }
    
    def calculate_priority_score(self, text: str, location: str, base_confidence: float) -> float:
        """Calculate priority score for a tweet (reuse existing logic)"""
        priority_score = base_confidence
        
        # Urgency boost
        urgency_keywords = ['urgent', 'emergency', 'help', 'fire', 'earthquake', 'flood']
        if any(keyword in text.lower() for keyword in urgency_keywords):
            priority_score += 0.15
        
        # Location boost
        if location:
            priority_score += 0.1
        
        # Keyword boost
        disaster_keywords = ['disaster', 'emergency', 'evacuation', 'rescue']
        if any(keyword in text.lower() for keyword in disaster_keywords):
            priority_score += 0.1
        
        return min(priority_score, 1.0)
    
    def search_tweets(self, query: str = None, max_results: int = 1000) -> List[Dict]:
        """Search for tweets (real or simulated based on mode)"""
        if query is None:
            # Default disaster-related query
            query = ' OR '.join(self.disaster_keywords[:10])  # Use top 10 keywords
        
        if self.simulation_mode:
            print(f"🔄 Generating {max_results} simulated tweets for query: {query}")
            return self.search_tweets_simulation(query, max_results)
        else:
            print(f"🔍 Searching real tweets for query: {query}")
            return self.search_tweets_real(query, max_results)
    
    def start_streaming(self, callback_function, interval: int = 30):
        """Start streaming tweets at regular intervals"""
        self.tweet_callback = callback_function
        self.is_streaming = True
        
        def stream_worker():
            while self.is_streaming:
                try:
                    # Fetch new tweets
                    tweets = self.search_tweets(max_results=10)
                    
                    # Filter for disaster tweets only
                    disaster_tweets = [t for t in tweets if t['is_disaster']]
                    
                    if disaster_tweets and self.tweet_callback:
                        self.tweet_callback(disaster_tweets)
                    
                    # Wait for next interval
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Error in streaming: {e}")
                    time.sleep(interval)
        
        self.stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self.stream_thread.start()
        
        mode = "simulation" if self.simulation_mode else "real API"
        print(f"🚀 Started Twitter streaming in {mode} mode (interval: {interval}s)")
    
    def stop_streaming(self):
        """Stop the tweet streaming"""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=5)
        print("⏹️ Stopped Twitter streaming")
    
    def get_stream_status(self) -> Dict:
        """Get current streaming status"""
        return {
            'is_streaming': self.is_streaming,
            'mode': 'simulation' if self.simulation_mode else 'real_api',
            'api_key_configured': bool(self.api_key),
            'model_loaded': bool(self.model)
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the service
    twitter_service = TwitterIntegrationService(simulation_mode=True)
    
    # Test tweet search
    print("Testing tweet search...")
    tweets = twitter_service.search_tweets(max_results=5)
    
    for tweet in tweets:
        print(f"\n📱 Tweet: {tweet['text'][:100]}...")
        print(f"   🎯 Disaster: {tweet['is_disaster']} (confidence: {tweet['confidence']:.2f})")
        print(f"   📍 Location: {tweet['location']}")
        print(f"   ⭐ Priority: {tweet['priority_score']:.2f}")
    
    # Test streaming (for a short time)
    def handle_new_tweets(tweets):
        print(f"\n🔥 Received {len(tweets)} new disaster tweets:")
        for tweet in tweets:
            print(f"   • {tweet['text'][:80]}... (Priority: {tweet['priority_score']:.2f})")
    
    print("\n\nTesting streaming for 10 seconds...")
    twitter_service.start_streaming(handle_new_tweets, interval=5)
    time.sleep(10)
    twitter_service.stop_streaming()
    
    print("\n✅ Twitter integration service test completed!")

