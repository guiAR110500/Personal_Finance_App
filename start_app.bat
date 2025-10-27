@echo off
echo Starting Personal Finance Dashboard...
echo.

:: Activate virtual environment
call "C:\Users\guigs\Documents\Personal_Finance_App\.venv\Scripts\activate.bat"

:: Start Streamlit app using full Python path
"C:\Users\guigs\Documents\Personal_Finance_App\.venv\Scripts\python.exe" -m streamlit run app.py

pause