import React from 'react'
import { getRiskLevel } from '../../utils/constants'
import './RiskBadge.css'

const RiskBadge = ({ score, showScore = true }) => {
  const riskInfo = getRiskLevel(score)
  
  return (
    <div 
      className="risk-badge"
      style={{
        '--risk-color': riskInfo.color,
        '--risk-bg': riskInfo.bgColor,
        '--risk-border': riskInfo.borderColor
      }}
    >
      <span className="risk-badge-dot"></span>
      <span className="risk-badge-label">{riskInfo.label}</span>
      {showScore && (
        <span className="risk-badge-score">{score}</span>
      )}
    </div>
  )
}

export default RiskBadge

