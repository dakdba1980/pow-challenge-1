@echo off
REM Python Environment Setup Script for TLS Protocol Client (Windows)

echo === Python Environment Setup for TLS Protocol Client (Windows) ===

REM Create project directory
set PROJECT_DIR=tls_protocol_client
if not exist "%PROJECT_DIR%" (
    mkdir "%PROJECT_DIR%"
    echo [INFO] Created project directory: %PROJECT_DIR%
) else (
    echo [INFO] Project directory already exists: %PROJECT_DIR%
)

cd "%PROJECT_DIR%"

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org/downloads/
    pause
    exit /b 1
)

python --version
echo [INFO] Python found

REM Check Python version (simplified check)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8+ is required
    pause
    exit /b 1
)

echo [INFO] Python version is compatible

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [INFO] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Create requirements.txt
echo [INFO] Creating requirements.txt...
(
echo # Core dependencies (already in Python standard library^)
echo # ssl - Built-in
echo # socket - Built-in
echo # hashlib - Built-in
echo # secrets - Built-in
echo # threading - Built-in
echo # multiprocessing - Built-in
echo # concurrent.futures - Built-in
echo.
echo # Optional dependencies for enhanced functionality
echo cryptography>=3.4.8
echo pyOpenSSL>=21.0.0
echo certifi>=2021.10.8
echo.
echo # Development and testing
echo pytest>=6.2.5
echo pytest-cov>=3.0.0
echo black>=21.12.0
echo flake8>=4.0.1
) > requirements.txt

REM Install packages
echo [INFO] Installing required packages...
python -m pip install -r requirements.txt

echo [INFO] All packages installed successfully

REM Create directory structure
echo [INFO] Creating directory structure...
if not exist "certs" mkdir certs
if not exist "logs" mkdir logs
if not exist "tests" mkdir tests

REM Create run batch file
echo [INFO] Creating run batch file...
(
echo @echo off
echo REM TLS Protocol Client Runner for Windows
echo.
echo echo Activating virtual environment...
echo call venv\Scripts\activate.bat
echo.
echo echo Starting TLS Protocol Client...
echo python run_client.py %%*
echo.
echo pause
) > run_client.bat

REM Create config file (same as Linux version)
echo [INFO] Creating configuration file...
(
echo """
echo Configuration file for TLS Protocol Client
echo Update these values according to your needs
echo """
echo.
echo # Server configuration
echo SERVER_CONFIG = {
echo     'host': '18.202.148.130',
echo     'ports': [3336, 8083, 8446, 49155, 3481, 65532],
echo     'default_port': 3336,
echo     'timeout': 30
echo }
echo.
echo # Personal information - UPDATE THESE WITH YOUR ACTUAL DETAILS
echo PERSONAL_INFO = {
echo     'name': 'Your Full Name',
echo     'emails': ['your.email@example.com', 'your.second@example.com'],
echo     'skype': 'your.skype.account',  # or 'N/A' if no Skype
echo     'birthdate': '01.01.1990',  # format: %%d.%%m.%%Y
echo     'country': 'Germany',  # Use names from countries-ofthe-world.com
echo     'address_lines': [
echo         'Your Street Address',
echo         'Your City and Postal Code'
echo     ]
echo }
echo.
echo # Certificate paths
echo CERT_CONFIG = {
echo     'cert_path': 'certs/client.crt',
echo     'key_path': 'certs/client.key',
echo     'pem_path': 'certs/client.pem'
echo }
echo.
echo # Performance settings
echo PERFORMANCE_CONFIG = {
echo     'max_threads': 8,
echo     'pow_check_interval': 10000,
echo     'random_string_length': 8
echo }
) > config.py

REM Create Windows-specific README
echo [INFO] Creating README file...
(
echo # TLS Protocol Client - Windows
echo.
echo A high-performance Python implementation of a TLS protocol client with proof-of-work authentication.
echo.
echo ## Setup
echo.
echo The environment has been automatically set up. To activate it:
echo.
echo ```batch
echo venv\Scripts\activate.bat
echo ```
echo.
echo ## Usage
echo.
echo ### Using the batch file (recommended^)
echo ```batch
echo run_client.bat --cert certs\client.crt --key certs\client.key
echo ```
echo.
echo ### Direct Python execution
echo ```batch
echo python run_client.py --cert certs\client.crt --key certs\client.key
echo ```
echo.
echo ### Using PEM file
echo ```batch
echo run_client.bat --pem your_file.pem
echo ```
echo.
echo ### Using configuration file
echo ```batch
echo run_client.bat --config
echo ```
echo.
echo ## Configuration
echo.
echo 1. Edit `config.py` to update your personal information
echo 2. Place your certificate files in the `certs\` directory
echo 3. Run the client using the `--config` flag
echo.
echo ## Files
echo.
echo - `tls_client.py` - Main client implementation
echo - `pem_extractor.py` - PEM file extraction utility
echo - `run_client.py` - Client runner with environment handling
echo - `run_client.bat` - Windows batch file runner
echo - `config.py` - Configuration file
echo - `requirements.txt` - Python dependencies
echo.
echo ## Directory Structure
echo.
echo ```
echo tls_protocol_client\
echo ├── certs\          # Certificate files
echo ├── logs\           # Log files  
echo ├── tests\          # Test files
echo ├── venv\           # Virtual environment
echo └── *.py            # Python scripts
echo ```
) > README.md

echo.
echo [INFO] Environment setup completed successfully!
echo.
echo [INFO] Next steps:
echo [INFO] 1. Copy your certificate files to the certs\ directory
echo [INFO] 2. Update config.py with your personal information
echo [INFO] 3. Run the client:
echo [INFO]    run_client.bat --config
echo.
echo [INFO] Project directory: %CD%
echo.
pause