"""
Setup script for MySQL database connection
This script will help you:
1. Check if MySQL is running
2. Test the connection
3. Create the database if it doesn't exist
4. Initialize the tables
"""

import sys
import os

def check_mysql_connection():
    """Check if MySQL is accessible"""
    try:
        import pymysql
        print("✓ PyMySQL is installed")
    except ImportError:
        print("✗ PyMySQL is not installed")
        print("  Installing PyMySQL...")
        os.system("pip install pymysql")
        import pymysql
        print("✓ PyMySQL installed successfully")
    
    # Try to connect to MySQL
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password=''
        )
        print("✓ MySQL connection successful!")
        return connection
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        print("\nPossible solutions:")
        print("1. Make sure XAMPP is installed")
        print("2. Start MySQL from XAMPP Control Panel")
        print("3. Check if MySQL is running on port 3306")
        return None

def create_database(connection):
    """Create the trading_ai database if it doesn't exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS trading_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Database 'trading_ai' created/verified")
        cursor.close()
        return True
    except Exception as e:
        print(f"✗ Failed to create database: {e}")
        return False

def test_database_connection():
    """Test connection to the trading_ai database"""
    try:
        import pymysql
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='trading_ai'
        )
        print("✓ Connected to trading_ai database successfully!")
        connection.close()
        return True
    except Exception as e:
        print(f"✗ Failed to connect to trading_ai database: {e}")
        return False

def initialize_tables():
    """Initialize database tables using Flask-SQLAlchemy"""
    try:
        os.environ['DB_TYPE'] = 'mysql'
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False

def main():
    print("=" * 60)
    print("MySQL Database Setup for Trading AI")
    print("=" * 60)
    print()
    
    # Step 1: Check MySQL connection
    print("Step 1: Checking MySQL connection...")
    connection = check_mysql_connection()
    if not connection:
        print("\n⚠ Please install and start XAMPP MySQL, then run this script again.")
        sys.exit(1)
    
    print()
    
    # Step 2: Create database
    print("Step 2: Creating database...")
    if not create_database(connection):
        connection.close()
        sys.exit(1)
    
    connection.close()
    print()
    
    # Step 3: Test database connection
    print("Step 3: Testing database connection...")
    if not test_database_connection():
        sys.exit(1)
    
    print()
    
    # Step 4: Initialize tables
    print("Step 4: Initializing database tables...")
    if not initialize_tables():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ Setup completed successfully!")
    print("=" * 60)
    print()
    print("To run the application with MySQL:")
    print("  Windows: set DB_TYPE=mysql && python app.py")
    print("  Or edit config.py and change DB_TYPE default to 'mysql'")
    print()

if __name__ == '__main__':
    main()
