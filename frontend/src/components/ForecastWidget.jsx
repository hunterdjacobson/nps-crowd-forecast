import React from 'react';

/**
 * ForecastWidget component for displaying weather and crowd level predictions.
 * 
 * @param {Object} props
 * @param {Object|null} props.forecast - The forecast data object.
 * @param {boolean} props.isLoading - Loading state indicator.
 * @param {string|null} props.error - Error message if any.
 */
const ForecastWidget = ({ forecast, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 space-y-4 animate-pulse">
        <div className="h-6 bg-gray-200 rounded-full w-1/3"></div>
        <div className="h-32 bg-gray-200 rounded-xl w-full"></div>
        <div className="h-20 bg-gray-200 rounded-xl w-full"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 text-center">
        <div className="text-red-600 font-bold mb-2">Error</div>
        <p className="text-red-700 text-sm mb-4">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="text-xs font-bold uppercase tracking-wider text-red-800 hover:underline"
        >
          Click to retry
        </button>
      </div>
    );
  }

  if (!forecast) return null;

  const { weather, crowd_forecast, forecast_date } = forecast;

  const getWeatherEmoji = (desc = '') => {
    const d = desc.toLowerCase();
    if (d.includes('thunder')) return '🌩️';
    if (d.includes('rain')) return '🌧️';
    if (d.includes('snow')) return '❄️';
    if (d.includes('sunny') || d.includes('clear')) return '☀️';
    return '⛅';
  };

  const crowdClasses = {
    'Low': 'crowd-low',
    'Moderate': 'crowd-moderate',
    'High': 'crowd-high',
    'Very High': 'crowd-very-high'
  };

  const probClasses = {
    'Low': 'bg-green-500',
    'Moderate': 'bg-yellow-500',
    'High': 'bg-orange-500',
    'Very High': 'bg-red-500'
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-100 bg-sky-light/10">
        <h3 className="text-sm font-black uppercase tracking-tighter text-gray-900 mb-4">
          Current Forecast
        </h3>
        
        {/* Weather Section */}
        {weather.available ? (
          <div className="flex items-center justify-between">
            <div>
              <div className="text-lg font-bold text-gray-900">{weather.period_name}</div>
              <div className="text-sm text-gray-800 capitalize font-medium">{weather.short_forecast}</div>
              <div className="text-xs text-gray-700 mt-1 font-bold">
                💨 {weather.wind_speed} {weather.wind_direction}
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl mb-1">{getWeatherEmoji(weather.short_forecast)}</div>
              <div className="text-2xl font-black text-gray-900">
                {weather.temperature}°{weather.temperature_unit}
              </div>
            </div>
          </div>
        ) : (
          <div className="py-4 text-center italic text-gray-600 text-sm font-medium">
            Weather unavailable for this location
          </div>
        )}
      </div>

      <div className="p-6 space-y-6">
        {/* Crowd Forecast Section */}
        <div className="text-center">
          <div className="text-xs font-black uppercase tracking-widest text-gray-900 mb-2">Predicted Crowd Level</div>
          <div className={`inline-block px-8 py-3 rounded-full text-2xl font-black shadow-sm ${crowdClasses[crowd_forecast.crowd_label] || 'bg-gray-100'}`}>
            {crowd_forecast.crowd_label}
          </div>
          <div className="text-sm text-gray-800 mt-2 font-bold">
            Confidence: <span className="text-gray-900">{(crowd_forecast.confidence * 100).toFixed(1)}%</span>
          </div>
        </div>

        {/* Probability Bars */}
        <div className="space-y-3">
          {crowd_forecast.probabilities ? (
            Object.entries(crowd_forecast.probabilities).map(([label, prob]) => (
              <div key={label} className="space-y-1">
                <div className="flex justify-between text-[10px] font-black uppercase text-gray-900 px-1">
                  <span>{label}</span>
                  <span>{(prob * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${probClasses[label] || 'bg-gray-400'}`}
                    style={{ width: `${prob * 100}%` }}
                  ></div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-xs text-gray-500 italic">
              Detailed probability data unavailable
            </div>
          )}
        </div>

        <div className="pt-4 text-center border-t border-gray-50">
          <p className="text-[10px] text-gray-700 font-bold uppercase tracking-widest">
            Forecast for {forecast_date}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForecastWidget;
