# How to Run the Disaster Tweet Triage System

## 🚀 **Quick Start Guide**

This guide will help you set up and run the complete disaster tweet triage system on your local machine.

## 📋 **Prerequisites**

### **Required Software**
1. **Python 3.11+** - Download from [python.org](https://python.org)
2. **Node.js 18+** - Download from [nodejs.org](https://nodejs.org)
3. **Git** - Download from [git-scm.com](https://git-scm.com)
4. **VS Code** (optional) - Download from [code.visualstudio.com](https://code.visualstudio.com)

### **Check Your Installation**
```bash
# Check Python version
python --version  # or python3 --version
# Should show Python 3.11 or higher

# Check Node.js version
node --version
# Should show v18.0.0 or higher

# Check npm version
npm --version
# Should show 8.0.0 or higher
```

## 📁 **Project Setup**

### **Step 1: Extract the Project**
1. Download the `disaster-tweet-triage-system.tar.gz` file
2. Extract it to a folder (e.g., `~/disaster-tweet-system/`)
3. Open terminal/command prompt in that folder

### **Step 2: Install Python Dependencies**
```bash
# Navigate to project directory
cd disaster-tweet-system

# Install required Python packages
pip install fastapi uvicorn pandas numpy scikit-learn nltk requests python-multipart

# Alternative: Install with pip3 if needed
pip3 install fastapi uvicorn pandas numpy scikit-learn nltk requests python-multipart

# Download NLTK data (run this once)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### **Step 3: Install Frontend Dependencies**
```bash
# Navigate to React app directory
cd disaster-heatmap-dashboard

# Install Node.js dependencies
npm install

# Alternative: Use yarn if you prefer
# yarn install

# Go back to project root
cd ..
```

## 🏃‍♂️ **Running the System**

### **Method 1: Run Both Components Separately (Recommended)**

#### **Terminal 1: Start the Backend API**
```bash
# In project root directory
python enhanced_realtime_server.py

# Alternative if python doesn't work
python3 enhanced_realtime_server.py
```

You should see output like:
```
✅ Loaded trained disaster classification model
✅ Twitter integration service initialized
🚀 Real-time disaster tweet triage API started successfully
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
```

#### **Terminal 2: Start the Frontend Dashboard**
```bash
# In a new terminal, navigate to React app
cd disaster-heatmap-dashboard

# Start the development server
npm run dev

# Alternative commands
# npm start
# yarn dev
```

You should see output like:
```
VITE v6.3.5  ready in 488 ms
➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.100:5173/
```

### **Method 2: Production Build**

#### **Build the Frontend**
```bash
cd disaster-heatmap-dashboard
npm run build
cd ..
```

#### **Serve Static Files (Optional)**
```bash
# Install a simple HTTP server
npm install -g serve

# Serve the built files
serve -s disaster-heatmap-dashboard/dist -l 3000
```

## 🌐 **Accessing the System**

### **Dashboard (Frontend)**
- **URL**: http://localhost:5173 (development) or http://localhost:3000 (production)
- **Features**: Real-time disaster tweets, interactive heatmap, priority alerts

### **API Backend**
- **URL**: http://localhost:8002
- **Health Check**: http://localhost:8002/health
- **API Documentation**: http://localhost:8002/docs
- **Live Tweets**: http://localhost:8002/tweets/live

## 🔧 **Configuration Options**

### **Environment Variables (Optional)**
Create a `.env` file in the project root:

```bash
# .env file
TWITTER_API_KEY=your_api_key_here
TWITTER_API_TYPE=twitterapi_io
SIMULATION_MODE=true
LOG_LEVEL=INFO
STREAM_INTERVAL=30
MAX_TWEETS=100
```

### **API Configuration**
Edit `enhanced_realtime_server.py` to change:
- **Port**: Change `port=8002` to your preferred port
- **Host**: Change `host="0.0.0.0"` if needed
- **CORS**: Modify allowed origins in CORS middleware

### **Frontend Configuration**
Edit `disaster-heatmap-dashboard/src/App.jsx`:
- **API URL**: Change `API_BASE_URL` to match your backend
- **Refresh Interval**: Modify the 30-second auto-refresh timer
- **Map Settings**: Adjust default map center and zoom

## 🧪 **Testing the System**

### **1. Test Backend API**
```bash
# Check health
curl http://localhost:8002/health

# Start streaming
curl -X POST "http://localhost:8002/streaming/start" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval": 30}'

# Get live tweets
curl http://localhost:8002/tweets/live?limit=10

# Test single prediction
curl -X POST "http://localhost:8002/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT: Major earthquake hits downtown area!", "location": "San Francisco, CA"}'
```

### **2. Test Frontend Dashboard**
1. Open http://localhost:5173 in your browser
2. You should see the disaster tweet dashboard
3. Click the "Refresh" button to load tweets
4. Interact with the heatmap by clicking on circles
5. Check that alerts appear with priority colors

### **3. Test Real-time Features**
1. Start the streaming via API or dashboard
2. Wait 30 seconds for new tweets to appear
3. Verify the "Last Update" timestamp changes
4. Check that the "Live" badge appears when streaming is active

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Python Import Errors**
```bash
# If you get import errors, install missing packages
pip install package_name

# For NLTK errors
python -c "import nltk; nltk.download('all')"

# For sklearn errors
pip install scikit-learn==1.3.0
```

#### **Node.js/npm Errors**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Use different Node version if needed
nvm use 18  # if you have nvm installed
```

#### **Port Already in Use**
```bash
# Find what's using the port
lsof -i :8002  # for backend
lsof -i :5173  # for frontend

# Kill the process
kill -9 PID_NUMBER

# Or use different ports in the configuration
```

#### **CORS Errors**
If you see CORS errors in the browser console:
1. Make sure the backend is running on http://localhost:8002
2. Check that the frontend API_BASE_URL matches the backend URL
3. Verify CORS is enabled in `enhanced_realtime_server.py`

#### **Model Loading Errors**
```bash
# If model files are missing, regenerate them
python fix_model_loading.py

# Check if files exist
ls -la *.pkl
# Should show: disaster_model.pkl, tfidf_vectorizer.pkl
```

### **Performance Issues**

#### **Slow Loading**
- Reduce the number of tweets loaded: Edit `max_results` parameters
- Increase refresh intervals: Change from 30s to 60s or more
- Use production build for frontend: `npm run build`

#### **High Memory Usage**
- Limit tweet cache size in `enhanced_realtime_server.py`
- Reduce model complexity if needed
- Close unused browser tabs

## 🔄 **Development Workflow**

### **Making Changes**

#### **Backend Changes**
1. Edit Python files (`enhanced_realtime_server.py`, `twitter_integration.py`)
2. Restart the backend server (Ctrl+C, then run again)
3. Test changes via API endpoints

#### **Frontend Changes**
1. Edit React files in `disaster-heatmap-dashboard/src/`
2. Changes auto-reload in development mode
3. For production: `npm run build` and restart server

#### **Model Changes**
1. Edit `fix_model_loading.py` to modify ML model
2. Run `python fix_model_loading.py` to retrain
3. Restart backend to load new model

### **Adding Features**

#### **New API Endpoints**
1. Add new routes in `enhanced_realtime_server.py`
2. Follow FastAPI patterns for request/response models
3. Update API documentation

#### **New Dashboard Components**
1. Create new React components in `disaster-heatmap-dashboard/src/components/`
2. Import and use in `App.jsx`
3. Add styling with Tailwind CSS classes

## 📦 **Deployment Options**

### **Local Production**
```bash
# Build frontend
cd disaster-heatmap-dashboard
npm run build

# Serve with Python
cd ..
python -m http.server 3000 --directory disaster-heatmap-dashboard/dist

# Run backend in production mode
python enhanced_realtime_server.py
```

### **Docker Deployment (Advanced)**
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install fastapi uvicorn pandas numpy scikit-learn nltk requests
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

EXPOSE 8002
CMD ["python", "enhanced_realtime_server.py"]
```

Build and run:
```bash
docker build -t disaster-triage .
docker run -p 8002:8002 disaster-triage
```

### **Cloud Deployment**
- **Heroku**: Use `Procfile` and `requirements.txt`
- **AWS**: Deploy with Elastic Beanstalk or EC2
- **Google Cloud**: Use App Engine or Cloud Run
- **Vercel/Netlify**: For frontend static deployment

## 📊 **Monitoring & Logs**

### **Backend Logs**
The backend server prints logs to console:
- API requests and responses
- Tweet processing status
- Error messages and stack traces
- Performance metrics

### **Frontend Logs**
Open browser Developer Tools (F12):
- Console tab: JavaScript errors and debug messages
- Network tab: API requests and responses
- Application tab: Local storage and cache

### **System Monitoring**
- **API Health**: http://localhost:8002/health
- **System Stats**: http://localhost:8002/stats
- **Streaming Status**: http://localhost:8002/streaming/status

## 🎯 **Next Steps**

### **Immediate Actions**
1. **Run the system** following the steps above
2. **Test all features** to ensure everything works
3. **Explore the code** in VS Code to understand the implementation
4. **Try the API endpoints** using the provided curl commands

### **Customization Ideas**
1. **Add new disaster types** to the classification model
2. **Integrate real Twitter API** using the provided guide
3. **Add email/SMS alerts** for critical disasters
4. **Create mobile app** using React Native
5. **Add more data sources** (news APIs, government feeds)

### **Production Deployment**
1. **Set up real Twitter API** access
2. **Deploy to cloud platform** (AWS, Google Cloud, etc.)
3. **Add monitoring and alerting**
4. **Implement user authentication**
5. **Scale for high traffic**

## 📞 **Getting Help**

If you encounter issues:

1. **Check the logs** in terminal/console for error messages
2. **Verify prerequisites** are installed correctly
3. **Check port availability** (8002 for backend, 5173 for frontend)
4. **Review this guide** for troubleshooting steps
5. **Test individual components** (API first, then frontend)

The system is designed to be robust and should work out of the box with the provided instructions. Happy coding! 🚀

