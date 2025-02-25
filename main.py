from db.database import init_db

if __name__ == "__main__":
    init_db()  
    print("✅ Database initialized. Starting the app...")

    # Start API or Scrapers (but NOT Celery!)
    print("🚀 App is running. Start Celery workers separately!")
