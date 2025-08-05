# Twitter API Implementation Guide for Real-Time Disaster Monitoring

## 🎯 **Overview**

This guide provides detailed instructions for implementing real Twitter API integration in the disaster tweet triage system. The current system uses simulation mode for demonstration, but can be easily upgraded to use real Twitter data.

## 🔑 **API Options & Pricing**

### **Option 1: TwitterAPI.io (Recommended for Production)**

#### **Pricing**
- **Cost**: $0.15 per 1,000 tweets
- **Payment**: Pay-as-you-go, no minimum spend
- **Credits**: 1 USD = 100,000 credits
- **Minimum**: $0.00015 (15 credits) per API call

#### **Features**
- Real-time Twitter data access
- No rate limits (QPS based)
- Simple REST API
- Comprehensive tweet metadata
- User profile information
- Follower/following data

#### **Implementation Steps**

1. **Sign up for TwitterAPI.io**
   ```bash
   # Visit: https://twitterapi.io/pricing
   # Sign in with Google
   # Add credits to your account
   ```

2. **Get API Key**
   ```bash
   # Dashboard → API Keys → Generate New Key
   export TWITTER_API_KEY="your_api_key_here"
   ```

3. **Update Configuration**
   ```python
   # In twitter_integration.py
   twitter_service = TwitterIntegrationService(
       api_key="your_api_key_here",
       simulation_mode=False  # Enable real API
   )
   ```

4. **Test Integration**
   ```python
   # Test real API access
   tweets = twitter_service.search_tweets("earthquake OR fire OR flood", max_results=10)
   print(f"Retrieved {len(tweets)} real tweets")
   ```

### **Option 2: Official Twitter API v2**

#### **Pricing Tiers**

**Free Tier ($0/month)**
- 1,500 tweets/month
- Basic endpoints only
- No streaming access
- Not suitable for production

**Basic Tier ($100/month)**
- 10,000 tweets/month
- Full v2 endpoints
- No streaming access
- Limited for real-time monitoring

**Pro Tier ($5,000/month)**
- 1M tweets/month
- Filtered stream access ✅
- Real-time capabilities
- Enterprise features

#### **Implementation Steps**

1. **Apply for Developer Account**
   ```bash
   # Visit: https://developer.twitter.com
   # Apply for developer access
   # Wait for approval (can take weeks)
   ```

2. **Create App and Get Keys**
   ```bash
   # Developer Portal → Create App
   # Get Bearer Token, API Key, API Secret
   export TWITTER_BEARER_TOKEN="your_bearer_token"
   export TWITTER_API_KEY="your_api_key"
   export TWITTER_API_SECRET="your_api_secret"
   ```

3. **Implement Official API Client**
   ```python
   import tweepy
   
   # Initialize Tweepy client
   client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
   
   # Search for tweets
   tweets = client.search_recent_tweets(
       query="earthquake OR fire OR flood -is:retweet",
       max_results=100,
       tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo']
   )
   ```

## 🛠️ **Implementation Details**

### **1. Update Twitter Integration Service**

```python
# Enhanced twitter_integration.py
class TwitterIntegrationService:
    def __init__(self, api_key=None, api_type="twitterapi_io"):
        self.api_key = api_key or os.getenv('TWITTER_API_KEY')
        self.api_type = api_type
        self.simulation_mode = not self.api_key
        
        if api_type == "twitterapi_io":
            self.base_url = "https://api.twitterapi.io/v2"
        elif api_type == "official":
            self.base_url = "https://api.twitter.com/2"
            
    def search_tweets_real(self, query, max_results=100):
        if self.api_type == "twitterapi_io":
            return self._search_twitterapi_io(query, max_results)
        elif self.api_type == "official":
            return self._search_official_api(query, max_results)
    
    def _search_twitterapi_io(self, query, max_results):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        params = {
            'query': query,
            'max_results': min(max_results, 100),
            'tweet.fields': 'created_at,author_id,public_metrics,geo,lang'
        }
        
        response = requests.get(
            f"{self.base_url}/tweets/search/recent",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            return self._process_api_response(response.json())
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def _search_official_api(self, query, max_results):
        import tweepy
        
        client = tweepy.Client(bearer_token=self.api_key)
        
        tweets = client.search_recent_tweets(
            query=f"{query} -is:retweet lang:en",
            max_results=max_results,
            tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo', 'lang'],
            user_fields=['location'],
            expansions=['author_id']
        )
        
        return self._process_tweepy_response(tweets)
```

### **2. Environment Configuration**

```bash
# .env file
TWITTER_API_KEY=your_api_key_here
TWITTER_API_TYPE=twitterapi_io  # or "official"
SIMULATION_MODE=false

# For official Twitter API
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_SECRET=your_api_secret
```

### **3. Enhanced Error Handling**

```python
def search_tweets_with_fallback(self, query, max_results=50):
    """Search with automatic fallback to simulation"""
    try:
        if not self.simulation_mode:
            # Try real API first
            tweets = self.search_tweets_real(query, max_results)
            if tweets:
                return tweets
        
        # Fallback to simulation
        print("⚠️ Using simulation mode (API unavailable)")
        return self.search_tweets_simulation(query, max_results)
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("🔄 Falling back to simulation mode")
        return self.search_tweets_simulation(query, max_results)
```

### **4. Real-time Streaming Implementation**

```python
def start_real_streaming(self, callback_function):
    """Start real-time Twitter streaming"""
    if self.api_type == "official" and self.has_streaming_access():
        # Use Twitter API v2 filtered stream
        self._start_filtered_stream(callback_function)
    else:
        # Use polling approach
        self._start_polling_stream(callback_function)

def _start_filtered_stream(self, callback_function):
    """Twitter API v2 filtered stream (Pro tier required)"""
    import tweepy
    
    class StreamListener(tweepy.StreamingClient):
        def on_tweet(self, tweet):
            processed_tweet = self.process_tweet(tweet._json)
            if processed_tweet['is_disaster']:
                callback_function([processed_tweet])
    
    stream = StreamListener(bearer_token=self.api_key)
    
    # Add filtering rules
    rules = [
        tweepy.StreamRule("earthquake OR fire OR flood OR tornado OR hurricane"),
        tweepy.StreamRule("emergency OR disaster OR evacuation OR rescue")
    ]
    
    stream.add_rules(rules)
    stream.filter(tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo'])

def _start_polling_stream(self, callback_function):
    """Polling-based streaming for basic API tiers"""
    def polling_worker():
        last_tweet_id = None
        
        while self.is_streaming:
            try:
                # Search for recent tweets
                tweets = self.search_tweets_real(
                    "earthquake OR fire OR flood OR tornado OR hurricane",
                    max_results=50
                )
                
                # Filter new tweets
                new_tweets = []
                for tweet in tweets:
                    if last_tweet_id and tweet['id'] <= last_tweet_id:
                        break
                    new_tweets.append(tweet)
                
                if new_tweets:
                    last_tweet_id = new_tweets[0]['id']
                    disaster_tweets = [t for t in new_tweets if t['is_disaster']]
                    
                    if disaster_tweets:
                        callback_function(disaster_tweets)
                
                time.sleep(60)  # Poll every minute
                
            except Exception as e:
                print(f"Streaming error: {e}")
                time.sleep(60)
    
    threading.Thread(target=polling_worker, daemon=True).start()
```

## 📊 **Cost Estimation**

### **TwitterAPI.io Costs**

```python
# Cost calculator
def estimate_monthly_cost(tweets_per_day):
    tweets_per_month = tweets_per_day * 30
    cost_per_1k = 0.15  # $0.15 per 1K tweets
    
    monthly_cost = (tweets_per_month / 1000) * cost_per_1k
    
    return {
        'tweets_per_month': tweets_per_month,
        'monthly_cost_usd': monthly_cost,
        'cost_per_tweet': cost_per_1k / 1000
    }

# Example calculations
print(estimate_monthly_cost(1000))   # $4.50/month
print(estimate_monthly_cost(5000))   # $22.50/month
print(estimate_monthly_cost(10000))  # $45.00/month
```

### **Usage Optimization**

```python
# Optimize API usage
class OptimizedTwitterService:
    def __init__(self):
        self.cache = {}
        self.last_search = {}
        
    def search_with_cache(self, query, max_results=50):
        cache_key = f"{query}_{max_results}"
        now = time.time()
        
        # Use cache if less than 5 minutes old
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if now - cached_time < 300:  # 5 minutes
                return cached_data
        
        # Fetch new data
        tweets = self.search_tweets_real(query, max_results)
        self.cache[cache_key] = (now, tweets)
        
        return tweets
    
    def smart_filtering(self, tweets):
        """Filter tweets to reduce processing costs"""
        # Remove duplicates
        seen_texts = set()
        unique_tweets = []
        
        for tweet in tweets:
            text_hash = hash(tweet['text'].lower())
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_tweets.append(tweet)
        
        # Filter by language
        english_tweets = [t for t in unique_tweets if t.get('lang') == 'en']
        
        # Filter by length (avoid spam)
        quality_tweets = [t for t in english_tweets if 20 <= len(t['text']) <= 280]
        
        return quality_tweets
```

## 🔧 **Production Deployment**

### **1. Environment Setup**

```bash
# Production environment variables
export TWITTER_API_KEY="prod_api_key"
export TWITTER_API_TYPE="twitterapi_io"
export SIMULATION_MODE="false"
export LOG_LEVEL="INFO"
export CACHE_SIZE="1000"
export STREAM_INTERVAL="30"
```

### **2. Monitoring & Alerts**

```python
# API usage monitoring
class APIMonitor:
    def __init__(self):
        self.usage_stats = {
            'requests_today': 0,
            'tweets_processed': 0,
            'cost_today': 0.0,
            'errors': 0
        }
    
    def track_request(self, tweet_count, cost):
        self.usage_stats['requests_today'] += 1
        self.usage_stats['tweets_processed'] += tweet_count
        self.usage_stats['cost_today'] += cost
    
    def check_limits(self):
        daily_budget = 50.0  # $50/day limit
        
        if self.usage_stats['cost_today'] > daily_budget * 0.9:
            self.send_alert("Approaching daily budget limit")
        
        if self.usage_stats['errors'] > 10:
            self.send_alert("High error rate detected")
    
    def send_alert(self, message):
        # Send email/Slack notification
        print(f"🚨 ALERT: {message}")
```

### **3. Backup Strategies**

```python
# Multi-source data strategy
class MultiSourceTwitterService:
    def __init__(self):
        self.primary_api = TwitterIntegrationService(api_type="twitterapi_io")
        self.backup_api = TwitterIntegrationService(api_type="official")
        self.simulation = TwitterIntegrationService(simulation_mode=True)
    
    def search_tweets_resilient(self, query, max_results=50):
        # Try primary API
        try:
            tweets = self.primary_api.search_tweets(query, max_results)
            if tweets:
                return tweets
        except Exception as e:
            print(f"Primary API failed: {e}")
        
        # Try backup API
        try:
            tweets = self.backup_api.search_tweets(query, max_results)
            if tweets:
                return tweets
        except Exception as e:
            print(f"Backup API failed: {e}")
        
        # Use simulation as last resort
        print("Using simulation mode as fallback")
        return self.simulation.search_tweets(query, max_results)
```

## 🚀 **Quick Start Guide**

### **Step 1: Choose API Provider**
```bash
# For TwitterAPI.io (recommended)
export TWITTER_API_KEY="your_twitterapi_io_key"
export TWITTER_API_TYPE="twitterapi_io"

# For Official Twitter API
export TWITTER_BEARER_TOKEN="your_bearer_token"
export TWITTER_API_TYPE="official"
```

### **Step 2: Update Configuration**
```python
# In enhanced_realtime_server.py
def initialize_twitter_service():
    global twitter_service
    
    api_key = os.getenv('TWITTER_API_KEY') or os.getenv('TWITTER_BEARER_TOKEN')
    api_type = os.getenv('TWITTER_API_TYPE', 'twitterapi_io')
    
    twitter_service = TwitterIntegrationService(
        api_key=api_key,
        api_type=api_type,
        simulation_mode=not api_key
    )
```

### **Step 3: Test Integration**
```bash
# Test API connection
curl "https://your-api-domain.com/health"

# Start streaming
curl -X POST "https://your-api-domain.com/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 30}'

# Check live tweets
curl "https://your-api-domain.com/tweets/live?limit=10"
```

### **Step 4: Monitor Usage**
```bash
# Check system stats
curl "https://your-api-domain.com/stats"

# Monitor API usage
tail -f /var/log/disaster-triage/api.log
```

## 📈 **Performance Optimization**

### **1. Caching Strategy**
- Cache API responses for 5 minutes
- Use Redis for distributed caching
- Implement cache warming for popular queries

### **2. Rate Limiting**
- Respect API rate limits
- Implement exponential backoff
- Use circuit breaker pattern

### **3. Data Processing**
- Batch process tweets for efficiency
- Use async/await for concurrent requests
- Implement data deduplication

## 🔒 **Security Best Practices**

### **1. API Key Management**
- Store keys in environment variables
- Use secret management services
- Rotate keys regularly
- Monitor for unauthorized usage

### **2. Data Privacy**
- Only store necessary tweet data
- Implement data retention policies
- Anonymize personal information
- Comply with GDPR/CCPA requirements

### **3. Access Control**
- Implement API authentication
- Use HTTPS for all communications
- Log all API access
- Monitor for suspicious activity

## 📞 **Support & Troubleshooting**

### **Common Issues**

1. **API Key Invalid**
   ```bash
   # Check key format and permissions
   curl -H "Authorization: Bearer $TWITTER_API_KEY" \
     "https://api.twitterapi.io/v2/tweets/search/recent?query=test"
   ```

2. **Rate Limit Exceeded**
   ```python
   # Implement retry logic
   import time
   from functools import wraps
   
   def retry_on_rate_limit(max_retries=3):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               for attempt in range(max_retries):
                   try:
                       return func(*args, **kwargs)
                   except RateLimitError:
                       wait_time = 2 ** attempt
                       time.sleep(wait_time)
               raise Exception("Max retries exceeded")
           return wrapper
       return decorator
   ```

3. **No Data Returned**
   ```python
   # Check query syntax and filters
   def validate_query(query):
       # Ensure query is not too restrictive
       if len(query.split()) > 10:
           return "Query too complex"
       
       # Check for required keywords
       disaster_keywords = ['earthquake', 'fire', 'flood', 'emergency']
       if not any(kw in query.lower() for kw in disaster_keywords):
           return "Query may be too broad"
       
       return "Valid"
   ```

### **Getting Help**
- **TwitterAPI.io Support**: https://twitterapi.io/contact
- **Twitter Developer Support**: https://developer.twitter.com/en/support
- **System Documentation**: Check `/docs` endpoint
- **Community Forums**: Developer communities and Stack Overflow

---

This implementation guide provides everything needed to transition from simulation mode to real Twitter API integration. The system is designed to be flexible and can work with multiple API providers while maintaining reliability through fallback mechanisms.

