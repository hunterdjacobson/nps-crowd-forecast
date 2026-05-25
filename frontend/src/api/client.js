import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

/**
 * Handles axios errors and throws user-friendly messages.
 * @param {Error} error 
 */
const handleError = (error) => {
  if (error.response?.status === 404) {
    throw new Error("Park not found");
  }
  throw new Error("Unable to reach the API — please try again");
};

/**
 * Search for parks by query.
 * @param {string} query 
 * @returns {Promise<any>}
 */
export async function searchParks(query) {
  try {
    const response = await client.get('/parks', { params: { q: query } });
    const results = response.data;
    
    const query_lower = query.toLowerCase();
    const filtered = results.filter(park => 
      park.full_name.toLowerCase().includes(query_lower) ||
      park.park_code.toLowerCase().includes(query_lower)
    );
    
    return filtered;
  } catch (error) {
    handleError(error);
  }
}

/**
 * Get detailed information for a specific park.
 * @param {string} parkCode 
 * @returns {Promise<any>}
 */
export async function getPark(parkCode) {
  try {
    const response = await client.get(`/parks/${parkCode}`);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

/**
 * Get the crowd level forecast for a specific park.
 * @param {string} parkCode 
 * @returns {Promise<any>}
 */
export async function getForecast(parkCode) {
  try {
    const response = await client.get(`/forecast/${parkCode}`);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}
