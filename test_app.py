import pytest
from flask import Flask, session
from app import app as flask_app  # Import the Flask app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Nigerian Islamic Association' in response.data
    
def test_about(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b"""Shakiru Nasiru""" in response.data

def test_contact(client):
    response = client.get('/contact')
    assert response.status_code == 200
    assert b'niaexecutiveboard@gmail.com' in response.data
    
def test_projects(client):
    response = client.get('/projects')
    assert response.status_code == 200
    assert b'Southside Islamic Center' in response.data

def test_services(client):
    response = client.get('/services')
    assert response.status_code == 200
    assert b'Community Service' in response.data
    
def test_gallery(client):
    response = client.get('/gallery')
    assert response.status_code == 200
    assert b'NIA Gallery' in response.data
    
def test_donate(client):
    response = client.get('/donation-detail')
    assert response.status_code == 200
    assert b'DONATE NOW' in response.data
    
def test_events(client):
    response = client.get('/events')
    assert response.status_code == 200
    assert b'Events' in response.data
    
def test_audio_listening(client):
    response = client.get('/audio-listening')
    assert response.status_code == 200
    assert b'Quran Recitations' in response.data

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_readiness_check(client):
    response = client.get('/ready')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_page_not_found(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_site_maintenance(client):
    response = client.get('/site_maintenance')
    assert response.status_code == 200
    assert 'site-cookie' in response.headers.get('Set-Cookie')

def test_admin_login(client):
    response = client.get('/admin/login')
    assert response.status_code == 200
    assert b'LOGIN' in response.data

def test_admin_logout(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True
    response = client.get('/admin/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/admin/login'
    with client.session_transaction() as sess:
        assert not sess.get('logged_in')


