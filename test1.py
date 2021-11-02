import time
import atexit
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


def print_date_time():
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


scheduler = BackgroundScheduler(timezone='CET')
today = datetime.today().strftime('%Y-%m-%d') + " 08:40:00"
scheduler.add_job(func=print_date_time, trigger="cron", second="*")
scheduler.start()
