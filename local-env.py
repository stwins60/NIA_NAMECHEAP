from app import db
import app


if __name__ == '__main__':
    with app.app.app_context():
        db.create_all()
    app.app.run(debug=True, host='0.0.0.0', port=5000)