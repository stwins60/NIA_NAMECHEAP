from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, current_app, session
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
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
import sentry_sdk
from prometheus_flask_exporter import PrometheusMetrics
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES
from functools import wraps
import database

app = Flask(__name__)
CORS(app)
token = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))
app.secret_key = token

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

db_pass = DB_PASSWORD.replace('@', '%40')


headers = {
    'Content-Type': 'text/html',
    'charset': 'utf-8',
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
    "Authorization": "Bearer " + token,
}

app.config['UPLOADED_PHOTOS_DEST'] = "static/uploads"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{db_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

db = SQLAlchemy(app)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)



metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Nigeria Islamic Association Website', version='1.0.3')

SESSION_COOKIE_TOKEN = f"nia-session-{''.join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890', 32))}"

sentry_sdk.init(
    dsn="https://5450658eef11bb7d1055b54edfbbf1c7@sentry.africantech.dev/2",
    enable_tracing=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations = [
        AsyncioIntegration(),
        FlaskIntegration(
            transaction_style="url"
        ),
        AioHttpIntegration(
            transaction_style="method_and_path_pattern"
        )
    ]
)
load_dotenv()
# SITE ENVIRONMENT VARIABLES
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


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

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"User('{self.username}')"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session and session['logged_in'] and session['current_user']:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return decorated_function


@app.route('/')
@app.route('/index')
@metrics.histogram('index_histogram', 'Request duration for index page')
@metrics.gauge('index_gauge', 'Request gauge for index page')
@metrics.summary('index_summary', 'Request summary for index page')
def index():
    quran_thread = threading.Thread(target=sync_get_verse)
    quran_thread.start()
    quran_thread.join()
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

    images_db = Image.query.all()
    images = []
    for image in images_db:
        images.append(image.filename)
    # images = os.getenv('IMAGE')
    multiple_images = images

    
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
            quran_verse_no = quran_verse_no,
            multiple_images=multiple_images
        ), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response


@app.route('/about')

@metrics.histogram('about_histogram', 'Request duration for about page')
@metrics.gauge('about_gauge', 'Request gauge for about page')
@metrics.summary('about_summary', 'Request summary for about page')
def about():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('about.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/services')

@metrics.histogram('services_histogram', 'Request duration for services page')
@metrics.gauge('services_gauge', 'Request gauge for services page')
@metrics.summary('services_summary', 'Request summary for services page')
def services():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('services.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/projects')

@metrics.histogram('projects_histogram', 'Request duration for projects page')
@metrics.gauge('projects_gauge', 'Request gauge for projects page')
@metrics.summary('projects_summary', 'Request summary for projects page')
def projects():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('projects.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/services2')

@metrics.histogram('services2_histogram', 'Request duration for services2 page')
@metrics.gauge('services2_gauge', 'Request gauge for services2 page')
@metrics.summary('services2_summary', 'Request summary for services2 page')
def services2():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('services2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/services-detail')

@metrics.histogram('services_detail_histogram', 'Request duration for services_detail page')
@metrics.gauge('services_detail_gauge', 'Request gauge for services_detail page')
@metrics.summary('services_detail_summary', 'Request summary for services_detail page')
def services_detail():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('services-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/events')

@metrics.histogram('events_histogram', 'Request duration for events page')
@metrics.gauge('events_gauge', 'Request gauge for events page')
@metrics.summary('events_summary', 'Request summary for events page')
def events():
    solat_times = helper.get_prayer_times()
    sunset = solat_times[2]
    sunrise = solat_times[1]
    response = make_response(render_template('events.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/event-detail')

@metrics.histogram('event_detail_histogram', 'Request duration for event_detail page')
@metrics.gauge('event_detail_gauge', 'Request gauge for event_detail page')
@metrics.summary('event_detail_summary', 'Request summary for event_detail page')
def event_detail():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('event-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/donation-detail')

@metrics.histogram('donation_detail_histogram', 'Request duration for donation_detail page')
@metrics.gauge('donation_detail_gauge', 'Request gauge for donation_detail page')
@metrics.summary('donation_detail_summary', 'Request summary for donation_detail page')
def donation_detail():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('donation-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/urgent-donation')

@metrics.histogram('urgent_donation_histogram', 'Request duration for urgent_donation page')
@metrics.gauge('urgent_donation_gauge', 'Request gauge for urgent_donation page')
@metrics.summary('urgent_donation_summary', 'Request summary for urgent_donation page')
def urgent_donation():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('urgent-donation.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/gallery')

@metrics.histogram('gallery_histogram', 'Request duration for gallery page')
@metrics.gauge('gallery_gauge', 'Request gauge for gallery page')
@metrics.summary('gallery_summary', 'Request summary for gallery page')
def gallery():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('gallery.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/gallery2')

def gallery2():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('gallery2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/gallery3')

def gallery3():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('gallery3.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/scholar-style1')

def scholar_style1():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('scholar-style1.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/scholar-style2')

def scholar_style2():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('scholar-style2.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/scholar-detail')

def scholar_detail():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('scholar-detail.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.route('/audio-listening')

@metrics.histogram('audio_listening_histogram', 'Request duration for audio_listening page')
@metrics.gauge('audio_listening_gauge', 'Request gauge for audio_listening page')
@metrics.summary('audio_listening_summary', 'Request summary for audio_listening page')
def audio_listening():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    response = make_response(render_template('audio-listening.html', sunrise=sunrise, sunset=sunset), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/contact', methods=['GET', 'POST'])

@metrics.histogram('contact_histogram', 'Request duration for contact page')
@metrics.gauge('contact_gauge', 'Request gauge for contact page')
@metrics.summary('contact_summary', 'Request summary for contact page')
def contact():
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    
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

@app.route('/admin')
@metrics.histogram('admin_histogram', 'Request duration for admin page')
@metrics.gauge('admin_gauge', 'Request gauge for admin page')
@metrics.summary('admin_summary', 'Request summary for admin page')
@login_required
def admin():
    images = Image.query.all()
    solat_times = helper.get_prayer_times()
    sunrise = solat_times[1]
    sunset = solat_times[2]
    
    response = make_response(
        render_template(
            'admin.html',
            images=images,
            sunrise=sunrise,
            sunset=sunset
            
        ), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.route('/upload', methods=['POST'])
@metrics.histogram('upload_histogram', 'Request duration for upload page')
@metrics.gauge('upload_gauge', 'Request gauge for upload page')
@metrics.summary('upload_summary', 'Request summary for upload page')
@login_required
def upload():
    if request.method == 'POST':
        if 'image' in request.files:
            print(request.files['image'])
            filename = photos.save(request.files['image'])
            new_image = Image(filename=filename)
            db.session.add(new_image)
            db.session.commit()
            flash('Image uploaded successfully')
        return redirect(url_for('admin'))

@app.route('/delete/<int:image_id>', methods=['POST'])
@metrics.histogram('delete_histogram', 'Request duration for delete page')
@metrics.gauge('delete_gauge', 'Request gauge for delete page')
@metrics.summary('delete_summary', 'Request summary for delete page')
@login_required
def delete(image_id):
    image = Image.query.get(image_id)
    if image:
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image.filename))
        db.session.delete(image)
        db.session.commit()
        flash('Image deleted successfully')
    return redirect(url_for('admin'))

@app.route('/admin/login', methods=['GET', 'POST'])
@metrics.histogram('admin_login_histogram', 'Request duration for admin_login page')
@metrics.gauge('admin_login_gauge', 'Request gauge for admin_login page')
@metrics.summary('admin_login_summary', 'Request summary for admin_login page')
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['current_user'] = username
            flash('You are now logged in')
            return redirect(url_for('admin'))
        else:
            flash('Invalid login')
    return render_template('admin-login.html')

@app.route('/admin/logout')
@metrics.histogram('admin_logout_histogram', 'Request duration for admin_logout page')
@metrics.gauge('admin_logout_gauge', 'Request gauge for admin_logout page')
@metrics.summary('admin_logout_summary', 'Request summary for admin_logout page')
def admin_logout():
    session['logged_in'] = False
    session['current_user'] = None
    flash('You are now logged out')
    return redirect(url_for('admin_login'))

@app.route('/site_maintenance')
@metrics.histogram('site_maintenance_histogram', 'Request duration for site_maintenance page')
@metrics.gauge('site_maintenance_gauge', 'Request gauge for site_maintenance page')
@metrics.summary('site_maintenance_summary', 'Request summary for site_maintenance page')
def site_maintenance():
    response = make_response(render_template('site_maintenance.html'), headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)

    return response

@app.errorhandler(404)
def page_not_found(e):
    response = make_response(render_template('404.html'),404)
    response.headers.update(headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response

@app.errorhandler(500)
def internal_server_error(e):
    response = make_response(render_template('500.html'),500)
    response.headers.update(headers)
    response.set_cookie('site-cookie', SESSION_COOKIE_TOKEN)
    return response


@app.route('/health')

@metrics.histogram('health_histogram', 'Request duration for health page')
@metrics.gauge('health_gauge', 'Request gauge for health page')
@metrics.summary('health_summary', 'Request summary for health page')
def health_check():
    response = make_response(jsonify({"status": "ok"}), 200)
    return response


@app.route('/ready')
@metrics.histogram('ready_histogram', 'Request duration for ready page')
@metrics.gauge('ready_gauge', 'Request gauge for ready page')
@metrics.summary('ready_summary', 'Request summary for ready page')
def readiness_check():
    response = make_response(jsonify({"status": "ok"}), 200)
    return response

# metrics.register_endpoint(health_check)
# metrics.register_endpoint(readiness_check)


# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5000)