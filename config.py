import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'trading-ai-secret-key-2024')
    
    # Database configuration
    # For XAMPP MySQL (default XAMPP settings):
    # - Host: localhost
    # - Port: 3306
    # - Username: root
    # - Password: (empty by default)
    # - Database: trading_ai
    
    # ⚠️ CHANGE THIS TO 'mysql' TO USE MYSQL, OR 'sqlite' TO USE SQLITE
    DB_TYPE = 'mysql'  # Change to 'mysql' or 'sqlite'
    
    # You can also override with environment variable
    DB_TYPE = os.environ.get('DB_TYPE', DB_TYPE).lower()
    
    if DB_TYPE == 'mysql':
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
        MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
        MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'trading_ai')
        
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///trading.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
