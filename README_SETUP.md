# Trading AI - Setup Instructions

## Quick Start (Without XAMPP - Using SQLite)

If you want to start immediately without installing XAMPP:

```bash
# Double-click this file:
start_with_sqlite.bat

# Or run manually:
python app.py
```

The application will use SQLite database and start on http://localhost:5000

---

## Setup with XAMPP MySQL

### Step 1: Install XAMPP

1. Download XAMPP from: https://www.apachefriends.org/download.html
2. Install XAMPP (default location: C:\xampp)
3. Open XAMPP Control Panel
4. Click "Start" next to MySQL
5. Wait until MySQL shows as running (green)

### Step 2: Install PyMySQL

```bash
pip install pymysql
```

### Step 3: Run Setup Script

```bash
# Double-click this file:
start_with_mysql.bat

# Or run manually:
python setup_mysql.py
```

This will:
- Check if MySQL is running
- Create the `trading_ai` database
- Initialize all tables
- Test the connection

### Step 4: Start the Application

```bash
# Option 1: Use the batch file
start_with_mysql.bat

# Option 2: Set environment variable and run
set DB_TYPE=mysql
python app.py

# Option 3: Edit config.py and change DB_TYPE default to 'mysql'
```

---

## Manual MySQL Configuration

If you need to customize MySQL settings:

### Default XAMPP MySQL Settings:
- Host: `localhost`
- Port: `3306`
- Username: `root`
- Password: (empty)
- Database: `trading_ai`

### To change settings:

Edit `config.py` and modify these lines:

```python
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''  # Add password if you set one
MYSQL_DATABASE = 'trading_ai'
```

Or use environment variables:

```bash
set MYSQL_HOST=localhost
set MYSQL_PORT=3306
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DATABASE=trading_ai
set DB_TYPE=mysql
python app.py
```

---

## Troubleshooting

### MySQL Connection Failed

**Problem:** Cannot connect to MySQL

**Solutions:**
1. Make sure XAMPP is installed
2. Open XAMPP Control Panel
3. Start MySQL service
4. Check if port 3306 is not blocked by firewall
5. Verify MySQL is running: `tasklist | findstr mysqld`

### Port Already in Use

**Problem:** Port 5000 is already in use

**Solution:** Change the port in app.py:

```python
socketio.run(app, host='0.0.0.0', port=5001, debug=False)
```

### Module Not Found Errors

**Problem:** Missing Python packages

**Solution:** Install all dependencies:

```bash
pip install flask flask-sqlalchemy flask-cors flask-socketio eventlet numpy pandas scipy requests ta python-dateutil pymysql
```

### Database Tables Not Created

**Problem:** Tables don't exist in database

**Solution:** Run the setup script:

```bash
python setup_mysql.py
```

---

## Switching Between SQLite and MySQL

### To use SQLite:
```bash
set DB_TYPE=sqlite
python app.py
```

### To use MySQL:
```bash
set DB_TYPE=mysql
python app.py
```

---

## Accessing the Application

Once started, open your browser and go to:
- http://localhost:5000

---

## Database Structure

The application creates these tables:
- `trades` - Trading history
- `signals` - Trading signals
- `backtest_results` - Backtest results
- `market_data` - Historical market data
- `user_settings` - User preferences

---

## Need Help?

If you encounter any issues:
1. Check that all dependencies are installed
2. Verify MySQL is running (if using MySQL)
3. Check the console output for error messages
4. Try using SQLite first to verify the app works
