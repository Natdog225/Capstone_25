import React from 'react';
import { Upload, FileText, DollarSign } from 'lucide-react';
import './CSS/FileImport.css';

const FileImport = () => {
  const handleImportClick = (type) => {
    console.log(`${type} button clicked - functionality to be implemented`);
  };

  return (
    <div className="file-import-container">
      <div className="file-import-header">
        <h2 className="section-title">File Import & Data Sync</h2>
        <p className="section-subtitle">
          Import sales data or sync with your existing systems
        </p>
      </div>

      <div className="import-buttons-grid">
        <button 
          className="import-button csv"
          onClick={() => handleImportClick('CSV')}
        >
          <div className="button-icon">
            <FileText size={32} />
          </div>
          <div className="button-content">
            <h3>Import CSV File</h3>
            <p>Upload sales data from CSV spreadsheets</p>
          </div>
        </button>

        <button 
          className="import-button toast"
          onClick={() => handleImportClick('Toast')}
        >
          <div className="button-icon">
            <Upload size={32} />
          </div>
          <div className="button-content">
            <h3>Sync with Toast</h3>
            <p>Connect to your Toast POS system</p>
          </div>
        </button>

        <button 
          className="import-button quickbooks"
          onClick={() => handleImportClick('QuickBooks')}
        >
          <div className="button-icon">
            <DollarSign size={32} />
          </div>
          <div className="button-content">
            <h3>Sync with QuickBooks</h3>
            <p>Import financial data from QuickBooks</p>
          </div>
        </button>
      </div>

      <div className="import-info-card">
        <h4>Data Import Information</h4>
        <ul>
          <li>CSV files should include date, sales amount, and transaction details</li>
          <li>Toast integration requires API credentials from your Toast account</li>
          <li>QuickBooks sync uses OAuth authentication for secure access</li>
          <li>All imported data is encrypted and stored securely</li>
        </ul>
      </div>
    </div>
  );
};

export default FileImport;