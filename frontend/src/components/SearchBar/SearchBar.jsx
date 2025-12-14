import React, { useState } from 'react'
import './SearchBar.css'

const SearchBar = ({ onSearch, isLoading = false }) => {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  const validateUrl = (inputUrl) => {
    if (!inputUrl.trim()) {
      return 'Lütfen bir URL girin'
    }
    
    try {
      const urlObj = new URL(inputUrl.startsWith('http') ? inputUrl : `https://${inputUrl}`)
      return null
    } catch {
      return 'Geçerli bir URL girin (örn: example.com veya https://example.com)'
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    
    const validationError = validateUrl(url)
    if (validationError) {
      setError(validationError)
      return
    }

    let formattedUrl = url.trim()
    if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
      formattedUrl = `https://${formattedUrl}`
    }

    onSearch(formattedUrl)
  }

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSubmit} className="search-bar-form">
        <div className="search-input-wrapper">
          <div className="search-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
          </div>
          <input
            type="text"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value)
              setError('')
            }}
            placeholder="Site URL'sini girin (örn: example.com)"
            className="search-input"
            disabled={isLoading}
          />
          {url && (
            <button
              type="button"
              onClick={() => {
                setUrl('')
                setError('')
              }}
              className="search-clear"
              disabled={isLoading}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          )}
        </div>
        <button
          type="submit"
          className="search-button"
          disabled={isLoading || !url.trim()}
        >
          {isLoading ? (
            <>
              <span className="button-spinner"></span>
              <span>Analiz Ediliyor...</span>
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
              <span>Analiz Et</span>
            </>
          )}
        </button>
      </form>
      {error && (
        <div className="search-error fade-in">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}

export default SearchBar

