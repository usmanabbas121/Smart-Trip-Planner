import React from 'react';
import { LogSheet } from '../types';
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
      const end = Math.ceil(interval.end / 15);
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
          {/* DOT Header */}
          <div className="dot-header">
            <div className="dot-title">U.S. DEPARTMENT OF TRANSPORTATION</div>
            <div className="dot-subtitle">DRIVER'S DAILY LOG (ONE CALENDAR DAY - 24 HOURS)</div>
          </div>

          {/* Top Section - Left and Right */}
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

          <div className="log-grid">
            <div className="grid-header">
              <div className="status-label">Off Duty</div>
              <div className="time-labels">{renderTimeLabels()}</div>
            </div>
            {renderGridLine(sheet.grid.off_duty, 0)}
            
            <div className="grid-header">
              <div className="status-label">Sleeper Berth</div>
              <div className="time-labels">{renderTimeLabels()}</div>
            </div>
            {renderGridLine(sheet.grid.sleeper_berth, 1)}
            
            <div className="grid-header">
              <div className="status-label">Driving</div>
              <div className="time-labels">{renderTimeLabels()}</div>
            </div>
            {renderGridLine(sheet.grid.driving, 2)}
            
            <div className="grid-header">
              <div className="status-label">On Duty (Not Driving)</div>
              <div className="time-labels">{renderTimeLabels()}</div>
            </div>
            {renderGridLine(sheet.grid.on_duty_not_driving, 3)}
          </div>

          <div className="log-totals">
            <div className="total-row">
              <span>
                <FiClock style={{ marginRight: '4px' }} />
                Off Duty: {sheet.totals.off_duty.toFixed(2)} hrs
              </span>
              <span>
                <FiClock style={{ marginRight: '4px' }} />
                Sleeper Berth: {sheet.totals.sleeper_berth.toFixed(2)} hrs
              </span>
              <span>
                <FiClock style={{ marginRight: '4px' }} />
                Driving: {sheet.totals.driving.toFixed(2)} hrs
              </span>
              <span>
                <FiClock style={{ marginRight: '4px' }} />
                On Duty (Not Driving): {sheet.totals.on_duty_not_driving.toFixed(2)} hrs
              </span>
            </div>
            <div className="total-sum">
              <FiClock style={{ marginRight: '6px' }} />
              Total: {(sheet.totals.off_duty + sheet.totals.sleeper_berth + sheet.totals.driving + sheet.totals.on_duty_not_driving).toFixed(2)} hrs
            </div>
          </div>

          <div className="log-remarks">
            <div className="remarks-label">REMARKS</div>
            <div className="remarks-content">
              {sheet.remarks.map((remark, idx) => (
                <div key={idx} className="remark-item">{remark}</div>
              ))}
              {sheet.dvl_manifest_no || sheet.shipper_commodity ? (
                <div className="remark-item">
                  <strong>Pro or Shipping No.:</strong> {sheet.dvl_manifest_no || ''}
                  {sheet.shipper_commodity && ` - ${sheet.shipper_commodity}`}
                </div>
              ) : null}
            </div>
          </div>

          <div className="log-recap">
            <div className="recap-label">Recap</div>
            <div className="recap-content">
              <div className="recap-item">
                <FiClock style={{ marginRight: '6px', color: '#000000' }} />
                On Duty Today: {sheet.recap.on_duty_today.toFixed(2)} hrs
              </div>
              <div className="recap-item">
                <FiClock style={{ marginRight: '6px', color: '#000000' }} />
                Total Last 7 Days: {sheet.recap.total_last_7_days.toFixed(2)} hrs
              </div>
              <div className="recap-item">
                <FiClock style={{ marginRight: '6px', color: '#000000' }} />
                Available Tomorrow (70hr): {sheet.recap.available_tomorrow_70.toFixed(2)} hrs
              </div>
              <div className="recap-item">
                <FiClock style={{ marginRight: '6px', color: '#000000' }} />
                Total Last 5 Days: {sheet.recap.total_last_5_days.toFixed(2)} hrs
              </div>
            </div>
          </div>
          </div>
        );
      })}
    </div>
  );
};

export default LogSheets;

