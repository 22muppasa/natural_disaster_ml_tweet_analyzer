import requests
import json
import time
import random
import threading
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pickle
import tweepy
from dataclasses import dataclass

@dataclass
class TwitterConfig:
    """Configuration for Twitter API access"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    bearer_token: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    api_type: str = "official"  # "official" or "twitterapi_io"
    simulation_mode: bool = True

class RealTwitterIntegrationService:
    """
    Enhanced Twitter integration service with real API support.
    Supports both Official Twitter API v2 and TwitterAPI.io
    """
    
    def __init__(self, config: TwitterConfig = None):
        self.config = config or TwitterConfig()
        self.is_streaming = False
        self.stream_thread = None
        self.tweet_callback = None
        self.rate_limit_reset = None
        self.requests_made = 0
        self.daily_cost = 0.0
        
        # Load environment variables if config not provided
        if not self.config.api_key:
            self.config.api_key = os.getenv('TWITTER_API_KEY')
        if not self.config.bearer_token:
            self.config.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not self.config.api_secret:
            self.config.api_secret = os.getenv('TWITTER_API_SECRET')
        if not self.config.access_token:
            self.config.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        if not self.config.access_token_secret:
            self.config.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Determine API type and simulation mode
        if self.config.api_type == "official" and self.config.bearer_token:
            self.config.simulation_mode = False
            self.api_client = self._init_official_client()
        elif self.config.api_type == "twitterapi_io" and self.config.api_key:
            self.config.simulation_mode = False
            self.api_client = None  # Will use requests directly
        else:
            self.config.simulation_mode = True
            self.api_client = None
        
        # Load the trained model for classification
        self.load_model()
        
        # Disaster-related keywords for filtering
        self.disaster_keywords = [
            'earthquake', 'fire', 'flood', 'tornado', 'hurricane', 'wildfire',
            'emergency', 'disaster', 'evacuation', 'rescue', 'urgent', 'help',
            'explosion', 'collapse', 'storm', 'tsunami', 'landslide', 'avalanche',
            'accident', 'crash', 'incident', 'alert', 'warning', 'danger',
            'breaking', 'critical', 'severe', 'major', 'massive'
        ]
        
        # Enhanced location mapping with coordinates
        self.location_coordinates = {
            'san francisco': [37.7749, -122.4194],
            'los angeles': [34.0522, -118.2437],
            'new york': [40.7128, -74.0060],
            'houston': [29.7604, -95.3698],
            'chicago': [41.8781, -87.6298],
            'miami': [25.7617, -80.1918],
            'seattle': [47.6062, -122.3321],
            'denver': [39.7392, -104.9903],
            'atlanta': [33.7490, -84.3880],
            'phoenix': [33.4484, -112.0740],
            'philadelphia': [39.9526, -75.1652],
            'dallas': [32.7767, -96.7970],
            'boston': [42.3601, -71.0589],
            'detroit': [42.3314, -83.0458],
            'washington': [38.9072, -77.0369],
            'las vegas': [36.1699, -115.1398],
            'portland': [45.5152, -122.6784],
            'nashville': [36.1627, -86.7816],
            'memphis': [35.1495, -90.0490],
            'louisville': [38.2527, -85.7585]
        }
        
        print(f"🔧 Twitter Integration initialized:")
        print(f"   API Type: {self.config.api_type}")
        print(f"   Simulation Mode: {self.config.simulation_mode}")
        print(f"   Model Loaded: {bool(self.model)}")
    
    def _init_official_client(self):
        """Initialize official Twitter API v2 client"""
        try:
            if self.config.access_token and self.config.access_token_secret:
                # OAuth 1.0a User Context
                client = tweepy.Client(
                    bearer_token=self.config.bearer_token,
                    consumer_key=self.config.api_key,
                    consumer_secret=self.config.api_secret,
                    access_token=self.config.access_token,
                    access_token_secret=self.config.access_token_secret,
                    wait_on_rate_limit=True
                )
            else:
                # App-only authentication
                client = tweepy.Client(
                    bearer_token=self.config.bearer_token,
                    wait_on_rate_limit=True
                )
            
            # Test the connection
            try:
                client.get_me()
                print("✅ Official Twitter API v2 client initialized successfully")
                return client
            except Exception as e:
                print(f"⚠️ Twitter API test failed: {e}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to initialize Twitter API client: {e}")
            return None
    
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
    
    def search_tweets_official_api(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search for tweets using Official Twitter API v2"""
        if not self.api_client:
            raise ValueError("Official Twitter API client not initialized")
        
        try:
            # Enhanced query with disaster-specific filters
            enhanced_query = f"({query}) lang:en -is:retweet"
            
            tweets = self.api_client.search_recent_tweets(
                query=enhanced_query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo', 'lang', 'context_annotations'],
                user_fields=['location', 'verified', 'public_metrics'],
                expansions=['author_id', 'geo.place_id'],
                place_fields=['full_name', 'country', 'geo']
            )
            
            if not tweets.data:
                return []
            
            # Process tweets with enhanced metadata
            processed_tweets = []
            users = {user.id: user for user in tweets.includes.get('users', [])} if tweets.includes else {}
            places = {place.id: place for place in tweets.includes.get('places', [])} if tweets.includes else {}
            
            for tweet in tweets.data:
                processed_tweet = self._process_official_tweet(tweet, users, places)
                processed_tweets.append(processed_tweet)
            
            self.requests_made += 1
            print(f"📡 Retrieved {len(processed_tweets)} tweets from Official API")
            
            return processed_tweets
            
        except tweepy.TooManyRequests:
            print("⚠️ Rate limit exceeded for Official Twitter API")
            return []
        except Exception as e:
            print(f"❌ Error searching tweets with Official API: {e}")
            return []
    
    def search_tweets_twitterapi_io(self, query: str, max_results: int = 100) -> List[Dict]:
        """Search for tweets using TwitterAPI.io"""
        if not self.config.api_key:
            raise ValueError("TwitterAPI.io API key not provided")
        
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'query': f"{query} lang:en",
            'max_results': min(max_results, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,geo,lang,context_annotations',
            'user.fields': 'location,verified,public_metrics',
            'expansions': 'author_id,geo.place_id'
        }
        
        try:
            response = requests.get(
                "https://api.twitterapi.io/v2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = []
                
                users = {}
                places = {}
                if 'includes' in data:
                    users = {user['id']: user for user in data['includes'].get('users', [])}
                    places = {place['id']: place for place in data['includes'].get('places', [])}
                
                for tweet_data in data.get('data', []):
                    processed_tweet = self._process_twitterapi_io_tweet(tweet_data, users, places)
                    tweets.append(processed_tweet)
                
                # Calculate cost
                tweet_count = len(tweets)
                cost = (tweet_count / 1000) * 0.15  # $0.15 per 1K tweets
                self.daily_cost += cost
                self.requests_made += 1
                
                print(f"📡 Retrieved {tweet_count} tweets from TwitterAPI.io (Cost: ${cost:.4f})")
                
                return tweets
            else:
                print(f"❌ TwitterAPI.io Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching tweets with TwitterAPI.io: {e}")
            return []
    
    def _process_official_tweet(self, tweet, users: Dict, places: Dict) -> Dict:
        """Process a tweet from Official Twitter API v2"""
        # Get user information
        user = users.get(tweet.author_id, {})
        user_location = getattr(user, 'location', None) if user else None
        
        # Get place information
        place = None
        if hasattr(tweet, 'geo') and tweet.geo and 'place_id' in tweet.geo:
            place = places.get(tweet.geo['place_id'])
        
        # Extract coordinates
        coordinates = None
        location_text = None
        
        if place:
            location_text = getattr(place, 'full_name', None)
            if hasattr(place, 'geo') and place.geo:
                # Extract coordinates from place geo data
                if 'bbox' in place.geo:
                    bbox = place.geo['bbox']
                    # Use center of bounding box
                    coordinates = [(bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2]
        elif user_location:
            location_text = user_location
            coordinates = self._get_coordinates_from_text(user_location)
        
        # Classify the tweet
        classification = self.classify_tweet(tweet.text)
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            tweet.text, 
            location_text, 
            classification['confidence'],
            coordinates is not None
        )
        
        return {
            'id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at.isoformat() if tweet.created_at else datetime.now().isoformat(),
            'author_id': tweet.author_id,
            'location': location_text,
            'coordinates': coordinates,
            'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
            'lang': getattr(tweet, 'lang', 'en'),
            'is_disaster': classification['is_disaster'],
            'confidence': classification['confidence'],
            'priority_score': priority_score,
            'classification_method': classification['method'],
            'user_verified': getattr(user, 'verified', False) if user else False,
            'source': 'official_api',
            'simulation': False
        }
    
    def _process_twitterapi_io_tweet(self, tweet_data: Dict, users: Dict, places: Dict) -> Dict:
        """Process a tweet from TwitterAPI.io"""
        # Get user information
        user = users.get(tweet_data.get('author_id'), {})
        user_location = user.get('location')
        
        # Get place information
        place = None
        if 'geo' in tweet_data and tweet_data['geo']:
            place_id = tweet_data['geo'].get('place_id')
            if place_id:
                place = places.get(place_id)
        
        # Extract coordinates
        coordinates = None
        location_text = None
        
        if place:
            location_text = place.get('full_name')
            if 'geo' in place and place['geo']:
                # Extract coordinates from place geo data
                geo_data = place['geo']
                if 'bbox' in geo_data:
                    bbox = geo_data['bbox']
                    coordinates = [(bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2]
        elif user_location:
            location_text = user_location
            coordinates = self._get_coordinates_from_text(user_location)
        
        # Classify the tweet
        classification = self.classify_tweet(tweet_data['text'])
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            tweet_data['text'], 
            location_text, 
            classification['confidence'],
            coordinates is not None
        )
        
        return {
            'id': tweet_data['id'],
            'text': tweet_data['text'],
            'created_at': tweet_data.get('created_at', datetime.now().isoformat()),
            'author_id': tweet_data.get('author_id'),
            'location': location_text,
            'coordinates': coordinates,
            'public_metrics': tweet_data.get('public_metrics', {}),
            'lang': tweet_data.get('lang', 'en'),
            'is_disaster': classification['is_disaster'],
            'confidence': classification['confidence'],
            'priority_score': priority_score,
            'classification_method': classification['method'],
            'user_verified': user.get('verified', False),
            'source': 'twitterapi_io',
            'simulation': False
        }
    
    def _get_coordinates_from_text(self, location_text: str) -> Optional[List[float]]:
        """Extract coordinates from location text"""
        if not location_text:
            return None
        
        location_lower = location_text.lower()
        
        # Check for direct coordinate format
        if ',' in location_text and any(c.isdigit() for c in location_text):
            try:
                parts = location_text.split(',')
                if len(parts) == 2:
                    lat, lon = float(parts[0].strip()), float(parts[1].strip())
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return [lat, lon]
            except:
                pass
        
        # Check against known locations
        for city, coords in self.location_coordinates.items():
            if city in location_lower:
                return coords
        
        return None
    
    def _calculate_priority_score(self, text: str, location: str, base_confidence: float, has_coordinates: bool) -> float:
        """Calculate priority score for a tweet"""
        priority_score = base_confidence
        
        # Urgency boost for critical keywords
        urgency_keywords = ['urgent', 'emergency', 'help', 'breaking', 'critical', 'severe', 'major']
        if any(keyword in text.lower() for keyword in urgency_keywords):
            priority_score += 0.2
        
        # Disaster type boost
        disaster_keywords = ['fire', 'earthquake', 'flood', 'tornado', 'hurricane', 'explosion']
        if any(keyword in text.lower() for keyword in disaster_keywords):
            priority_score += 0.15
        
        # Location boost
        if has_coordinates:
            priority_score += 0.15
        elif location:
            priority_score += 0.1
        
        # Action keywords boost
        action_keywords = ['evacuation', 'rescue', 'emergency services', 'first responders']
        if any(keyword in text.lower() for keyword in action_keywords):
            priority_score += 0.1
        
        return min(priority_score, 1.0)
    
    def search_tweets(self, query: str = None, max_results: int = 50) -> List[Dict]:
        """Search for tweets using the configured API"""
        if query is None:
            query = ' OR '.join(self.disaster_keywords[:10])
        
        if self.config.simulation_mode:
            print(f"🔄 Using simulation mode for query: {query}")
            return self._generate_simulated_tweets(query, max_results)
        
        try:
            if self.config.api_type == "official":
                return self.search_tweets_official_api(query, max_results)
            elif self.config.api_type == "twitterapi_io":
                return self.search_tweets_twitterapi_io(query, max_results)
            else:
                raise ValueError(f"Unknown API type: {self.config.api_type}")
        
        except Exception as e:
            print(f"❌ Real API failed, falling back to simulation: {e}")
            return self._generate_simulated_tweets(query, max_results)
    
    def _generate_simulated_tweets(self, query: str, max_results: int) -> List[Dict]:
        """Generate simulated tweets for fallback"""
        # Import the original simulation logic
        from twitter_integration import TwitterIntegrationService
        
        sim_service = TwitterIntegrationService(simulation_mode=True)
        return sim_service.search_tweets_simulation(query, max_results)
    
    def start_streaming(self, callback_function, interval: int = 60):
        """Start streaming tweets at regular intervals"""
        self.tweet_callback = callback_function
        self.is_streaming = True
        
        def stream_worker():
            while self.is_streaming:
                try:
                    # Fetch new tweets
                    tweets = self.search_tweets(max_results=20)
                    
                    # Filter for disaster tweets only
                    disaster_tweets = [t for t in tweets if t['is_disaster']]
                    
                    if disaster_tweets and self.tweet_callback:
                        self.tweet_callback(disaster_tweets)
                    
                    # Wait for next interval
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"❌ Error in streaming: {e}")
                    time.sleep(interval)
        
        self.stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self.stream_thread.start()
        
        api_mode = "simulation" if self.config.simulation_mode else f"real API ({self.config.api_type})"
        print(f"🚀 Started Twitter streaming in {api_mode} mode (interval: {interval}s)")
    
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
            'mode': 'simulation' if self.config.simulation_mode else 'real_api',
            'api_type': self.config.api_type,
            'api_key_configured': bool(self.config.api_key or self.config.bearer_token),
            'model_loaded': bool(self.model),
            'requests_made': self.requests_made,
            'daily_cost': self.daily_cost
        }
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'requests_made_today': self.requests_made,
            'estimated_daily_cost': self.daily_cost,
            'api_type': self.config.api_type,
            'simulation_mode': self.config.simulation_mode,
            'rate_limit_reset': self.rate_limit_reset
        }

# Example usage and configuration
if __name__ == "__main__":
    # Example 1: Official Twitter API v2
    official_config = TwitterConfig(
        bearer_token="your_bearer_token_here",
        api_type="official",
        simulation_mode=False
    )
    
    # Example 2: TwitterAPI.io
    twitterapi_config = TwitterConfig(
        api_key="your_twitterapi_io_key_here",
        api_type="twitterapi_io",
        simulation_mode=False
    )
    
    # Example 3: Simulation mode (default)
    sim_config = TwitterConfig(simulation_mode=True)
    
    # Initialize service
    twitter_service = RealTwitterIntegrationService(sim_config)
    
    # Test search
    print("Testing tweet search...")
    tweets = twitter_service.search_tweets("earthquake OR fire OR flood", max_results=5)
    
    for tweet in tweets:
        print(f"\n📱 Tweet: {tweet['text'][:100]}...")
        print(f"   🎯 Disaster: {tweet['is_disaster']} (confidence: {tweet['confidence']:.2f})")
        print(f"   📍 Location: {tweet.get('location', 'Unknown')}")
        print(f"   ⭐ Priority: {tweet['priority_score']:.2f}")
        print(f"   🔗 Source: {tweet.get('source', 'simulation')}")
    
    # Test streaming
    def handle_new_tweets(tweets):
        print(f"\n🔥 Received {len(tweets)} new disaster tweets:")
        for tweet in tweets:
            print(f"   • {tweet['text'][:80]}... (Priority: {tweet['priority_score']:.2f})")
    
    print("\n\nTesting streaming for 30 seconds...")
    twitter_service.start_streaming(handle_new_tweets, interval=10)
    time.sleep(30)
    twitter_service.stop_streaming()
    
    # Show usage stats
    stats = twitter_service.get_usage_stats()
    print(f"\n📊 Usage Stats: {stats}")
    
    print("\n✅ Real Twitter integration service test completed!")

