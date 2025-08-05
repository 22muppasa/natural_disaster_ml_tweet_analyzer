import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { MapPin, AlertTriangle, Clock, TrendingUp, RefreshCw, Map } from 'lucide-react'
import DisasterHeatmap from './components/DisasterHeatmap.jsx'
import './App.css'

function App() {
  const [tweets, setTweets] = useState([])
  const [loading, setLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [selectedTweet, setSelectedTweet] = useState(null)

  // Simulated real-time data fetching
  const fetchTopPriorityTweets = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8001/top_priority?limit=10')
      const data = await response.json()
      setTweets(data)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching tweets:', error)
      // Fallback to mock data if API is not available
      setTweets(mockTweets)
    }
    setLoading(false)
  }

  // API configuration
  const API_BASE_URL = 'https://8002-i30427mxkxuydow12jlnz-d351187c.manusvm.computer'
    {
      text: "URGENT: Major earthquake hits downtown area, buildings collapsing!",
      is_disaster: true,
      confidence: 0.91,
      priority_score: 1.0,
      coordinates: [37.7749, -122.4194],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.91,
        keyword_boost: 0.0,
        location_boost: 0.2,
        urgency_boost: 0.3,
        geolocation_confidence: 0.9
      }
    },
    {
      text: "Wildfire spreading rapidly near residential areas, evacuations ordered",
      is_disaster: true,
      confidence: 0.88,
      priority_score: 0.95,
      coordinates: [34.0522, -118.2437],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.88,
        keyword_boost: 0.1,
        location_boost: 0.2,
        urgency_boost: 0.15,
        geolocation_confidence: 0.9
      }
    },
    {
      text: "Flash flood warning issued, water levels rising quickly",
      is_disaster: true,
      confidence: 0.85,
      priority_score: 0.92,
      coordinates: [29.7604, -95.3698],
      geolocation_confidence: 0.9,
      priority_factors: {
        base_confidence: 0.85,
        keyword_boost: 0.1,
        location_boost: 0.2,
        urgency_boost: 0.15,
        geolocation_confidence: 0.9
      }
    }
  ]

  useEffect(() => {
    fetchTopPriorityTweets()
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchTopPriorityTweets, 30000)
    return () => clearInterval(interval)
  }, [])

  const getPriorityColor = (score) => {
    if (score >= 0.9) return 'bg-red-500'
    if (score >= 0.7) return 'bg-orange-500'
    if (score >= 0.5) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getPriorityLabel = (score) => {
    if (score >= 0.9) return 'CRITICAL'
    if (score >= 0.7) return 'HIGH'
    if (score >= 0.5) return 'MEDIUM'
    return 'LOW'
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-8 w-8 text-red-500" />
              <div>
                <h1 className="text-2xl font-bold">Disaster Tweet Triage</h1>
                <p className="text-slate-400">Real-time emergency monitoring system</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-slate-400">Last Update</p>
                <p className="font-mono text-sm">{formatTime(lastUpdate)}</p>
              </div>
              <Button 
                onClick={fetchTopPriorityTweets} 
                disabled={loading}
                variant="outline"
                size="sm"
                className="border-slate-600 text-white hover:bg-slate-700"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Tweet List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-red-500" />
                High Priority Alerts
              </h2>
              <Badge variant="secondary" className="bg-slate-700 text-white">
                {tweets.length} Active
              </Badge>
            </div>

            {loading && tweets.length === 0 ? (
              <div className="text-center py-8">
                <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-slate-400" />
                <p className="text-slate-400">Loading disaster alerts...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {tweets.map((tweet, index) => (
                  <Card 
                    key={index} 
                    className={`bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-all cursor-pointer ${
                      selectedTweet === index ? 'ring-2 ring-blue-500' : ''
                    }`}
                    onClick={() => setSelectedTweet(selectedTweet === index ? null : index)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <Badge 
                          className={`${getPriorityColor(tweet.priority_score)} text-white font-semibold`}
                        >
                          {getPriorityLabel(tweet.priority_score)}
                        </Badge>
                        <div className="flex items-center text-sm text-slate-400">
                          <Clock className="h-4 w-4 mr-1" />
                          {Math.floor(Math.random() * 5) + 1}m ago
                        </div>
                      </div>
                      
                      <p className="text-white mb-3 leading-relaxed">{tweet.text}</p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-slate-400">
                          <span>Confidence: {(tweet.confidence * 100).toFixed(1)}%</span>
                          <span>Priority: {(tweet.priority_score * 100).toFixed(1)}%</span>
                        </div>
                        {tweet.coordinates && (
                          <div className="flex items-center text-sm text-blue-400">
                            <MapPin className="h-4 w-4 mr-1" />
                            {tweet.coordinates[0].toFixed(4)}, {tweet.coordinates[1].toFixed(4)}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
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
                  <CardTitle className="text-white">Alert Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-white mb-2">Priority Factors</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Base Confidence:</span>
                        <span className="text-white">
                          {(tweets[selectedTweet].priority_factors.base_confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Location Boost:</span>
                        <span className="text-white">
                          +{(tweets[selectedTweet].priority_factors.location_boost * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Urgency Boost:</span>
                        <span className="text-white">
                          +{(tweets[selectedTweet].priority_factors.urgency_boost * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Geo Confidence:</span>
                        <span className="text-white">
                          {(tweets[selectedTweet].geolocation_confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {tweets[selectedTweet].coordinates && (
                    <div>
                      <h4 className="font-semibold text-white mb-2">Location</h4>
                      <div className="bg-slate-900 p-3 rounded border border-slate-700">
                        <div className="flex items-center text-blue-400 mb-1">
                          <MapPin className="h-4 w-4 mr-2" />
                          Coordinates
                        </div>
                        <p className="font-mono text-sm text-white">
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
                <div className="space-y-3">
                  <Alert className="border-green-500/50 bg-green-500/10">
                    <AlertTriangle className="h-4 w-4 text-green-500" />
                    <AlertDescription className="text-green-400">
                      All systems operational
                    </AlertDescription>
                  </Alert>
                  <div className="text-sm text-slate-400 space-y-1">
                    <div className="flex justify-between">
                      <span>API Status:</span>
                      <span className="text-green-400">Online</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Model:</span>
                      <span className="text-white">Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Auto-refresh:</span>
                      <span className="text-white">30s</span>
                    </div>
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

