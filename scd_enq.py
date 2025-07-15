from datetime import datetime
from rq import Queue
from redis import Redis
from myjobs import greet
from submit_proof import run_batch_requests_for_user
from submit_proof import send_request
# Connect to Redis

def schedule_job(session):
    """Schedule a job to run at a specific time."""

    try:
        redis_conn = Redis()
        queue = Queue(name='default', connection=redis_conn)
        
        # Set the schedule time (update as needed)

        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day  # Use current date
        # year = 2025
        # month = 7
        # day = 15  # Updated to current date
        hour = 22  # mention in 24 hours format 
        minute = 54
        seconds = 30
        seconds2 = 40

        scheduled_time = datetime(year, month, day, hour, minute, seconds)
        scheduled_time2 = datetime(year, month, day, hour, minute, seconds2)
        current_time = datetime.now()
        
        if scheduled_time > current_time:
            job = queue.enqueue_at(scheduled_time, send_request, session)
            job2 = queue.enqueue_at(scheduled_time2, send_request, session)
            print(f"✅ Job scheduled successfully!")
            print(f"Job {job2.id} scheduled successfully!")
            print(f"🕐 Execution time: {scheduled_time}")
            print(f"📋 Job ID: {job.id}")
        else:   
            print(f"⚠️  Scheduled time {scheduled_time} is in the past!")
            print(f"🕐 Current time: {current_time}")
            print("💡 Please update the year, month, day, hour, minute, or seconds")
            
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")
        print("💡 Make sure Redis server is running:")
        print("   docker run -d --name redis -p 6379:6379 redis")
