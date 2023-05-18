from datetime import datetime, timedelta
from .db_globals import *

def get_next_archive_date() -> datetime:
    collection = db.next_archive_date
    data = collection.find_one({"_id": DATE_ID}, {"_id": 0})
    if data is None:
        raise Exception("Couldn't find document")
    return datetime(data["year"], data["month"], data["day"], data["hour"], data["minute"], data["second"])

def update_next_archive_date(name: str, archive_freq: timedelta, update_db=True) -> str:
    old_date = get_next_archive_date()
    new_date: datetime = old_date + archive_freq
    new_date_fields = {
        "year": new_date.year,
        "month": new_date.month,
        "day": new_date.day,
        "hour": new_date.hour,
        "minute": new_date.minute,
        "second": new_date.second
    }
    if update_db:
        collection = db.next_archive_date
        collection.update_one({"_id": DATE_ID}, {"$set": new_date_fields}, upsert=True)
    month = str(old_date.month)
    day = str(old_date.day)
    year = str(old_date.year)
    return f"{name}-{month}-{day}-{year[len(year) - 2:]}"