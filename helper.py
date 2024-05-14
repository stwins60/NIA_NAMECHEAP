import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import datetime
import time
import json


LONGITUDE = "-87.6298"
LATITUDE = "41.8781"
now = datetime.datetime.now()
CURRENT_MONTH = now.month
CURRENT_YEAR = now.year
CURRENT_WEEK_DAY = now.weekday()
CURRENT_DAY = now.day
CURRENT_TIME_HOUR = now.hour
CURRENT_TIME_MINUTE = now.minute

# print(CURRENT_DAY)

url = f"https://api.aladhan.com/v1/calendar?latitude={LATITUDE}&longitude={LONGITUDE}&method=2&month={CURRENT_MONTH}&year={CURRENT_YEAR}"


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# convert to am/pm
def convert_to_am_pm(time):
    time = time.split(":")
    hour = int(time[0])
    # Extract minutes and remove any timezone information
    minute = int(time[1].split()[0])
    if hour > 12:
        hour = hour - 12
        time = f"{hour}:{minute:02d} PM"
    elif hour == 12:
        time = f"{hour}:{minute:02d} PM"
    elif hour == 0:
        hour = 12
        time = f"{hour}:{minute:02d} AM"
    else:
        time = f"{hour}:{minute:02d} AM"
    return time


def get_data():
    # response = requests.get(url)
    response = requests_retry_session().get(url)
    data = response.json()
    # print(data)
    filtered_data = data['data'][CURRENT_DAY - 1]['date']
    return filtered_data

# get prayer times
def get_prayer_times():
    # response = requests.get(url)
    response = requests_retry_session().get(url)
    data = response.json()
    timings = data['data'][CURRENT_DAY - 1]['timings']
    fajr = timings['Fajr']
    sunrise = timings['Sunrise']
    sunset = timings['Sunset']
    dhuhr = timings['Dhuhr']
    asr = timings['Asr']
    maghrib = timings['Maghrib']
    isha = timings['Isha']
    if (
        "(CDT)" in fajr
        or "(CDT)" in sunrise
        or "(CDT)" in sunset
        or "(CDT)" in dhuhr
        or "(CDT)" in asr
        or "(CDT)" in maghrib
        or "(CDT)" in isha
    ):
        fajr = fajr.replace(" (CDT)", "")
        sunrise = sunrise.replace(" (CDT)", "")
        sunset = sunset.replace(" (CDT)", "")
        dhuhr = dhuhr.replace(" (CDT)", "")
        asr = asr.replace(" (CDT)", "")
        maghrib = maghrib.replace(" (CDT)", "")
        isha = isha.replace(" (CDT)", "")

    fajr = convert_to_am_pm(fajr)
    sunrise = convert_to_am_pm(sunrise)
    sunset = convert_to_am_pm(sunset)
    dhuhr = convert_to_am_pm(dhuhr)
    asr = convert_to_am_pm(asr)
    maghrib = convert_to_am_pm(maghrib)
    isha = convert_to_am_pm(isha)
    return fajr, sunrise, sunset, dhuhr, asr, maghrib, isha


# solat = get_prayer_times()
# print(solat)
# print(f"fajr: {solat[0]}")
# print(f"sunrise: {solat[1]}")
# print(f"sunset: {solat[2]}")
# print(f"dhuhr: {solat[3]}")
# print(f"asr: {solat[4]}")
# print(f"maghrib: {solat[5]}")
# print(f"isha: {solat[6]}")


def get_data():
    # response = requests.get(url)
    response = requests_retry_session().get(url)
    data = response.json()
    # print(data)
    filtered_data = data['data'][CURRENT_DAY - 1]
    return filtered_data

def get_gregorian_date():
    data = get_data()
    day = data["date"]["gregorian"]["weekday"]["en"]
    day_num = data["date"]["gregorian"]["day"]
    month = data["date"]["gregorian"]["month"]["en"]
    year = data["date"]["gregorian"]["year"]
    return f"{day}, {month} {day_num}, {year}"

def get_hijri_date():
    data = get_data()
    day = data["date"]["hijri"]["weekday"]["en"]
    day_num = data["date"]["hijri"]["day"]
    month = data["date"]["hijri"]["month"]["en"]
    year = data["date"]["hijri"]["year"]
    designation = data["date"]["hijri"]["designation"]['abbreviated']
    return f"{day_num}, {month}, {year} {designation}"

# print(get_data())

# print(get_gregorian_date())
# print(get_hijri_date())
