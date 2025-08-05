import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { MapPin, AlertTriangle, Clock, TrendingUp, RefreshCw, Map, Wifi, WifiOff } from 'lucide-react'
import DisasterHeatmap from './components/DisasterHeatmap.jsx'
import './App.css'

function App() {
  const [tweets, setTweets] = useState([])
  const [selectedTweet, setSelectedTweet] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [streamingActive, setStreamingActive] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')

  // API configuration
  const API_BASE_URL = 'http://localhost:8002'

  // Fetch live tweets from the API
  const fetchLiveTweets = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tweets/live?limit=2000`)
      if (response.ok) {
        const data = await response.json()
        setStreamingActive(data.streaming_active || false)
        return data.tweets || []
      } else {
        console.error('Failed to fetch live tweets:', response.status)
        return []
      }
    } catch (error) {
      console.error('Error fetching live tweets:', error)
      return []
    }
  }

  // Start streaming if not already active
  const startStreaming = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/streaming/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enabled: true,
          interval: 30,
          max_tweets: 2000
        })
      })
      
      if (response.ok) {
        console.log('✅ Real-time streaming started')
        setStreamingActive(true)
      } else {
        console.log('ℹ️ Streaming may already be active')
      }
    } catch (error) {
      console.error('Error starting streaming:', error)
    }
  }

  // Check API health and streaming status
  const checkApiStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      if (response.ok) {
        const health = await response.json()
        setApiStatus('online')
        setStreamingActive(health.streaming?.active || false)
        return true
      } else {
        setApiStatus('offline')
        return false
      }
    } catch (error) {
      console.error('Error checking API status:', error)
      setApiStatus('offline')
      return false
    }
  }

  // Load tweets data
  const loadTweets = async () => {
    setLoading(true)
    
    // Check API status first
    const apiOnline = await checkApiStatus()
    
    if (apiOnline) {
      // Try to start streaming if not active
      if (!streamingActive) {
        await startStreaming()
      }
      
      // Fetch live tweets
      const liveTweets = await fetchLiveTweets()
      
      if (liveTweets.length > 0) {
        // Sort by priority score and add timestamps
        const sortedTweets = liveTweets
          .sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0))
          .map((tweet, index) => ({
            ...tweet,
            id: tweet.id || `tweet_${index}`,
            timestamp: tweet.created_at ? new Date(tweet.created_at) : new Date(Date.now() - Math.random() * 3600000)
          }))
        
        setTweets(sortedTweets)
      } else {
        // Fallback to mock data if no live tweets
        setTweets(getMockTweets())
      }
    } else {
      // Use mock data when API is offline
      setTweets(getMockTweets())
    }
    
    setLastUpdate(new Date())
    setLoading(false)
  }

  // Mock data fallback
  const getMockTweets = () => [
    {
      id: "mock_1",
      text: "URGENT: Major earthquake hits downtown area, buildings collapsing!",
      is_disaster: true,
      confidence: 0.911,
      priority_score: 1.0,
      coordinates: [37.7749, -122.4194],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.911,
        keyword_boost: 0.0,
        location_boost: 0.2,
        urgency_boost: 0.3,
        geolocation_confidence: 0.9
      },
      timestamp: new Date(Date.now() - 60000),
      simulation: true
    },
    {
      id: "mock_2",
      text: "Wildfire spreading rapidly near residential areas, evacuations ordered",
      is_disaster: true,
      confidence: 0.809,
      priority_score: 1.0,
      coordinates: [34.0522, -118.2437],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.809,
        keyword_boost: 0.1,
        location_boost: 0.2,
        urgency_boost: 0.15,
        geolocation_confidence: 0.9
      },
      timestamp: new Date(Date.now() - 120000),
      simulation: true
    },
    {
      id: "mock_3",
      text: "Flash flood warning issued, water levels rising quickly",
      is_disaster: true,
      confidence: 0.840,
      priority_score: 1.0,
      coordinates: [29.7604, -95.3698],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.840,
        keyword_boost: 0.1,
        location_boost: 0.2,
        urgency_boost: 0.15,
        geolocation_confidence: 0.9
      },
      timestamp: new Date(Date.now() - 180000),
      simulation: true
    },
    {
      id: "mock_4",
      text: "Tornado spotted moving towards city center",
      is_disaster: true,
      confidence: 0.755,
      priority_score: 1.0,
      coordinates: [35.5653, -96.9289],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.755,
        keyword_boost: 0.0,
        location_boost: 0.2,
        urgency_boost: 0.15,
        geolocation_confidence: 0.9
      },
      timestamp: new Date(Date.now() - 240000),
      simulation: true
    },
    {
      id: "mock_5",
      text: "Building explosion reported, emergency services responding",
      is_disaster: true,
      confidence: 0.698,
      priority_score: 1.0,
      coordinates: [40.7128, -74.0060],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.698,
        keyword_boost: 0.1,
        location_boost: 0.2,
        urgency_boost: 0.15,
        geolocation_confidence: 0.9
      },
      timestamp: new Date(Date.now() - 300000),
      simulation: true
    }
  ]

  // Auto-refresh functionality
  useEffect(() => {
    loadTweets()
    
    const interval = setInterval(() => {
      loadTweets()
    }, 30000) // Refresh every 30 seconds
    
    return () => clearInterval(interval)
  }, [])

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const getTimeAgo = (timestamp) => {
    const now = new Date()
    const diff = Math.floor((now - timestamp) / 1000)
    
    if (diff < 60) return `${diff}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return `${Math.floor(diff / 86400)}d ago`
  }

  const getPriorityLevel = (score) => {
    if (score >= 0.9) return { level: 'CRITICAL', color: 'bg-red-500' }
    if (score >= 0.7) return { level: 'HIGH', color: 'bg-orange-500' }
    if (score >= 0.5) return { level: 'MEDIUM', color: 'bg-yellow-500' }
    return { level: 'LOW', color: 'bg-green-500' }
  }

  const getApiStatusIcon = () => {
    switch (apiStatus) {
      case 'online':
        return <Wifi className="h-4 w-4 text-green-500" />
      case 'offline':
        return <WifiOff className="h-4 w-4 text-red-500" />
      default:
        return <RefreshCw className="h-4 w-4 text-yellow-500 animate-spin" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Disaster Tweet Triage</h1>
                <p className="text-slate-400 text-sm">Real-time emergency monitoring system</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-slate-400">Last Update</span>
                <span className="text-white font-mono">{formatTime(lastUpdate)}</span>
                {getApiStatusIcon()}
              </div>
              
              <Button 
                onClick={loadTweets} 
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* High Priority Alerts */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-5 w-5 text-red-500" />
                    <CardTitle className="text-white">High Priority Alerts</CardTitle>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                      {tweets.length} Active
                    </Badge>
                    {streamingActive && (
                      <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                        Live
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {tweets.map((tweet, index) => {
                  const priority = getPriorityLevel(tweet.priority_score || 0)
                  const isSelected = selectedTweet === index
                  
                  return (
                    <div
                      key={tweet.id}
                      className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                        isSelected 
                          ? 'border-blue-500 bg-blue-500/10' 
                          : 'border-slate-600 bg-slate-700/30 hover:bg-slate-700/50'
                      }`}
                      onClick={() => setSelectedTweet(isSelected ? null : index)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <Badge className={`${priority.color} text-white text-xs`}>
                          {priority.level}
                        </Badge>
                        <div className="flex items-center space-x-2 text-xs text-slate-400">
                          <Clock className="h-3 w-3" />
                          <span>{getTimeAgo(tweet.timestamp)}</span>
                          {tweet.simulation && (
                            <Badge variant="outline" className="text-xs border-slate-500 text-slate-400">
                              SIM
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-white mb-3 leading-relaxed">{tweet.text}</p>
                      
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-4">
                          <span className="text-slate-400">
                            Confidence: <span className="text-white">{((tweet.confidence || 0) * 100).toFixed(1)}%</span>
                          </span>
                          <span className="text-slate-400">
                            Priority: <span className="text-white">{((tweet.priority_score || 0) * 100).toFixed(1)}%</span>
                          </span>
                        </div>
                        
                        {tweet.coordinates && (
                          <div className="flex items-center space-x-1 text-blue-400">
                            <MapPin className="h-3 w-3" />
                            <span className="text-xs">
                              {tweet.coordinates[0].toFixed(4)}, {tweet.coordinates[1].toFixed(4)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
                
                {tweets.length === 0 && (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-slate-600" />
                    <p className="text-slate-400">No active alerts</p>
                    <p className="text-slate-500 text-sm">
                      {apiStatus === 'offline' ? 'API offline - using demo data' : 'Monitoring for new disasters...'}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Interactive Heatmap */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Map className="h-5 w-5 mr-2 text-blue-500" />
                  Disaster Heatmap
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Geographic distribution of alerts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="aspect-square rounded-lg overflow-hidden border border-slate-700">
                  <DisasterHeatmap 
                    tweets={tweets} 
                    selectedTweet={selectedTweet}
                    onTweetSelect={setSelectedTweet}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Selected Tweet Details */}
            {selectedTweet !== null && tweets[selectedTweet] && (
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white text-lg">Alert Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="text-white font-medium mb-2">Priority Factors</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Base Confidence:</span>
                        <span className="text-white">
                          {((tweets[selectedTweet].priority_factors?.base_confidence || tweets[selectedTweet].confidence || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Location Boost:</span>
                        <span className="text-white">
                          +{((tweets[selectedTweet].priority_factors?.location_boost || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Urgency Boost:</span>
                        <span className="text-white">
                          +{((tweets[selectedTweet].priority_factors?.urgency_boost || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Geo Confidence:</span>
                        <span className="text-white">
                          {((tweets[selectedTweet].geolocation_confidence || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {tweets[selectedTweet].coordinates && (
                    <div>
                      <h4 className="text-white font-medium mb-2">Location</h4>
                      <div className="bg-slate-900 rounded p-3">
                        <div className="flex items-center space-x-2 text-blue-400">
                          <MapPin className="h-4 w-4" />
                          <span className="text-sm">Coordinates</span>
                        </div>
                        <p className="text-white font-mono text-sm mt-1">
                          {tweets[selectedTweet].coordinates[0].toFixed(6)}, {tweets[selectedTweet].coordinates[1].toFixed(6)}
                        </p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* System Status */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <Alert className="bg-green-500/20 border-green-500/50">
                  <AlertTriangle className="h-4 w-4 text-green-500" />
                  <AlertDescription className="text-green-400">
                    All systems operational
                  </AlertDescription>
                </Alert>
                
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">API Status:</span>
                    <span className={`capitalize ${
                      apiStatus === 'online' ? 'text-green-400' : 
                      apiStatus === 'offline' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {apiStatus}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Model:</span>
                    <span className="text-green-400">Active</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Streaming:</span>
                    <span className={streamingActive ? 'text-green-400' : 'text-yellow-400'}>
                      {streamingActive ? 'Live' : 'Standby'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Auto-refresh:</span>
                    <span className="text-green-400">30s</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

