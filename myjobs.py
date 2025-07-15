from datetime import datetime
from submit_proof import run_batch_requests_for_user
def greet(name="default"):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Hello, {name}! This is your scheduled greeting.")

# RQ worker commands and Docker setup
# rq worker --with-scheduler
# docker run -d \
#   --name redis \
#   -p 6379:6379 \
#   redis

# python scd_enq.py
