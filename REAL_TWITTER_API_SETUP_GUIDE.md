# Real Twitter API Integration Setup Guide

## 🎯 **Overview**

This guide provides step-by-step instructions to integrate real Twitter API access into your disaster tweet triage system. The system currently runs in simulation mode but can be easily upgraded to use live Twitter data.

## 🔑 **API Options & Costs**

### **Option 1: TwitterAPI.io (Recommended)**

#### **Why TwitterAPI.io?**
- ✅ **Cost-effective**: $0.15 per 1,000 tweets
- ✅ **No minimum spend**: Pay only for what you use
- ✅ **Easy setup**: Simple API key authentication
- ✅ **Real-time access**: No rate limits (QPS based)
- ✅ **Comprehensive data**: Full tweet metadata

#### **Pricing**
- **Cost**: $0.15 per 1,000 tweets
- **Example**: 10,000 tweets/month = $1.50
- **Example**: 100,000 tweets/month = $15.00
- **Payment**: Credit-based system, 1 USD = 100,000 credits

#### **Setup Steps**

1. **Sign up for TwitterAPI.io**
   - Visit: https://twitterapi.io/pricing
   - Sign in with Google account
   - Add credits to your account (minimum $1)

2. **Get API Key**
   - Go to Dashboard → API Keys
   - Generate new API key
   - Copy the key (keep it secure!)

3. **Configure Environment Variables**
   ```bash
   export TWITTER_API_KEY="your_twitterapi_io_key_here"
   export TWITTER_API_TYPE="twitterapi_io"
   export SIMULATION_MODE="false"
   ```

4. **Test the Integration**
   ```bash
   # Start the enhanced server
   python3.11 enhanced_realtime_server_with_real_api.py
   
   # Test API configuration
   curl -X POST "http://localhost:8003/api/configure" \
     -H "Content-Type: application/json" \
     -d '{
       "api_key": "your_twitterapi_io_key_here",
       "api_type": "twitterapi_io"
     }'
   ```

### **Option 2: Official Twitter API v2**

#### **Pricing Tiers**

**Free Tier ($0/month)**
- ❌ 1,500 tweets/month (too limited)
- ❌ Basic endpoints only
- ❌ No streaming access

**Basic Tier ($100/month)**
- ⚠️ 10,000 tweets/month
- ✅ Full v2 endpoints
- ❌ No streaming access

**Pro Tier ($5,000/month)**
- ✅ 1M tweets/month
- ✅ Filtered stream access
- ✅ Real-time capabilities
- ✅ Enterprise features

#### **Setup Steps**

1. **Apply for Developer Account**
   - Visit: https://developer.twitter.com
   - Apply for developer access
   - Wait for approval (can take weeks)
   - Describe your use case clearly

2. **Create App and Get Credentials**
   - Developer Portal → Create App
   - Get the following credentials:
     - Bearer Token
     - API Key
     - API Secret
     - Access Token (optional)
     - Access Token Secret (optional)

3. **Configure Environment Variables**
   ```bash
   export TWITTER_BEARER_TOKEN="your_bearer_token"
   export TWITTER_API_KEY="your_api_key"
   export TWITTER_API_SECRET="your_api_secret"
   export TWITTER_API_TYPE="official"
   export SIMULATION_MODE="false"
   ```

4. **Test the Integration**
   ```bash
   # Configure via API
   curl -X POST "http://localhost:8003/api/configure" \
     -H "Content-Type: application/json" \
     -d '{
       "bearer_token": "your_bearer_token",
       "api_key": "your_api_key",
       "api_secret": "your_api_secret",
       "api_type": "official"
     }'
   ```

## 🚀 **Quick Setup Instructions**

### **Step 1: Choose Your API Provider**

For most users, we recommend **TwitterAPI.io** due to its cost-effectiveness and ease of setup.

### **Step 2: Get API Credentials**

**For TwitterAPI.io:**
1. Visit https://twitterapi.io/pricing
2. Sign up and add $5-10 in credits
3. Generate API key from dashboard

**For Official Twitter API:**
1. Apply at https://developer.twitter.com
2. Wait for approval
3. Create app and get Bearer Token

### **Step 3: Configure the System**

**Method A: Environment Variables (Recommended)**
```bash
# For TwitterAPI.io
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_TYPE="twitterapi_io"
export SIMULATION_MODE="false"

# For Official API
export TWITTER_BEARER_TOKEN="your_bearer_token"
export TWITTER_API_TYPE="official"
export SIMULATION_MODE="false"
```

**Method B: API Configuration**
```bash
# Start the server first
python3.11 enhanced_realtime_server_with_real_api.py

# Then configure via API
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "api_type": "twitterapi_io"
  }'
```

### **Step 4: Test Real API Access**

```bash
# Check system health
curl http://localhost:8003/health

# Search for real tweets
curl "http://localhost:8003/tweets/search?query=earthquake%20OR%20fire&max_results=10"

# Start real-time streaming
curl -X POST "http://localhost:8003/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 60}'

# Check live tweets
curl "http://localhost:8003/tweets/live?limit=10"
```

## 🔧 **Configuration Options**

### **Environment Variables**

```bash
# API Configuration
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# System Configuration
TWITTER_API_TYPE=twitterapi_io  # or "official"
SIMULATION_MODE=false           # Set to "true" for simulation
LOG_LEVEL=INFO
STREAM_INTERVAL=60             # Seconds between API calls
MAX_TWEETS_PER_REQUEST=100     # Tweets per API call
DAILY_BUDGET=50.00             # Daily spending limit (USD)
```

### **Runtime Configuration via API**

The system supports dynamic configuration changes without restart:

```bash
# Configure TwitterAPI.io
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_twitterapi_io_key",
    "api_type": "twitterapi_io"
  }'

# Configure Official Twitter API
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "bearer_token": "your_bearer_token",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "api_type": "official"
  }'

# Switch back to simulation mode
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "api_type": "simulation"
  }'
```

## 📊 **Cost Management**

### **TwitterAPI.io Cost Estimation**

```python
# Cost calculator
def estimate_monthly_cost(tweets_per_day):
    tweets_per_month = tweets_per_day * 30
    cost_per_1k = 0.15  # $0.15 per 1K tweets
    monthly_cost = (tweets_per_month / 1000) * cost_per_1k
    return monthly_cost

# Examples
print(f"1,000 tweets/day = ${estimate_monthly_cost(1000):.2f}/month")  # $4.50
print(f"5,000 tweets/day = ${estimate_monthly_cost(5000):.2f}/month")  # $22.50
print(f"10,000 tweets/day = ${estimate_monthly_cost(10000):.2f}/month") # $45.00
```

### **Usage Monitoring**

The system includes built-in cost tracking:

```bash
# Check usage statistics
curl "http://localhost:8003/stats"

# Monitor API usage
curl "http://localhost:8003/health" | jq '.api_usage'
```

### **Budget Controls**

Set daily spending limits in your environment:

```bash
export DAILY_BUDGET=50.00  # $50 daily limit
export ALERT_THRESHOLD=0.9  # Alert at 90% of budget
```

## 🔒 **Security Best Practices**

### **API Key Management**

1. **Never commit API keys to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*.key" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   # Create .env file
   cat > .env << EOF
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_TYPE=twitterapi_io
   SIMULATION_MODE=false
   EOF
   
   # Load environment variables
   source .env
   ```

3. **Rotate keys regularly**
   - Generate new API keys monthly
   - Revoke old keys immediately
   - Monitor for unauthorized usage

### **Access Control**

1. **Restrict API access**
   ```bash
   # Only allow specific IPs (if needed)
   export ALLOWED_IPS="192.168.1.0/24,10.0.0.0/8"
   ```

2. **Use HTTPS in production**
   ```bash
   # Enable SSL/TLS
   export USE_HTTPS=true
   export SSL_CERT_PATH=/path/to/cert.pem
   export SSL_KEY_PATH=/path/to/key.pem
   ```

## 🚨 **Error Handling & Fallbacks**

### **Automatic Fallback**

The system automatically falls back to simulation mode if:
- API credentials are invalid
- Rate limits are exceeded
- Network connectivity issues
- API service is down

### **Error Monitoring**

```bash
# Check for errors
curl "http://localhost:8003/health" | jq '.twitter_service'

# View system logs
tail -f /var/log/disaster-triage/api.log
```

### **Rate Limit Handling**

The system includes intelligent rate limit management:
- Automatic retry with exponential backoff
- Request queuing during rate limits
- Graceful degradation to simulation mode

## 📈 **Performance Optimization**

### **Caching Strategy**

```bash
# Configure caching
export CACHE_TTL=300          # 5 minutes
export MAX_CACHE_SIZE=1000    # Maximum cached tweets
export ENABLE_REDIS=true      # Use Redis for distributed caching
```

### **Batch Processing**

```bash
# Optimize API usage
export BATCH_SIZE=100         # Tweets per API call
export BATCH_INTERVAL=60      # Seconds between batches
export PARALLEL_REQUESTS=3    # Concurrent API calls
```

## 🧪 **Testing Your Setup**

### **1. Test API Connection**

```bash
# Test TwitterAPI.io
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.twitterapi.io/v2/tweets/search/recent?query=test&max_results=10"

# Test Official Twitter API
curl -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  "https://api.twitter.com/2/tweets/search/recent?query=test&max_results=10"
```

### **2. Test System Integration**

```bash
# Start the server
python3.11 enhanced_realtime_server_with_real_api.py

# Test health endpoint
curl http://localhost:8003/health

# Test search functionality
curl "http://localhost:8003/tweets/search?query=earthquake&max_results=5"

# Test streaming
curl -X POST "http://localhost:8003/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 60}'

# Wait and check results
sleep 70
curl "http://localhost:8003/tweets/live?limit=10"
```

### **3. Verify Real Data**

Look for these indicators that real API is working:
- `"simulation": false` in tweet data
- `"source": "twitterapi_io"` or `"source": "official_api"`
- Real Twitter user IDs and timestamps
- Actual tweet content (not simulated)

## 🔄 **Switching Between APIs**

### **Runtime Switching**

You can switch between API providers without restarting:

```bash
# Switch to TwitterAPI.io
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_key", "api_type": "twitterapi_io"}'

# Switch to Official API
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{"bearer_token": "your_token", "api_type": "official"}'

# Switch to simulation
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d '{"api_type": "simulation"}'
```

### **Hybrid Approach**

For maximum reliability, you can configure multiple API sources:

```bash
# Primary: TwitterAPI.io
export TWITTER_API_KEY="your_twitterapi_key"
export TWITTER_API_TYPE="twitterapi_io"

# Backup: Official API
export TWITTER_BEARER_TOKEN="your_bearer_token"
export BACKUP_API_TYPE="official"

# Fallback: Simulation
export ENABLE_SIMULATION_FALLBACK="true"
```

## 📞 **Support & Troubleshooting**

### **Common Issues**

1. **"API key invalid" error**
   ```bash
   # Check key format
   echo $TWITTER_API_KEY | wc -c  # Should be reasonable length
   
   # Test key directly
   curl -H "Authorization: Bearer $TWITTER_API_KEY" \
     "https://api.twitterapi.io/v2/tweets/search/recent?query=test&max_results=1"
   ```

2. **"Rate limit exceeded" error**
   ```bash
   # Check current limits
   curl "http://localhost:8003/stats" | jq '.usage'
   
   # Wait for reset or reduce frequency
   export STREAM_INTERVAL=120  # Increase to 2 minutes
   ```

3. **"No tweets returned" error**
   ```bash
   # Check query syntax
   curl "http://localhost:8003/tweets/search?query=earthquake%20OR%20fire&max_results=10"
   
   # Verify API is working
   curl "http://localhost:8003/health" | jq '.twitter_service'
   ```

### **Getting Help**

- **TwitterAPI.io Support**: https://twitterapi.io/contact
- **Twitter Developer Support**: https://developer.twitter.com/en/support
- **System Health Check**: `curl http://localhost:8003/health`
- **API Documentation**: http://localhost:8003/docs

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
export ENABLE_MONITORING="true"
```

### **Monitoring & Alerts**

```bash
# Set up monitoring
export WEBHOOK_URL="https://hooks.slack.com/your-webhook"
export ALERT_EMAIL="admin@yourcompany.com"
export MONITOR_INTERVAL="300"  # 5 minutes
```

### **Scaling Considerations**

- **Load Balancing**: Multiple API instances
- **Database**: PostgreSQL for persistent storage
- **Caching**: Redis for distributed caching
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK stack for log aggregation

---

## ✅ **Quick Checklist**

- [ ] Choose API provider (TwitterAPI.io recommended)
- [ ] Sign up and get API credentials
- [ ] Set environment variables
- [ ] Test API connection
- [ ] Configure the system
- [ ] Start streaming
- [ ] Verify real data is flowing
- [ ] Set up monitoring and alerts
- [ ] Deploy to production

With this setup, your disaster tweet triage system will have access to real-time Twitter data, enabling genuine emergency monitoring and response capabilities!

