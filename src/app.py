from flask import Flask

app = Flask(__name__, template_folder="pages")

from routes import home

if __name__ == "__main__":
    app.run(debug=True)

