import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix for Leaflet default icon issue in React/Vite
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

/**
 * Helper component to handle map flying/recentering.
 */
const RecenterMap = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    // Check for valid center and non-zero latitude
    if (center && center[0] !== 0) {
      map.flyTo(center, zoom, {
        duration: 1.5
      });
    }
  }, [center, zoom, map]);
  return null;
};

/**
 * Map component for displaying park markers and handling selection.
 * 
 * @param {Object} props
 * @param {Array} props.parks - List of park objects.
 * @param {Object|null} props.selectedPark - Currently selected park.
 * @param {Function} props.onParkSelect - Callback for park selection.
 */
const Map = ({ parks = [], selectedPark, onParkSelect }) => {
  const mapRef = useRef(null);
  
  // Default center of USA
  const defaultCenter = [39.5, -98.35];
  const defaultZoom = 4;

  useEffect(() => {
    if (parks.length > 0 && !selectedPark && mapRef.current) {
      mapRef.current.setView(defaultCenter, defaultZoom);
    }
  }, [parks, selectedPark]);

  // Filter out parks with invalid coordinates
  const validParks = parks.filter(p => 
    p.lat !== undefined && p.lon !== undefined && 
    p.lat !== 0 && p.lon !== 0 &&
    !isNaN(p.lat) && !isNaN(p.lon)
  );

  return (
    <div className="map-container rounded-xl shadow-inner border-2 border-gray-100 overflow-hidden">
      <MapContainer 
        center={defaultCenter} 
        zoom={defaultZoom} 
        scrollWheelZoom={true}
        className="h-full w-full"
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <RecenterMap center={selectedPark && selectedPark.lat !== 0 ? [selectedPark.lat, selectedPark.lon] : null} zoom={9} />

        {validParks.map((park) => (
          <Marker 
            key={park.id || `${park.lat}-${park.lon}`} 
            position={[park.lat, park.lon]}
          >
            <Popup>
              <div className="p-1">
                <h4 className="font-bold text-sm mb-2 text-gray-900">{park.full_name || park.fullName}</h4>
                <button 
                  onClick={() => onParkSelect(park)}
                  className="bg-green-700 text-white text-[10px] font-black uppercase tracking-widest px-3 py-2 rounded hover:bg-green-800 transition-colors w-full shadow-sm"
                >
                  View Forecast
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default Map;
