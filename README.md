# Personal Finance App

A Python-based personal finance application that connects to Google Sheets to manage and analyze financial data.

## Features

- Google Sheets integration for data storage
- Data visualization with charts
- Financial data analysis and tracking

## Setup

1. Install dependencies:
   ```bash
   pip install gspread pandas google-auth google-api-python-client plotly streamlit
   ```

2. Set up Google Sheets credentials:
   - Place your `credentials.json` file in the project root
   - Configure your Google Sheets API access

3. Run the application:
   ```bash
   python main.py
   ```

## Dependencies

- gspread: Google Sheets API integration
- pandas: Data manipulation and analysis
- google-auth: Authentication for Google APIs
- plotly: Interactive charts and visualizations
- streamlit: Web application framework

## Configuration

Make sure to update the sheet_id in `data_source.py` to match your Google Sheets document.