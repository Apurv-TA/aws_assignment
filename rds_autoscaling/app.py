from flask import Flask, render_template, url_for

from rds import all_db, update_df

app = Flask(__name__)

@app.route("/")
def entry_point():
    update_df(url_for("entry_point"))
    contents = all_db()
    return render_template("index.html", contents=contents)


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run()
