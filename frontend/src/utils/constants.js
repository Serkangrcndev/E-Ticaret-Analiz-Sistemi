export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const RISK_LEVELS = {
  LOW: {
    label: 'Düşük Risk',
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.1)',
    borderColor: 'rgba(16, 185, 129, 0.3)'
  },
  MEDIUM: {
    label: 'Orta Risk',
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.1)',
    borderColor: 'rgba(245, 158, 11, 0.3)'
  },
  HIGH: {
    label: 'Yüksek Risk',
    color: '#f97316',
    bgColor: 'rgba(249, 115, 22, 0.1)',
    borderColor: 'rgba(249, 115, 22, 0.3)'
  },
  CRITICAL: {
    label: 'Kritik Risk',
    color: '#ef4444',
    bgColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: 'rgba(239, 68, 68, 0.3)'
  }
}

export const getRiskLevel = (score) => {
  if (score >= 75) return RISK_LEVELS.CRITICAL
  if (score >= 50) return RISK_LEVELS.HIGH
  if (score >= 25) return RISK_LEVELS.MEDIUM
  return RISK_LEVELS.LOW
}

export const SENTIMENT_COLORS = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280'
}

// Hex color'ı rgba'ya çevir
export const hexToRgba = (hex, alpha = 1) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

