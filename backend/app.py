from flask import Flask
from flask_cors import CORS
from models import init_db

app = Flask(__name__)
CORS(app)


@app.route("/")
def health_check():
    return {"status": "Backend running"}, 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
