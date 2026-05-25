import { useState, useCallback } from 'react';
import { searchParks, getPark, getForecast } from '../api/client';

/**
 * Custom hook for managing national parks data and state.
 * 
 * @returns {Object} Parks state and handler functions.
 */
export function useParks() {
  const [parks, setParks] = useState([]);
  const [selectedPark, setSelectedPark] = useState(null);
  const [parkDetails, setParkDetails] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Handles searching for parks.
   * @param {string} query
   */
  const handleSearch = useCallback(async (query) => {
    setIsLoading(true);
    setError(null);
    try {
      const results = await searchParks(query);
      setParks(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Handles selecting a park and fetching its details and forecast concurrently.
   * @param {Object} park
   */
  const handleParkSelect = useCallback(async (park) => {
    // Reset selection-specific states
    setSelectedPark(park);
    setParkDetails(null);
    setForecast(null);
    setIsLoading(true);
    setError(null);

    const parkCode = park.park_code || park.parkCode;

    try {
      const [details, forecastData] = await Promise.all([
        getPark(parkCode),
        getForecast(parkCode)
      ]);
      
      setParkDetails(details);
      setForecast(forecastData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    parks,
    selectedPark,
    parkDetails,
    forecast,
    isLoading,
    error,
    handleSearch,
    handleParkSelect
  };
}
