import React from 'react';

/**
 * ParkCard component for displaying park details, alerts, and visitor centers.
 * 
 * @param {Object} props
 * @param {Object} props.park - The park object from NPS API.
 * @param {Array} props.alerts - Array of alert objects.
 * @param {Array} props.visitorCenters - Array of visitor center objects.
 */
const ParkCard = ({ park, alerts = [], visitorCenters = [] }) => {
  const today = new Date().toLocaleDateString('en', { weekday: 'long' }).toLowerCase();

  const getAlertBadgeColor = (category) => {
    switch (category) {
      case 'Closure':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Information':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTodayHours = (center) => {
    const hours = center.operatingHours?.[0]?.standardHours;
    return hours?.[today] || 'Hours not available';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden flex flex-col h-full">
      {/* Header Section */}
      <div className="p-6 bg-white border-b border-gray-100">
        <h2 className="text-2xl font-bold leading-tight text-gray-900">{park.fullName}</h2>
        <p className="text-gray-600 font-medium mt-1 uppercase text-xs tracking-widest">
          {park.states} | {park.designation}
        </p>
      </div>

      <div className="p-6 flex-1 flex flex-col gap-6">
        {/* Description */}
        <div>
          <p className="text-gray-800 line-clamp-5 italic">
            "{park.description}"
          </p>
          {park.description?.length > 200 && (
            <a 
              href={park.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-xs font-bold text-green-700 hover:underline mt-1 inline-block"
            >
              Read more...
            </a>
          )}
        </div>

        {/* Alerts Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-black uppercase tracking-wider text-gray-900">Active Alerts</h3>
          {alerts.length > 0 ? (
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div 
                  key={alert.id} 
                  className={`flex flex-col p-3 border rounded-lg ${getAlertBadgeColor(alert.category)}`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase px-1.5 py-0.5 rounded border border-current">
                      {alert.category}
                    </span>
                    <span className="font-bold text-sm">{alert.title}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-3 bg-green-50 text-green-800 border border-green-200 rounded-lg text-sm font-medium">
              ✓ No active alerts
            </div>
          )}
        </div>

        {/* Visitor Centers Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-black uppercase tracking-wider text-gray-900">Visitor Centers</h3>
          {visitorCenters.length > 0 ? (
            <div className="grid gap-3">
              {visitorCenters.slice(0, 3).map((center) => (
                <div key={center.id} className="text-sm">
                  <div className="font-bold text-gray-900">{center.name}</div>
                  <div className="text-gray-800 flex justify-between items-center">
                    <span>Today's Hours:</span>
                    <span className="font-mono text-xs text-gray-900">{getTodayHours(center)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-600 italic">No visitor center data available</p>
          )}
        </div>
      </div>

      {/* Footer Link */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 mt-auto">
        <a 
          href={park.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-green-700 font-black text-sm hover:underline flex items-center justify-center gap-2 uppercase tracking-tight"
        >
          View on NPS.gov
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  );
};

export default ParkCard;
