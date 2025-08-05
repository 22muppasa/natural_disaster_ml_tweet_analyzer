from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import json
import time
from datetime import datetime, timedelta
import threading
import asyncio
from twitter_integration import TwitterIntegrationService

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Disaster Tweet Triage API",
    description="Enhanced API with real-time Twitter integration for disaster monitoring",
    version="3.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for real-time data
live_tweets = []
tweet_cache = {}
streaming_status = {"active": False, "last_update": None}
twitter_service = None

# Pydantic models
class TweetInput(BaseModel):
    text: str
    location: Optional[str] = ""
    keyword: Optional[str] = ""

class BatchTweetInput(BaseModel):
    tweets: List[TweetInput]

class StreamingConfig(BaseModel):
    enabled: bool
    interval: Optional[int] = 30
    max_tweets: Optional[int] = 100

# Initialize Twitter service
def initialize_twitter_service():
    """Initialize the Twitter integration service"""
    global twitter_service
    try:
        # Try to use real API if key is available, otherwise use simulation
        twitter_service = TwitterIntegrationService(simulation_mode=True)
        print("✅ Twitter integration service initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Twitter service: {e}")
        return False

# Background task for real-time tweet streaming
def handle_new_tweets(tweets: List[Dict]):
    """Handle new tweets from the streaming service"""
    global live_tweets, tweet_cache, streaming_status
    
    current_time = datetime.now()
    
    for tweet in tweets:
        # Add timestamp and processing info
        tweet['processed_at'] = current_time.isoformat()
        tweet['source'] = 'twitter_stream'
        
        # Add to live tweets (keep only recent ones)
        live_tweets.append(tweet)
        
        # Cache the tweet
        tweet_cache[tweet['id']] = tweet
    
    # Keep only last 100 tweets in live feed
    live_tweets = live_tweets[-100:]
    
    # Update streaming status
    streaming_status['last_update'] = current_time.isoformat()
    streaming_status['total_processed'] = len(tweet_cache)
    
    print(f"📡 Processed {len(tweets)} new disaster tweets (Total cached: {len(tweet_cache)})")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    success = initialize_twitter_service()
    if success:
        print("🚀 Real-time disaster tweet triage API started successfully")
    else:
        print("⚠️ API started with limited functionality")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with Twitter service status"""
    global twitter_service, streaming_status
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": bool(twitter_service and twitter_service.model),
        "twitter_service": "active" if twitter_service else "inactive",
        "streaming": streaming_status,
        "cached_tweets": len(tweet_cache),
        "live_tweets": len(live_tweets)
    }
    
    if twitter_service:
        health_status.update(twitter_service.get_stream_status())
    
    return health_status

# Single tweet prediction (enhanced)
@app.post("/predict")
async def predict_tweet(tweet: TweetInput):
    """Predict if a single tweet is about a disaster with enhanced features"""
    global twitter_service
    
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not available")
    
    try:
        # Use the Twitter service's classification
        classification = twitter_service.classify_tweet(tweet.text)
        
        # Calculate priority score
        priority_score = twitter_service.calculate_priority_score(
            tweet.text, tweet.location, classification['confidence']
        )
        
        # Get geolocation if available
        coordinates = None
        geolocation_confidence = 0.0
        
        if tweet.location:
            # Simple coordinate extraction (enhanced version would use geocoding API)
            if ',' in tweet.location and any(c.isdigit() for c in tweet.location):
                try:
                    parts = tweet.location.split(',')
                    if len(parts) == 2:
                        lat, lon = float(parts[0].strip()), float(parts[1].strip())
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            coordinates = [lat, lon]
                            geolocation_confidence = 0.8
                except:
                    pass
            
            if not coordinates:
                # Use sample coordinates for known locations
                location_map = {
                    'san francisco': [37.7749, -122.4194],
                    'los angeles': [34.0522, -118.2437],
                    'new york': [40.7128, -74.0060],
                    'houston': [29.7604, -95.3698],
                    'chicago': [41.8781, -87.6298]
                }
                
                for city, coords in location_map.items():
                    if city in tweet.location.lower():
                        coordinates = coords
                        geolocation_confidence = 0.9
                        break
        
        # Enhanced priority factors
        priority_factors = {
            "base_confidence": classification['confidence'],
            "keyword_boost": 0.1 if tweet.keyword and any(kw in tweet.keyword.lower() for kw in ['fire', 'earthquake', 'flood']) else 0.0,
            "location_boost": 0.2 if coordinates else (0.1 if tweet.location else 0.0),
            "urgency_boost": 0.3 if any(word in tweet.text.lower() for word in ['urgent', 'emergency', 'help']) else 0.0,
            "geolocation_confidence": geolocation_confidence
        }
        
        return {
            "text": tweet.text,
            "is_disaster": classification['is_disaster'],
            "confidence": classification['confidence'],
            "priority_score": priority_score,
            "coordinates": coordinates,
            "geolocation_confidence": geolocation_confidence,
            "priority_factors": priority_factors,
            "classification_method": classification.get('method', 'unknown'),
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Batch prediction
@app.post("/predict_batch")
async def predict_batch(batch: BatchTweetInput):
    """Predict multiple tweets and return sorted by priority"""
    results = []
    
    for tweet_input in batch.tweets:
        try:
            result = await predict_tweet(tweet_input)
            results.append(result)
        except Exception as e:
            # Continue processing other tweets even if one fails
            print(f"Error processing tweet: {e}")
            continue
    
    # Sort by priority score (highest first)
    results.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return results

# Real-time tweet streaming endpoints
@app.post("/streaming/start")
async def start_streaming(config: StreamingConfig):
    """Start real-time tweet streaming"""
    global twitter_service, streaming_status
    
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not available")
    
    if streaming_status['active']:
        return {"message": "Streaming already active", "status": streaming_status}
    
    try:
        # Start streaming with callback
        twitter_service.start_streaming(
            callback_function=handle_new_tweets,
            interval=config.interval
        )
        
        streaming_status['active'] = True
        streaming_status['started_at'] = datetime.now().isoformat()
        streaming_status['config'] = config.dict()
        
        return {
            "message": "Real-time streaming started successfully",
            "status": streaming_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming: {str(e)}")

@app.post("/streaming/stop")
async def stop_streaming():
    """Stop real-time tweet streaming"""
    global twitter_service, streaming_status
    
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not available")
    
    try:
        twitter_service.stop_streaming()
        streaming_status['active'] = False
        streaming_status['stopped_at'] = datetime.now().isoformat()
        
        return {
            "message": "Streaming stopped successfully",
            "status": streaming_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop streaming: {str(e)}")

@app.get("/streaming/status")
async def get_streaming_status():
    """Get current streaming status"""
    global streaming_status, twitter_service
    
    status = streaming_status.copy()
    
    if twitter_service:
        status.update(twitter_service.get_stream_status())
    
    return status

# Live tweets endpoint
@app.get("/tweets/live")
async def get_live_tweets(limit: int = 50):
    """Get recent live disaster tweets"""
    global live_tweets
    
    # Return most recent tweets, limited by the specified amount
    recent_tweets = live_tweets[-limit:] if live_tweets else []
    
    return {
        "tweets": recent_tweets,
        "count": len(recent_tweets),
        "total_cached": len(tweet_cache),
        "last_update": streaming_status.get('last_update'),
        "streaming_active": streaming_status.get('active', False)
    }

# Search tweets endpoint
@app.get("/tweets/search")
async def search_tweets(
    query: Optional[str] = None,
    max_results: int = 50,
    disaster_only: bool = True
):
    """Search for tweets using the Twitter service"""
    global twitter_service
    
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not available")
    
    try:
        tweets = twitter_service.search_tweets(query=query, max_results=max_results)
        
        if disaster_only:
            tweets = [t for t in tweets if t['is_disaster']]
        
        # Sort by priority score
        tweets.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return {
            "tweets": tweets,
            "count": len(tweets),
            "query": query,
            "disaster_only": disaster_only,
            "searched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

# Top priority tweets (enhanced)
@app.get("/top_priority")
async def get_top_priority_tweets(limit: int = 10, source: str = "all"):
    """Get top priority disaster tweets from various sources"""
    global live_tweets, tweet_cache
    
    all_tweets = []
    
    if source in ["all", "live"]:
        all_tweets.extend(live_tweets)
    
    if source in ["all", "cache"]:
        all_tweets.extend(list(tweet_cache.values()))
    
    # Remove duplicates based on tweet ID
    seen_ids = set()
    unique_tweets = []
    for tweet in all_tweets:
        if tweet['id'] not in seen_ids:
            unique_tweets.append(tweet)
            seen_ids.add(tweet['id'])
    
    # Filter for disaster tweets only
    disaster_tweets = [t for t in unique_tweets if t.get('is_disaster', False)]
    
    # Sort by priority score
    disaster_tweets.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    return {
        "tweets": disaster_tweets[:limit],
        "total_available": len(disaster_tweets),
        "source": source,
        "retrieved_at": datetime.now().isoformat()
    }

# Statistics endpoint
@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics"""
    global live_tweets, tweet_cache, streaming_status, twitter_service
    
    # Calculate statistics
    total_tweets = len(tweet_cache)
    disaster_tweets = len([t for t in tweet_cache.values() if t.get('is_disaster', False)])
    
    # Recent activity (last hour)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_tweets = [
        t for t in tweet_cache.values() 
        if 'processed_at' in t and datetime.fromisoformat(t['processed_at']) > one_hour_ago
    ]
    
    stats = {
        "total_processed_tweets": total_tweets,
        "disaster_tweets": disaster_tweets,
        "normal_tweets": total_tweets - disaster_tweets,
        "live_tweets_count": len(live_tweets),
        "recent_activity": {
            "last_hour": len(recent_tweets),
            "disaster_rate": len([t for t in recent_tweets if t.get('is_disaster', False)]) / max(len(recent_tweets), 1)
        },
        "streaming": streaming_status,
        "system": {
            "uptime": "active",
            "model_type": "Logistic Regression with TF-IDF",
            "features": "Real-time Twitter integration, ML classification, Priority scoring",
            "version": "3.0.0"
        }
    }
    
    if twitter_service:
        stats["twitter_service"] = twitter_service.get_stream_status()
    
    return stats

# Manual tweet ingestion for testing
@app.post("/tweets/ingest")
async def ingest_test_tweets(count: int = 10):
    """Manually ingest test tweets for demonstration"""
    global twitter_service
    
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not available")
    
    try:
        # Generate test tweets
        tweets = twitter_service.search_tweets(max_results=count)
        
        # Process them as if they came from streaming
        disaster_tweets = [t for t in tweets if t['is_disaster']]
        
        if disaster_tweets:
            handle_new_tweets(disaster_tweets)
        
        return {
            "message": f"Ingested {len(disaster_tweets)} disaster tweets out of {len(tweets)} total",
            "disaster_tweets": disaster_tweets,
            "ingested_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Real-Time Disaster Tweet Triage API...")
    print("📡 Features: Real-time Twitter streaming, ML classification, Priority scoring")
    print("🌐 Access: http://localhost:8002")
    print("📚 Docs: http://localhost:8002/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )

