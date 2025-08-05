# Real-Time Disaster Tweet Triage System

## 🚀 Project Overview

This project implements a real-time disaster tweet triage system designed to help emergency agencies quickly identify and prioritize on-the-ground reports from social media. It leverages machine learning for tweet classification, integrates with Twitter APIs for real-time data, and visualizes disaster locations on an interactive heatmap dashboard.

## ✨ Features

-   **Machine Learning Classification**: Utilizes a trained model (Logistic Regression with TF-IDF) to classify tweets as disaster-related or not, achieving an F1 Score of 75.9%.
-   **Real-Time Twitter Integration**: Supports both simulated tweet data and real-time streaming from Twitter APIs (TwitterAPI.io or Official Twitter API v2).
-   **Priority Scoring**: A multi-factor algorithm that assigns a priority score to each disaster tweet based on ML confidence, urgency keywords, location data, and action-oriented terms.
-   **Geolocation & Heatmap**: Extracts geographic coordinates from tweets and visualizes disaster hotspots on an interactive Leaflet.js heatmap, with priority-based color coding and dynamic sizing.
-   **FastAPI Backend**: A high-performance Python API for tweet processing, classification, streaming management, and data delivery to the frontend.
-   **React Frontend Dashboard**: A modern, responsive web interface for real-time monitoring of high-priority alerts, displaying tweet details, and interacting with the heatmap.
-   **Dynamic Configuration**: Ability to switch between simulation and real Twitter API modes at runtime without restarting the server.
-   **Comprehensive Documentation**: Detailed guides for setup, API integration, deployment, and troubleshooting.

## 🌐 Live Demo

-   **Dashboard**: [https://bngmhxsg.manus.space](https://bngmhxsg.manus.space)
-   **API Endpoint**: [https://8003-i30427mxkxuydow12jlnz-d351187c.manusvm.computer](https://8003-i30427mxkxuydow12jlnz-d351187c.manusvm.computer)
    -   API Documentation: [https://8003-i30427mxkxuydow12jlnz-d351187c.manusvm.computer/docs](https://8003-i30427mxkxuydow12jlnz-d351187c.manusvm.computer/docs)

## 🚀 Getting Started (Startup Guide)

This guide will help you set up and run the system on your local machine. You can choose to run it in **Simulation Mode** (no API keys needed) or **Real Twitter API Mode**.

### Prerequisites

Make sure you have the following installed:
-   **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
-   **Node.js 18+**: [Download Node.js](https://nodejs.org/en/download/)
-   **Git**: [Download Git](https://git-scm.com/downloads)

### Step 1: Clone the Repository (or Extract Archive)

If you received a `.tar.gz` archive, extract it to your desired project directory. Otherwise, clone the repository:

```bash
git clone <repository_url> # Replace with actual repo URL if available
cd real-time-disaster-triage
```

### Step 2: Install Python Dependencies (Backend)

Navigate to the project root and install the required Python packages:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn nltk requests tweepy python-multipart

# Download NLTK data (run this once)
python -c "import nltk; nltk.download(\'punkt\'); nltk.download(\'stopwords\')"
```

### Step 3: Install Node.js Dependencies (Frontend)

Navigate into the `disaster-heatmap-dashboard` directory and install Node.js packages:

```bash
cd disaster-heatmap-dashboard
npm install

# Go back to the project root
cd ..
```

### Step 4: Run the System

Open **two separate terminal windows**.

#### Terminal 1: Start the Backend API

In the project root directory, run:

```bash
python3.11 enhanced_realtime_server_with_real_api.py
```

This will start the FastAPI server, by default on `http://localhost:8003`. It will initially run in **Simulation Mode**.

#### Terminal 2: Start the Frontend Dashboard

In the `disaster-heatmap-dashboard` directory, run:

```bash
npm run dev
```

This will start the React development server, by default on `http://localhost:5173`.

### Step 5: Access the System

Open your web browser and navigate to:

-   **Dashboard**: `http://localhost:5173`
-   **API Documentation**: `http://localhost:8003/docs`

You should see the dashboard displaying simulated disaster tweets and an interactive heatmap.

## ⚙️ Configuration (Real Twitter API)

To switch from **Simulation Mode** to **Real Twitter API Mode**, you\'ll need API credentials. We recommend **TwitterAPI.io** for its cost-effectiveness and ease of use.

### Get API Credentials

**Option A: TwitterAPI.io (Recommended)**
1.  Visit [https://twitterapi.io/pricing](https://twitterapi.io/pricing).
2.  Sign up and add some credits (e.g., $5-10).
3.  Generate an API key from your dashboard.

**Option B: Official Twitter API v2**
1.  Apply for a developer account at [https://developer.twitter.com](https://developer.twitter.com).
2.  Once approved, create an app and obtain your Bearer Token, API Key, and API Secret.

### Configure the System

You can configure the API credentials using environment variables or at runtime via an API endpoint.

#### Method 1: Using Environment Variables (Recommended for persistent setup)

Create a `.env` file in your project root directory (next to `enhanced_realtime_server_with_real_api.py`):

```dotenv
# .env file

# For TwitterAPI.io
TWITTER_API_KEY="your_twitterapi_io_key_here"
TWITTER_API_TYPE="twitterapi_io"

# For Official Twitter API (uncomment and replace if using)
# TWITTER_BEARER_TOKEN="your_bearer_token_here"
# TWITTER_API_KEY="your_official_api_key_here"
# TWITTER_API_SECRET="your_official_api_secret_here"
# TWITTER_API_TYPE="official"

SIMULATION_MODE="false" # Set to "true" to revert to simulation mode

# Optional: Configure streaming interval and max tweets
STREAM_INTERVAL=30 # Seconds between API calls for streaming
MAX_TWEETS_PER_REQUEST=50 # Max tweets to fetch per API call
```

Then, load these environment variables before starting the backend server. For example, using `source .env` in your terminal or a tool like `dotenv` in Python.

#### Method 2: Runtime Configuration via API

Start the backend server in simulation mode first, then use the `/api/configure` endpoint:

```bash
# Start the backend server (if not already running)
python3.11 enhanced_realtime_server_with_real_api.py

# Configure for TwitterAPI.io
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d \'{
    "api_key": "your_twitterapi_io_key_here",
    "api_type": "twitterapi_io"
  }\'

# Or configure for Official Twitter API
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d \'{
    "bearer_token": "your_bearer_token_here",
    "api_key": "your_official_api_key_here",
    "api_secret": "your_official_api_secret_here",
    "api_type": "official"
  }\'

# To switch back to simulation mode
curl -X POST "http://localhost:8003/api/configure" \
  -H "Content-Type: application/json" \
  -d \'{
    "api_type": "simulation"
  }\'
```

### Verify Real API is Working

Check the health endpoint after configuration:

```bash
curl http://localhost:8003/health | jq .
```

Look for `


    "mode": "real_api"` in the `twitter_service` section.

## 🧪 Testing and Verification

### Test Real vs Simulation Mode

-   **Simulation Mode Indicators**:
    -   `"simulation": true` in tweet data
    -   `"mode": "simulation"` in health check (`/health` endpoint)
    -   Tweet IDs start with `sim_`
-   **Real API Mode Indicators**:
    -   `"simulation": false` in tweet data
    -   `"mode": "real_api"` in health check
    -   Real Twitter user IDs and timestamps
    -   `"source": "twitterapi_io"` or `"source": "official_api"`

### Test Commands

```bash
# Check current mode
curl "http://localhost:8003/health" | jq ".twitter_service.mode"

# Search for tweets and check source (replace query as needed)
curl "http://localhost:8003/tweets/search?query=earthquake%20OR%20fire&max_results=5" | jq ".tweets[0].source"

# Start streaming and monitor
curl -X POST "http://localhost:8003/streaming/start" \
  -H "Content-Type: application/json" \
  -d \'{"enabled": true, "interval": 30}\'

# Wait for a moment (e.g., 35 seconds) and check for new tweets
sleep 35
curl "http://localhost:8003/tweets/live?limit=3" | jq ".tweets[0]"
```

## 💰 Cost Management

### TwitterAPI.io Cost Estimation

-   **Rate**: $0.15 per 1,000 tweets
-   **Example**: 10,000 tweets/month = $1.50

### Usage Monitoring

The system includes built-in cost tracking. Check the `/stats` endpoint:

```bash
curl "http://localhost:8003/stats" | jq .
```

## 🔒 Security Best Practices

-   **API Key Management**: Never commit API keys to version control. Use environment variables or secure vaults. Rotate keys regularly.
-   **Access Control**: CORS is configured for frontend access. Consider implementing further access restrictions in production.
-   **HTTPS**: Always use HTTPS in production environments for secure communication.

## 🚨 Troubleshooting

### Common Issues

-   **"Twitter service not initialized"**: Ensure the backend server is running and initialized correctly.
-   **"API Key invalid"**: Double-check your API credentials. Test them directly with `curl` commands against the API provider.
-   **"No real tweets returned"**: Verify you are not in simulation mode and your API configuration is correct. Try a broader search query.
-   **"Rate limit exceeded"**: The system has built-in retry logic and fallback to simulation. Consider increasing `STREAM_INTERVAL` or reducing `MAX_TWEETS_PER_REQUEST`.

For more detailed troubleshooting, refer to the `UPDATED_RUN_GUIDE.md` and `REAL_TWITTER_API_SETUP_GUIDE.md` files.

## 📊 Monitoring & Analytics

-   **Backend Logs**: The backend server prints detailed logs to the console, including API requests, tweet processing status, and errors.
-   **Frontend Logs**: Use your browser\'s developer tools (F12) to inspect console messages and network requests.
-   **System Endpoints**: Utilize `/health`, `/stats`, and `/streaming/status` endpoints for real-time system monitoring.

## 📦 Deployment

The system is designed for easy deployment:

-   **Local Production**: Instructions are available in `UPDATED_RUN_GUIDE.md`.
-   **Docker**: A `Dockerfile` can be created for containerized deployment.
-   **Cloud Platforms**: The FastAPI backend and React frontend can be deployed independently to platforms like Heroku, AWS, Google Cloud, Vercel, or Netlify.

## 📚 Further Documentation

-   `FINAL_SYSTEM_DOCUMENTATION.md`: Comprehensive technical overview and user guide.
-   `TWITTER_API_IMPLEMENTATION_GUIDE.md`: Detailed guide on integrating various Twitter APIs.
-   `REAL_TWITTER_API_SETUP_GUIDE.md`: Specific setup instructions for real Twitter API integration.
-   `UPDATED_RUN_GUIDE.md`: Detailed guide on running the system with all modes.
-   `SETUP_AND_RUN_GUIDE.md`: Original setup guide for simulation mode.
-   `HEATMAP_FEATURES.md`: Details on the interactive heatmap features.

## 🙏 Acknowledgements

-   Kaggle for the 


NLP with Disaster Tweets dataset.
-   FastAPI, React, Leaflet.js, and other open-source libraries for building this system.

---

