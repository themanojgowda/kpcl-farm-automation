#!/usr/bin/env python3
"""
Test script to verify scd_enq.py functionality
"""

from datetime import datetime
from myjobs import greet

def test_greet_function():
    """Test the greet function directly"""
    print("🧪 Testing greet function:")
    greet("Test User")
    print()

def test_scheduled_datetime():
    """Test the scheduled datetime calculation"""
    year = 2025
    month = 7
    day = 14
    hour = 23  # mention in 24 hours format 
    minute = 40
    seconds = 50
    
    scheduled_time = datetime(year, month, day, hour, minute, seconds)
    current_time = datetime.now()
    
    print(f"🕐 Scheduled execution time: {scheduled_time}")
    print(f"🕐 Current time: {current_time}")
    
    if scheduled_time > current_time:
        print(f"⏰ Job will run in the future ({scheduled_time - current_time} from now)")
    else:
        print(f"⚠️  Scheduled time is in the past ({current_time - scheduled_time} ago)")
    print()

def test_redis_connection():
    """Test Redis connection (optional)"""
    try:
        from redis import Redis
        from rq import Queue
        
        # Try to connect to Redis
        redis_conn = Redis()
        redis_conn.ping()
        print("✅ Redis server is running and accessible")
        
        queue = Queue(name='default', connection=redis_conn)
        print(f"✅ Queue created successfully: {queue}")
        
    except Exception as e:
        print(f"❌ Redis not available: {e}")
        print("💡 To use RQ functionality, start Redis server:")
        print("   docker run -d --name redis -p 6379:6379 redis")
        print("   or install Redis locally")
    print()

if __name__ == "__main__":
    print("🚀 Testing KPCL Farm Automation - RQ Scheduler Components\n")
    
    test_greet_function()
    test_scheduled_datetime()
    test_redis_connection()
    
    print("✅ All tests completed!")
