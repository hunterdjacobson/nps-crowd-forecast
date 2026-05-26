import { useState, useCallback } from 'react';
import { searchParks, getPark, getForecast } from '../api/client';

/**
 * Custom hook for managing national parks data and state,
 * now with specific handling for Render's free-tier cold starts.
 */
export function useParks() {
  const [parks, setParks] = useState([]);
  const [selectedPark, setSelectedPark] = useState(null);
  const [parkDetails, setParkDetails] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isWakingUp, setIsWakingUp] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Helper for exponential backoff retries to handle cold starts.
   */
  const fetchWithRetry = async (fetchFn, args) => {
    const delays = [3000, 6000, 12000]; // 3s, 6s, 12s
    let lastError;

    for (let i = 0; i <= delays.length; i++) {
      try {
        return await fetchFn(...args);
      } catch (err) {
        lastError = err;
        // If we haven't exhausted retries, wait and try again
        if (i < delays.length) {
          setIsWakingUp(true);
          await new Promise(resolve => setTimeout(resolve, delays[i]));
        }
      }
    }
    throw lastError;
  };

  /**
   * Handles searching for parks with retry logic.
   */
  const handleSearch = useCallback(async (query) => {
    setIsLoading(true);
    setIsWakingUp(false);
    setError(null);
    setSelectedPark(null);
    setParkDetails(null);
    setForecast(null);
    
    try {
      const results = await fetchWithRetry(searchParks, [query]);
      setParks(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
      setIsWakingUp(false);
    }
  }, []);

  /**
   * Handles selecting a park with concurrent fetches and retry logic.
   */
  const handleParkSelect = useCallback(async (park) => {
    setSelectedPark(park);
    setParkDetails(null);
    setForecast(null);
    setIsLoading(true);
    setIsWakingUp(false);
    setError(null);

    const parkCode = park.park_code || park.parkCode;

    try {
      // Wrap the combined fetches in the retry logic
      const [details, forecastData] = await fetchWithRetry(
        () => Promise.all([getPark(parkCode), getForecast(parkCode)]),
        []
      );
      
      setParkDetails(details);
      setForecast(forecastData);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
      setIsWakingUp(false);
    }
  }, []);

  return {
    parks,
    selectedPark,
    parkDetails,
    forecast,
    isLoading,
    isWakingUp,
    error,
    handleSearch,
    handleParkSelect
  };
}
