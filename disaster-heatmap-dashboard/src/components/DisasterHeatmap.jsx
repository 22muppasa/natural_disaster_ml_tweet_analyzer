import React, { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in React Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Component to fit map bounds to markers
function FitBounds({ tweets }) {
  const map = useMap()
  
  useEffect(() => {
    if (tweets && tweets.length > 0) {
      const validTweets = tweets.filter(tweet => tweet.coordinates)
      if (validTweets.length > 0) {
        const bounds = L.latLngBounds(validTweets.map(tweet => tweet.coordinates))
        map.fitBounds(bounds, { padding: [20, 20] })
      }
    }
  }, [tweets, map])
  
  return null
}

// Custom hook for heatmap data processing
function useHeatmapData(tweets) {
  return React.useMemo(() => {
    if (!tweets || tweets.length === 0) return []
    
    // Group tweets by location and calculate intensity
    const locationGroups = {}
    
    tweets.forEach(tweet => {
      if (!tweet.coordinates) return
      
      const key = `${tweet.coordinates[0].toFixed(3)},${tweet.coordinates[1].toFixed(3)}`
      
      if (!locationGroups[key]) {
        locationGroups[key] = {
          coordinates: tweet.coordinates,
          tweets: [],
          totalPriority: 0,
          maxPriority: 0,
          count: 0
        }
      }
      
      locationGroups[key].tweets.push(tweet)
      locationGroups[key].totalPriority += tweet.priority_score
      locationGroups[key].maxPriority = Math.max(locationGroups[key].maxPriority, tweet.priority_score)
      locationGroups[key].count += 1
    })
    
    // Convert to array and calculate average priority
    return Object.values(locationGroups).map(group => ({
      ...group,
      avgPriority: group.totalPriority / group.count,
      intensity: group.maxPriority // Use max priority for visual intensity
    }))
  }, [tweets])
}

const DisasterHeatmap = ({ tweets = [], selectedTweet, onTweetSelect }) => {
  const [mapCenter] = useState([39.8283, -98.5795]) // Center of USA
  const [mapZoom] = useState(4)
  const heatmapData = useHeatmapData(tweets)
  
  // Get color based on priority score
  const getPriorityColor = (score) => {
    if (score >= 0.9) return '#ef4444' // red-500
    if (score >= 0.7) return '#f97316' // orange-500
    if (score >= 0.5) return '#eab308' // yellow-500
    return '#22c55e' // green-500
  }
  
  // Get radius based on tweet count and priority
  const getMarkerRadius = (count, intensity) => {
    const baseRadius = 8
    const countMultiplier = Math.min(count * 2, 20)
    const intensityMultiplier = intensity * 15
    return baseRadius + countMultiplier + intensityMultiplier
  }
  
  // Get opacity based on priority
  const getMarkerOpacity = (intensity) => {
    return Math.max(0.3, intensity * 0.8)
  }
  
  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <FitBounds tweets={tweets} />
        
        {heatmapData.map((location, index) => (
          <CircleMarker
            key={index}
            center={location.coordinates}
            radius={getMarkerRadius(location.count, location.intensity)}
            fillColor={getPriorityColor(location.intensity)}
            color={getPriorityColor(location.intensity)}
            weight={2}
            opacity={0.8}
            fillOpacity={getMarkerOpacity(location.intensity)}
            eventHandlers={{
              click: () => {
                if (location.tweets.length > 0) {
                  onTweetSelect?.(tweets.findIndex(t => t === location.tweets[0]))
                }
              }
            }}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-semibold mb-2">
                  Disaster Alert Cluster
                </div>
                <div className="space-y-1">
                  <div>
                    <span className="font-medium">Location:</span> {location.coordinates[0].toFixed(4)}, {location.coordinates[1].toFixed(4)}
                  </div>
                  <div>
                    <span className="font-medium">Alert Count:</span> {location.count}
                  </div>
                  <div>
                    <span className="font-medium">Max Priority:</span> {(location.maxPriority * 100).toFixed(1)}%
                  </div>
                  <div>
                    <span className="font-medium">Avg Priority:</span> {(location.avgPriority * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <div className="font-medium mb-1">Recent Alerts:</div>
                  {location.tweets.slice(0, 2).map((tweet, idx) => (
                    <div key={idx} className="text-xs text-gray-600 mb-1">
                      "{tweet.text.substring(0, 50)}..."
                    </div>
                  ))}
                  {location.tweets.length > 2 && (
                    <div className="text-xs text-gray-500">
                      +{location.tweets.length - 2} more alerts
                    </div>
                  )}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 text-white text-sm">
        <div className="font-semibold mb-2">Priority Levels</div>
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span>Critical (90%+)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span>High (70-89%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span>Medium (50-69%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Low (&lt;50%)</span>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t border-slate-600 text-xs text-slate-300">
          Circle size indicates alert density
        </div>
      </div>
      
      {/* Stats overlay */}
      <div className="absolute top-4 right-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 text-white text-sm">
        <div className="font-semibold mb-1">Heatmap Stats</div>
        <div className="space-y-1 text-xs">
          <div>Total Alerts: {tweets.length}</div>
          <div>Active Locations: {heatmapData.length}</div>
          <div>
            Avg Priority: {tweets.length > 0 ? (tweets.reduce((sum, t) => sum + t.priority_score, 0) / tweets.length * 100).toFixed(1) : 0}%
          </div>
        </div>
      </div>
    </div>
  )
}

export default DisasterHeatmap

