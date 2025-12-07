# Trading AI - Quick Start Guide

## ✅ Current Status

Your Trading AI application is ready to run! All dependencies are installed.

---

## 🚀 Option 1: Start Immediately (SQLite - No XAMPP needed)

**Easiest way to get started:**

### Windows:
Double-click: `start_with_sqlite.bat`

### Or manually:
```bash
python app.py
```

Then open: **http://localhost:5000**

---

## 🗄️ Option 2: Use XAMPP MySQL

### Prerequisites:
1. **Install XAMPP** from https://www.apachefriends.org/
2. **Start MySQL** from XAMPP Control Panel

### Setup Steps:

#### Step 1: Start MySQL
1. Open XAMPP Control Panel
2. Click "Start" next to MySQL
3. Wait for it to turn green

#### Step 2: Run Setup
Double-click: `start_with_mysql.bat`

Or manually:
```bash
python setup_mysql.py
```

#### Step 3: Start Application
```bash
set DB_TYPE=mysql
python app.py
```

Then open: **http://localhost:5000**

---

## 📋 What's Installed

✅ Flask - Web framework  
✅ Flask-SQLAlchemy - Database ORM  
✅ Flask-SocketIO - Real-time communication  
✅ Flask-CORS - Cross-origin support  
✅ Eventlet - Async support  
✅ NumPy, Pandas, SciPy - Data processing  
✅ TA - Technical analysis  
✅ PyMySQL - MySQL connector  

---

## 🔧 Configuration Files Created

- `config.py` - Database configuration
- `setup_mysql.py` - MySQL setup script
- `start_with_sqlite.bat` - Quick start with SQLite
- `start_with_mysql.bat` - Quick start with MySQL
- `test_app.py` - Test script

---

## 🎯 Next Steps

1. **Start the app** using one of the methods above
2. **Open your browser** to http://localhost:5000
3. **Explore the trading interface**

---

## ⚙️ MySQL Connection Settings

If you need to customize MySQL settings, edit `config.py`:

```python
MYSQL_HOST = 'localhost'      # MySQL server
MYSQL_PORT = '3306'           # MySQL port
MYSQL_USER = 'root'           # Username
MYSQL_PASSWORD = ''           # Password (empty by default in XAMPP)
MYSQL_DATABASE = 'trading_ai' # Database name
```

---

## 🐛 Troubleshooting

### "MySQL connection failed"
- Make sure XAMPP is installed
- Start MySQL from XAMPP Control Panel
- Check if port 3306 is available

### "Port 5000 already in use"
- Change port in app.py: `socketio.run(app, port=5001)`

### "Module not found"
- Run: `pip install flask flask-sqlalchemy flask-socketio pymysql`

---

## 📞 Testing MySQL Connection

To test if MySQL is running:

```bash
python -c "import pymysql; pymysql.connect(host='localhost', user='root', password='')"
```

If successful, you'll see no errors.

---

## 🔄 Switching Databases

### Use SQLite:
```bash
set DB_TYPE=sqlite
python app.py
```

### Use MySQL:
```bash
set DB_TYPE=mysql
python app.py
```

---

## ✨ Features

- Real-time market data analysis
- Trading signals generation
- Backtesting strategies
- Multiple trading pairs support
- WebSocket real-time updates
- Technical indicators (SMC/ICT)

---

**Ready to trade? Start the application now!** 🚀
