# Updated Run Guide - Disaster Tweet Triage System with Real Twitter API

## 🚀 **System Overview**

The disaster tweet triage system now includes **real Twitter API integration** alongside the existing simulation mode. You can run the system in three modes:

1. **Simulation Mode** (Default) - Uses realistic simulated tweets
2. **TwitterAPI.io Mode** - Uses real Twitter data via TwitterAPI.io ($0.15/1K tweets)
3. **Official Twitter API Mode** - Uses official Twitter API v2 (requires Pro tier)

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.11+** - Download from [python.org](https://python.org)
- **Node.js 18+** - Download from [nodejs.org](https://nodejs.org)
- **Git** - Download from [git-scm.com](https://git-scm.com)

### **New Dependencies**
```bash
# Install additional Python packages for real API support
pip install tweepy fastapi uvicorn pandas numpy scikit-learn nltk requests python-multipart
```

## 🏃‍♂️ **Running the System**

### **Option 1: Simulation Mode (No API Key Required)**

This is the default mode and works immediately without any API keys.

#### **Terminal 1: Start Enhanced Backend**
```bash
# Navigate to project directory
cd disaster-tweet-system

# Start the enhanced server with real API support
python3.11 enhanced_realtime_server_with_real_api.py
```

#### **Terminal 2: Start Frontend Dashboard**
```bash
# Navigate to React app directory
cd disaster-heatmap-dashboard

# Update API endpoint to use new server
# Edit src/App.jsx and change API_BASE_URL to:
# const API_BASE_URL = 'http://localhost:8003';

# Start the development server
npm run dev
```

#### **Access the System**
- **Dashboard**: http://localhost:5173
- **Enhanced API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs

### **Option 2: Real Twitter API Mode**

#### **Step 1: Get API Credentials**

**For TwitterAPI.io (Recommended):**
1. Visit https://twitterapi.io/pricing
2. Sign up and add $5-10 in credits
3. Generate API key from dashboard

**For Official Twitter API:**
1. Apply at https://developer.twitter.com
2. Get approved (can take weeks)
3. Create app and get Bearer Token

#### **Step 2: Configure Environment Variables**

```bash
# For TwitterAPI.io
export TWITTER_API_KEY="your_twitterapi_io_key_here"
export TWITTER_API_TYPE="twitterapi_io"
export SIMULATION_MODE="false"

# For Official Twitter API
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
export TWITTER_API_TYPE="official"
export SIMULATION_MODE="false"
```

#### **Step 3: Start the System**

```bash
# Terminal 1: Start enhanced backend with real API
python3.11 enhanced_realtime_server_with_real_api.py

# Terminal 2: Start frontend (same as before)
cd disaster-heatmap-dashboard
npm run dev
```

#### **Step 4: Verify Real API is Working**

```bash
# Check system health
curl http://localhost:8003/health

# Should show "mode": "real_api" instead of "simulation"
```

## 🌐 **New API Endpoints**

The enhanced system includes new endpoints for real Twitter integration:

### **Configuration Endpoints**
```bash
# Configure API credentials at runtime
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "api_type": "twitterapi_io"
  }'

# Check current configuration
curl "http://localhost:8003/health"
```

### **Real Tweet Search**
```bash
# Search for real tweets
curl "http://localhost:8003/tweets/search?query=earthquake%20OR%20fire&max_results=10"

# Get live disaster tweets
curl "http://localhost:8003/tweets/live?limit=10"
```

### **Enhanced Streaming**
```bash
# Start real-time streaming
curl -X POST "http://localhost:8003/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 60}'

# Check streaming status
curl "http://localhost:8003/streaming/status"

# Stop streaming
curl -X POST "http://localhost:8003/streaming/stop"
```

### **System Statistics**
```bash
# Get comprehensive stats including API usage
curl "http://localhost:8003/stats"
```

## 🔧 **Configuration Options**

### **Environment Variables**

Create a `.env` file in your project root:

```bash
# API Configuration
TWITTER_API_KEY=your_api_key_here
TWITTER_API_TYPE=twitterapi_io  # or "official"
SIMULATION_MODE=false           # Set to "true" for simulation

# System Configuration
LOG_LEVEL=INFO
STREAM_INTERVAL=60             # Seconds between API calls
MAX_TWEETS_PER_REQUEST=100     # Tweets per API call
DAILY_BUDGET=50.00             # Daily spending limit (USD)
```

### **Runtime Configuration**

You can switch between modes without restarting the server:

```bash
# Switch to real API
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_key", "api_type": "twitterapi_io"}'

# Switch back to simulation
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{"api_type": "simulation"}'
```

## 🧪 **Testing Real vs Simulation Mode**

### **Simulation Mode Indicators**
- `"simulation": true` in tweet data
- `"mode": "simulation"` in health check
- Tweet IDs start with "sim_"
- Consistent, predictable data

### **Real API Mode Indicators**
- `"simulation": false` in tweet data
- `"mode": "real_api"` in health check
- Real Twitter user IDs and timestamps
- `"source": "twitterapi_io"` or `"source": "official_api"`
- Actual tweet content from Twitter

### **Test Commands**

```bash
# Check current mode
curl "http://localhost:8003/health" | jq '.twitter_service.mode'

# Search for tweets and check source
curl "http://localhost:8003/tweets/search?query=earthquake&max_results=5" | jq '.tweets[0].source'

# Start streaming and monitor
curl -X POST "http://localhost:8003/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 30}'

# Wait and check for new tweets
sleep 35
curl "http://localhost:8003/tweets/live?limit=3" | jq '.tweets[0]'
```

## 💰 **Cost Management**

### **TwitterAPI.io Costs**
- **Rate**: $0.15 per 1,000 tweets
- **Example**: 10,000 tweets/month = $1.50
- **Monitoring**: Built-in cost tracking in `/stats` endpoint

### **Usage Monitoring**
```bash
# Check daily usage and costs
curl "http://localhost:8003/stats" | jq '.usage'

# Monitor in real-time
watch -n 30 'curl -s "http://localhost:8003/health" | jq ".api_usage"'
```

## 🔄 **Switching Between Modes**

### **Quick Mode Switching**

```bash
# Function to switch modes quickly
switch_to_simulation() {
  curl -X POST "http://localhost:8003/api/configure" \
    -H "Content-Type: application/json" \
    -d '{"api_type": "simulation"}'
}

switch_to_real_api() {
  curl -X POST "http://localhost:8003/api/configure" \
    -H "Content-Type: application/json" \
    -d '{"api_key": "'$TWITTER_API_KEY'", "api_type": "twitterapi_io"}'
}

# Usage
switch_to_simulation
switch_to_real_api
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. "Twitter service not initialized" Error**
```bash
# Check if server is running
curl http://localhost:8003/health

# Restart the server
pkill -f enhanced_realtime_server_with_real_api.py
python3.11 enhanced_realtime_server_with_real_api.py
```

#### **2. API Key Invalid**
```bash
# Test API key directly
curl -H "Authorization: Bearer $TWITTER_API_KEY" \
  "https://api.twitterapi.io/v2/tweets/search/recent?query=test&max_results=1"

# Reconfigure via API
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_correct_key", "api_type": "twitterapi_io"}'
```

#### **3. No Real Tweets Returned**
```bash
# Check if in simulation mode
curl "http://localhost:8003/health" | jq '.twitter_service.mode'

# Verify API configuration
curl "http://localhost:8003/health" | jq '.twitter_service'

# Test with broader query
curl "http://localhost:8003/tweets/search?query=the&max_results=5"
```

#### **4. Rate Limit Exceeded**
```bash
# Check usage stats
curl "http://localhost:8003/stats" | jq '.usage'

# Reduce streaming frequency
curl -X POST "http://localhost:8003/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 120}'  # 2 minutes instead of 1
```

### **Fallback Behavior**

The system automatically falls back to simulation mode if:
- API credentials are invalid
- Rate limits are exceeded
- Network connectivity issues
- API service is down

## 📊 **Monitoring & Analytics**

### **Real-time Monitoring**

```bash
# Monitor system health
watch -n 10 'curl -s "http://localhost:8003/health" | jq "{mode: .twitter_service.mode, streaming: .streaming.active, cache: .cache.tweets_cached}"'

# Monitor API costs
watch -n 60 'curl -s "http://localhost:8003/stats" | jq ".usage"'

# Monitor tweet flow
watch -n 30 'curl -s "http://localhost:8003/tweets/live?limit=1" | jq "{total: .total_available, last_update: .last_update}"'
```

### **Dashboard Integration**

The frontend dashboard automatically detects and displays:
- Current API mode (simulation vs real)
- Real-time status indicators
- API usage statistics
- Cost tracking (when using paid APIs)

## 🎯 **Production Deployment**

### **Environment Setup**

```bash
# Production environment variables
export ENVIRONMENT=production
export TWITTER_API_KEY="prod_api_key"
export TWITTER_API_TYPE="twitterapi_io"
export SIMULATION_MODE="false"
export LOG_LEVEL="WARNING"
export DAILY_BUDGET="100.00"
```

### **Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install tweepy fastapi uvicorn pandas numpy scikit-learn nltk requests python-multipart
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

EXPOSE 8003
CMD ["python", "enhanced_realtime_server_with_real_api.py"]
```

```bash
# Build and run
docker build -t disaster-triage-real-api .
docker run -p 8003:8003 \
  -e TWITTER_API_KEY="your_key" \
  -e TWITTER_API_TYPE="twitterapi_io" \
  -e SIMULATION_MODE="false" \
  disaster-triage-real-api
```

## 📈 **Performance Optimization**

### **Caching Strategy**
- Tweet cache: 100 most recent tweets in memory
- API response caching: 5-minute TTL
- Geolocation cache: Persistent city coordinates

### **Batch Processing**
- Default: 50 tweets per API call
- Configurable via `MAX_TWEETS_PER_REQUEST`
- Automatic batching for efficiency

### **Rate Limit Management**
- Intelligent retry with exponential backoff
- Automatic fallback to simulation mode
- Request queuing during rate limits

## 🔐 **Security Considerations**

### **API Key Security**
- Never commit API keys to version control
- Use environment variables or secure vaults
- Rotate keys regularly
- Monitor for unauthorized usage

### **Access Control**
- CORS configured for frontend access
- Rate limiting on API endpoints
- Input validation and sanitization
- HTTPS in production environments

## 📞 **Getting Help**

### **System Health Checks**
```bash
# Comprehensive health check
curl "http://localhost:8003/health" | jq '.'

# API documentation
open http://localhost:8003/docs

# System statistics
curl "http://localhost:8003/stats" | jq '.'
```

### **Support Resources**
- **TwitterAPI.io Support**: https://twitterapi.io/contact
- **Twitter Developer Support**: https://developer.twitter.com/en/support
- **System Documentation**: Available at `/docs` endpoint

---

## ✅ **Quick Start Checklist**

### **For Simulation Mode (Immediate)**
- [ ] Install Python dependencies: `pip install tweepy fastapi uvicorn pandas numpy scikit-learn nltk requests`
- [ ] Start backend: `python3.11 enhanced_realtime_server_with_real_api.py`
- [ ] Start frontend: `cd disaster-heatmap-dashboard && npm run dev`
- [ ] Access dashboard: http://localhost:5173

### **For Real API Mode**
- [ ] Choose API provider (TwitterAPI.io recommended)
- [ ] Get API credentials
- [ ] Set environment variables
- [ ] Start system with real API configuration
- [ ] Verify real data is flowing
- [ ] Monitor usage and costs

The enhanced system provides a seamless transition from simulation to real Twitter data, enabling genuine disaster monitoring capabilities while maintaining cost control and reliability through intelligent fallback mechanisms.

