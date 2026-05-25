import React from 'react';
import { useParks } from './hooks/useParks';
import SearchBar from './components/SearchBar';
import Map from './components/Map';
import ParkCard from './components/ParkCard';
import ForecastWidget from './components/ForecastWidget';

function App() {
  const {
    parks,
    selectedPark,
    parkDetails,
    forecast,
    isLoading,
    error,
    handleSearch,
    handleParkSelect
  } = useParks();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
      {/* Header */}
      <header className="bg-green-800 text-white p-6 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black tracking-tight flex items-center gap-2 text-white">
              <span role="img" aria-label="tent">🏕️</span> NPS Crowd Forecast
            </h1>
            <p className="text-green-100 font-medium text-sm">
              Live conditions & crowd predictions for US National Parks
            </p>
          </div>
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>
      </header>

      {/* Global Error Banner */}
      {error && (
        <div className="bg-red-600 text-white p-3 text-center text-sm font-bold animate-pulse">
          ⚠️ {error}
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 md:p-8">
        <div className="flex flex-col md:flex-row gap-8">
          
          {/* LEFT COLUMN: Info & Search */}
          <div className="w-full md:w-1/3 flex flex-col gap-6">
            {!parkDetails && !isLoading && !error && parks.length === 0 && (
              <div className="bg-white p-8 rounded-xl border-2 border-dashed border-gray-200 text-center text-gray-800">
                <p className="text-lg font-medium">Search for a park to begin</p>
                <p className="text-sm mt-1 italic">Try "Yosemite", "Zion", or "Yellowstone"</p>
              </div>
            )}

            {parkDetails && (
              <div className="animate-in fade-in slide-in-from-left duration-500">
                <ParkCard 
                  park={parkDetails.park} 
                  alerts={parkDetails.alerts} 
                  visitorCenters={parkDetails.visitor_centers} 
                />
              </div>
            )}
          </div>

          {/* RIGHT COLUMN: Map & Forecast */}
          <div className="w-full md:w-2/3 flex flex-col gap-6">
            <div className="sticky top-4 space-y-6">
              <Map 
                parks={parks} 
                selectedPark={selectedPark} 
                onParkSelect={handleParkSelect} 
              />
              
              <div className="max-w-md mx-auto md:mx-0">
                <ForecastWidget 
                  forecast={forecast} 
                  isLoading={isLoading} 
                  error={null} // Sub-component error handled globally or locally if needed
                />
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-8 px-4 text-center">
        <p className="text-gray-800 text-xs font-bold tracking-widest uppercase">
          Powered by NPS API · NOAA · XGBoost
        </p>
      </footer>
    </div>
  );
}

export default App;
