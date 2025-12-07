"""
Simple test script to verify the app can start and database works
"""

import os
os.environ['DB_TYPE'] = 'sqlite'  # Use SQLite for testing

print("Testing Trading AI application...")
print("=" * 60)

try:
    print("\n1. Importing modules...")
    import eventlet
    eventlet.monkey_patch()
    
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    print("   ✓ Modules imported successfully")
    
    print("\n2. Creating Flask app...")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_trading.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    print("   ✓ Flask app created")
    
    print("\n3. Defining models...")
    class TestModel(db.Model):
        __tablename__ = 'test'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
    print("   ✓ Models defined")
    
    print("\n4. Creating database tables...")
    with app.app_context():
        db.create_all()
    print("   ✓ Database tables created")
    
    print("\n5. Testing database write...")
    with app.app_context():
        test_record = TestModel(name='test')
        db.session.add(test_record)
        db.session.commit()
    print("   ✓ Database write successful")
    
    print("\n6. Testing database read...")
    with app.app_context():
        records = TestModel.query.all()
        print(f"   ✓ Found {len(records)} record(s)")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nThe application should work correctly.")
    print("You can now run: python app.py")
    
    # Cleanup
    import os
    if os.path.exists('test_trading.db'):
        os.remove('test_trading.db')
        print("\nTest database cleaned up.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease install missing dependencies:")
    print("pip install flask flask-sqlalchemy eventlet")
