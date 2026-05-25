import React, { useState } from 'react';

/**
 * SearchBar component for filtering national parks.
 * 
 * @param {Object} props
 * @param {Function} props.onSearch - Callback function called with the search query.
 * @param {boolean} props.isLoading - Loading state indicator.
 */
const SearchBar = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = () => {
    const trimmedQuery = query.trim();
    if (trimmedQuery.length >= 2) {
      onSearch(trimmedQuery);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div className="flex w-full max-w-2xl gap-2 items-center bg-white p-2 rounded-lg shadow-md border border-gray-200">
      <div className="flex-1 relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search national parks..."
          className="w-full px-4 py-2 outline-none text-gray-900 bg-transparent font-medium placeholder:text-gray-500"
        />
      </div>
      
      <div 
        onClick={handleSubmit}
        className={`flex items-center justify-center px-6 py-2 rounded-md transition-colors cursor-pointer select-none font-black uppercase tracking-widest text-white shadow-sm
          ${isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-700 hover:bg-green-800'}`}
      >
        {isLoading ? (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Searching...</span>
          </div>
        ) : (
          <span>Search</span>
        )}
      </div>
    </div>
  );
};

export default SearchBar;
