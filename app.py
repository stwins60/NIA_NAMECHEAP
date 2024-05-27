from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_cors import CORS
from mailer import sendMyEmail, ValidateEmail
import os
import random
import helper
import quranVerse
import random
import aiohttp
import asyncio
import threading
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk


app = Flask(__name__)
CORS(app)
token = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
app.secret_key = token

headers = {
    'Content-Type': 'text/html',
    'charset': 'utf-8',
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
    "Authorization": "Bearer " + token,
}

SESSION_COOKIE_TOKEN = f"nia-session-{''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))}"

sentry_sdk.init(
    dsn="https://5450658eef11bb7d1055b54edfbbf1c7@sentry.africantech.dev/2",
    enable_tracing=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations = [
        FlaskIntegration(
            transaction_style="url"
        )
    ]
)

def get_random_verse():
    verse = random.randint(1, 6236)
    return verse

async def fetch_verse(session, verse):
    url = f'http://api.alquran.cloud/ayah/{verse}/editions/quran-uthmani,en.asad'
    async with session.get(url) as response:
        data = await response.json()
        verse_a = data['data'][0]['text']
        verse_en = data['data'][1]['text']
        sura = data['data'][0]['surah']['englishName'] + '(' + str(data['data'][0]['surah']['number']) + '):' + str(data['data'][0]['numberInSurah'])
        return verse_a, verse_en, sura

async def get_verse():
    verse = get_random_verse()
    async with aiohttp.ClientSession() as session:
        return await fetch_verse(session, verse)

def sync_get_verse():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_verse())


@app.route('/')
@app.route('/index')
def index():
    quran_thread = threading.Thread(target=sync_get_verse)
    quran_thread.start()
    quran_thread.join()
    # return render_template('index.html')
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    
    quran_verse_a, quran_verse_en, sura = sync_get_verse()
    quran_chapter_no = sura.split(':')[0].split(')')[0]
    quran_chapter_no = quran_chapter_no.split('(')[1]
    quran_verse_no = sura.split(':')[1].split(')')[0]

    
    response = make_response(
        render_template(
            'index.html',
            fajr=fajr,
            sunrise=sunrise,
            sunset=sunset,
            dhuhr=dhuhr,
            asr=asr,
            maghrib=maghrib,
            isha=isha,
            geogorian_date=geogorian_date,
            hijri_date=hijri_date,
            quran_verse_a=quran_verse_a,
            quran_verse_en=quran_verse_en,
            quran_chapter_no = quran_chapter_no,
            quran_verse_no = quran_verse_no
        ), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/index2')
def index2():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('index2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/index3')
def index3():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('index3.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/about')
def about():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('about.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/services')
def services():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('services.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/projects')
def projects():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    
    response = make_response(render_template('projects.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/services2')
def services2():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('services2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/services-detail')
def services_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('services-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/blog')
def blog():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('blog.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/blog-detail')
def blog_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('blog-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/blog2')
def blog2():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('blog2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/events')
def events():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('events.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/event-detail')
def event_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('event-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/donation-detail')
def donation_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('donation-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/urgent-donation')
def urgent_donation():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('urgent-donation.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/gallery')
def gallery():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('gallery.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/gallery2')
def gallery2():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('gallery2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/gallery3')
def gallery3():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('gallery3.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/products')
def products():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('products.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/product-detail')
def product_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('product-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/cart')
def cart():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('cart.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/checkout')
def checkout():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('checkout.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/online-courses')
def online_courses():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('online-courses.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/online-courses-detail')
def online_courses_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('online-courses-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/scholar-style1')
def scholar_style1():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('scholar-style1.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/scholar-style2')
def scholar_style2():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('scholar-style2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/scholar-detail')
def scholar_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('scholar-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/sermons')
def sermons():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('sermons.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/sermons-detail')
def sermons_detail():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('sermons-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/audio-listening')
def audio_listening():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    response = make_response(render_template('audio-listening.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    solat_times = helper.get_prayer_times()
    geogorian_date = helper.get_gregorian_date()
    hijri_date = helper.get_hijri_date()
    fajr = solat_times[0]
    sunrise = solat_times[1]
    sunset = solat_times[2]
    dhuhr = solat_times[3]
    asr = solat_times[4]
    maghrib = solat_times[5]
    isha = solat_times[6]
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_num = request.form['tel']
        msg = request.form['message']
        subject = "NIA Enquiry"
        if name == '' or email == '' or phone_num == '' or msg == '':
            flash('Please fill in all the fields')
            return redirect(url_for('contact'))
        if not ValidateEmail(email):
            flash('Please enter a valid email address')
            return redirect(url_for('contact'))
        sendMyEmail(subject, msg, phone_num, name, email)
        flash('Your message has been sent successfully!')
        return redirect(url_for('contact'))
    response = make_response(render_template('contact.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/site_maintenance')
def site_maintenance():
    response = make_response(render_template('site_maintenance.html'), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template('404.html'), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.errorhandler(500)
def internal_server_error(e):
    response = make_response(render_template('500.html'), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response


# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5000)