import threading
import schedule
import time
from collections import defaultdict
import requests
from datetime import datetime
from values import url_proof_upload, payload_proof_upload
# user_sessions = defaultdict(requests.Session)
from logger_setup import logger


schedule_time = "18:38:00"  # Time to run the task daily
interval_seconds = 3  # Interval between requests in seconds
limit_requests = 30  # Limit the number of requests

def send_request(n, session):
    logger.info(f"📤 Request #{n+1} for {session} at {datetime.now()}")
    try:
        response = session.post(url_proof_upload, data=payload_proof_upload)
        logger.info(f"✅ {session} response: {response.status_code}, response text: {response.text}")
    except Exception as e:
        logger.error(f"❌ {session} request failed: {e}")

def run_batch_requests_for_user(session):
    for i in range(limit_requests):
        threading.Timer(interval_seconds * i, send_request, args=(i, session)).start()

# def schedule_user_task(session):
#     schedule.every().day.at(schedule_time).do(run_batch_requests_for_user, session=session)
#     logger.info(f"📅 Task scheduled for {session} at {schedule_time}")


# # Background scheduler thread
# def run_scheduler_forever():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# # Start the scheduler loop in a background thread (once, globally)
# scheduler_thread = threading.Thread(target=run_scheduler_forever, daemon=True)
# scheduler_thread.start()
