import React from 'react';
import { LogSheet, IntermediateCity } from '../types';
import { FaFileAlt } from 'react-icons/fa';
import { FiClock } from 'react-icons/fi';
import './LogSheets.css';

interface LogSheetsProps {
  logSheets: LogSheet[];
}

const LogSheets: React.FC<LogSheetsProps> = ({ logSheets }) => {
  const renderGridLine = (intervals: Array<{ start: number; end: number }>, rowIndex: number) => {
    const line = Array(96).fill(false);
    
    intervals.forEach(interval => {
      const start = Math.floor(interval.start / 15);
      const end = Math.floor(interval.end / 15);
      for (let i = start; i < end && i < 96; i++) {
        line[i] = true;
      }
    });

    return (
      <div className="grid-row" key={rowIndex}>
        {line.map((active, idx) => (
          <div
            key={idx}
            className={`grid-cell ${active ? 'active' : ''}`}
            style={{ width: `${100 / 96}%` }}
          />
        ))}
      </div>
    );
  };

  const renderTimeLabels = () => {
    const labels: JSX.Element[] = [];
    const hourLabels = ['Midnight', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', 'Noon', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'];
    
    for (let i = 0; i < 96; i++) {
      const hour = Math.floor(i / 4);
      const quarter = i % 4;
      
      if (quarter === 0) {
        labels.push(
          <div key={i} className="time-label hour-mark">
            {hourLabels[hour]}
          </div>
        );
      } else {
        labels.push(
          <div key={i} className="time-label quarter-mark">
            {quarter === 2 ? '|' : ''}
          </div>
        );
      }
    }
    return labels;
  };

  const parseDate = (dateStr: string) => {
    const [month, day, year] = dateStr.split('/');
    return { month, day, year };
  };

  const calculateTotalHours = (totals: LogSheet['totals']) => {
    return (totals.off_duty + totals.sleeper_berth + totals.driving + totals.on_duty_not_driving).toFixed(2);
  };

  const renderCityTimeGrid = (
    cities: IntermediateCity[] | undefined,
    remarks: string[],
    dvlManifestNo?: string,
    shipperCommodity?: string,
    recap?: { on_duty_today: number; total_last_7_days: number; available_tomorrow_70: number; total_last_5_days: number },
    fromLocation?: string,
    toLocation?: string
  ) => {
    const hours = Array.from({ length: 24 }, (_, i) => i);
    const citiesList = cities || [];
    
    const sortedCities = [...citiesList].sort((a, b) => a.hours_into_day - b.hours_into_day);
    
    const cityAtHour: { [key: number]: IntermediateCity[] } = {};
    
    sortedCities.forEach(city => {
      const hoursIntoDay = city.hours_into_day;
      if (hoursIntoDay >= 0 && hoursIntoDay < 24) {
        const hour = Math.floor(hoursIntoDay);
        if (hour >= 0 && hour < 24) {
          if (!cityAtHour[hour]) {
            cityAtHour[hour] = [];
          }
          cityAtHour[hour].push(city);
        }
      }
    });
    
    hours.forEach(hour => {
      if (cityAtHour[hour]) {
        cityAtHour[hour].sort((a, b) => a.hours_into_day - b.hours_into_day);
      }
    });
    
    return (
      <>
        {/* Timeline Section */}
        <div className="city-timeline-box">
          <div className="city-timeline-row">
            <div className="city-row-label">REMARKS</div>
            <div className="city-hour-blocks">
              {hours.map(hour => {
                const citiesInHour = cityAtHour[hour] || [];
                const hourLabel = hour === 0 ? 'Mid' : hour === 12 ? 'Noon' : hour.toString();
                const primaryCity = citiesInHour.find(c => c.type === 'pickup' || c.type === 'dropoff') || citiesInHour[0];
                const cityType = primaryCity?.type || 'intermediate';
                const fillClass = cityType === 'pickup' ? 'city-fill pickup' : 
                                 cityType === 'dropoff' ? 'city-fill dropoff' : 'city-fill';
                
                return (
                  <div key={hour} className={`city-hour-block ${primaryCity ? 'has-city' : ''}`}>
                    <div className="hour-label-top">{hourLabel}</div>
                    <div className="hour-cell">
                      {primaryCity && <div className={fillClass}></div>}
                    </div>
                    {primaryCity && (
                      <div className={`city-name-below ${cityType}`}>
                        <div className="city-name-text">
                          {primaryCity.name}
                          {citiesInHour.length > 1 && (
                            <span className="city-count-badge">
                              +{citiesInHour.length - 1}
                            </span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              <div className="total-label">=24</div>
            </div>
          </div>
        </div>
        
        <div className="remarks-box">
          <div className="remarks-inside-box">
          <div className="remarks-upper-section">
            {recap && (
              <div className="recap-grid">
                <div className="recap-chip">
                  <span className="recap-label-text">On Duty Today:</span>
                  <span className="recap-value">{recap.on_duty_today.toFixed(2)} hrs</span>
                </div>
                <div className="recap-chip">
                  <span className="recap-label-text">Total Last 7 Days:</span>
                  <span className="recap-value">{recap.total_last_7_days.toFixed(2)} hrs</span>
                </div>
                <div className="recap-chip">
                  <span className="recap-label-text">Available (70hr):</span>
                  <span className="recap-value">{recap.available_tomorrow_70.toFixed(2)} hrs</span>
                </div>
                <div className="recap-chip">
                  <span className="recap-label-text">Total Last 5 Days:</span>
                  <span className="recap-value">{recap.total_last_5_days.toFixed(2)} hrs</span>
                </div>
                {(dvlManifestNo || shipperCommodity) && (
                  <div className="remark-chip shipping">
                    <span className="remark-time">Pro/Ship#</span>
                    <span className="remark-desc">{dvlManifestNo}{shipperCommodity && ` - ${shipperCommodity}`}</span>
                  </div>
                )}
              </div>
            )}
            {!recap && (dvlManifestNo || shipperCommodity) && (
              <div className="recap-grid">
                <div className="remark-chip shipping">
                  <span className="remark-time">Pro/Ship#</span>
                  <span className="remark-desc">{dvlManifestNo}{shipperCommodity && ` - ${shipperCommodity}`}</span>
                </div>
              </div>
            )}
          </div>
          
          {(recap || dvlManifestNo || shipperCommodity) && remarks && remarks.length > 0 && (
            <div className="remarks-divider"></div>
          )}
          
          {remarks && remarks.length > 0 && (
            <div className="remarks-lower-section">
              <div className="remarks-grid">
                {remarks.map((remark, idx) => {
                  const parts = remark.split(' - ');
                  const time = parts[0];
                  const description = parts.slice(1).join(' - ');
                  return (
                    <div key={idx} className="remark-chip">
                      <span className="remark-time">{time}</span>
                      <span className="remark-desc">{description}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="log-sheets">
      <h2>
        <FaFileAlt style={{ marginRight: '8px', verticalAlign: 'middle', color: '#ffffff' }} />
        {logSheets.length > 1 ? 'Log Sheets' : 'Log Sheet'}
      </h2>
      {logSheets.map((sheet, sheetIndex) => {
        const dateParts = parseDate(sheet.date);
        const totalHours = calculateTotalHours(sheet.totals);
        const vehicleNumbers = [sheet.truck_tractor_number, sheet.trailer_number].filter(Boolean).join(' / ');
        
        return (
          <div key={sheetIndex} className="log-sheet">
          <div className="dot-header">
            <div className="dot-title">U.S. DEPARTMENT OF TRANSPORTATION</div>
            <div className="dot-subtitle">DRIVER'S DAILY LOG (ONE CALENDAR DAY - 24 HOURS)</div>
          </div>

          <div className="log-header-top">
            <div className="header-left">
              <div className="header-field-dot">
                <label>Date:</label>
                <div className="date-fields">
                  <div className="date-field">
                    <div className="date-label">(MONTH)</div>
                    <div className="date-value">{dateParts.month}</div>
                  </div>
                  <div className="date-field">
                    <div className="date-label">(DAY)</div>
                    <div className="date-value date-day">{dateParts.day}</div>
                  </div>
                  <div className="date-field">
                    <div className="date-label">(YEAR)</div>
                    <div className="date-value">{dateParts.year}</div>
                  </div>
                </div>
              </div>
              <div className="header-field-dot">
                <label>Name of carrier:</label>
                <span className="field-value">{sheet.carrier_name || '________________'}</span>
              </div>
              <div className="header-field-dot">
                <label>Main office address:</label>
                <span className="field-value">{sheet.main_office_address || '________________'}</span>
              </div>
              <div className="header-field-dot">
                <label>Home terminal address:</label>
                <span className="field-value">{sheet.home_terminal_address || '________________'}</span>
              </div>
              <div className="header-field-dot from-field">
                <label>From:</label>
                <span className="field-value">{sheet.from || '________________'}</span>
              </div>
              <div className="header-field-dot to-field">
                <label>To:</label>
                <span className="field-value">{sheet.to || '________________'}</span>
              </div>
            </div>
            
            <div className="header-right">
              <div className="header-instructions">
                <div>ORIGINAL - Submit to carrier within 13 days</div>
                <div>DUPLICATE - Driver retains possession for eight days</div>
              </div>
              <div className="header-field-dot">
                <label>Truck or tractor and trailer number:</label>
                <span className="field-value">{vehicleNumbers || '________________'}</span>
              </div>
              <div className="header-field-dot">
                <label>Total miles driving today:</label>
                <span className="field-value">{sheet.total_miles_driving.toFixed(1)}</span>
              </div>
              <div className="header-field-dot">
                <label>Driver's signature/certification:</label>
                <span className="field-value signature">{sheet.driver_name || '________________'}</span>
              </div>
              <div className="header-field-dot co-driver-field">
                <label>Name of co-driver:</label>
                <span className="field-value">{sheet.co_driver_name || '________________'}</span>
              </div>
              <div className="header-field-dot total-hours-field">
                <label>Total hours:</label>
                <span className="field-value">{totalHours}</span>
              </div>
              <div className="certification-text">I certify that these entries are true and correct</div>
            </div>
          </div>

          <div className="log-grid-new">
            <div className="log-grid-header-row">
              <div className="log-grid-label"></div>
              <div className="log-grid-hours">
                {Array.from({ length: 24 }).map((_, i) => (
                  <div key={i} className="log-hour-cell">
                    <span>{i === 0 ? 'Mid' : i === 12 ? 'Noon' : i}</span>
                  </div>
                ))}
              </div>
              <div className="log-grid-total-header">TOTAL<br/>HOURS</div>
            </div>
            
            <div className="log-grid-status-row">
              <div className="log-grid-label">Off Duty</div>
              <div className="log-grid-cells">
                {renderGridLine(sheet.grid.off_duty, 0)}
              </div>
              <div className="log-grid-total">{sheet.totals.off_duty.toFixed(2)}</div>
            </div>
            
            <div className="log-grid-status-row">
              <div className="log-grid-label">Sleeper Berth</div>
              <div className="log-grid-cells">
                {renderGridLine(sheet.grid.sleeper_berth, 1)}
              </div>
              <div className="log-grid-total">{sheet.totals.sleeper_berth.toFixed(2)}</div>
            </div>
            
            <div className="log-grid-status-row">
              <div className="log-grid-label">Driving</div>
              <div className="log-grid-cells">
                {renderGridLine(sheet.grid.driving, 2)}
              </div>
              <div className="log-grid-total">{sheet.totals.driving.toFixed(2)}</div>
            </div>
            
            <div className="log-grid-status-row">
              <div className="log-grid-label">On Duty (Not Driving)</div>
              <div className="log-grid-cells">
                {renderGridLine(sheet.grid.on_duty_not_driving, 3)}
              </div>
              <div className="log-grid-total">{sheet.totals.on_duty_not_driving.toFixed(2)}</div>
            </div>
          </div>

          {renderCityTimeGrid(
            sheet.intermediate_cities,
            sheet.remarks,
            sheet.dvl_manifest_no,
            sheet.shipper_commodity,
            sheet.recap,
            sheet.from,
            sheet.to
          )}
          </div>
        );
      })}
    </div>
  );
};

export default LogSheets;

