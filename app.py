import os
from flask import Flask, render_template, request, redirect, send_file

from s3 import list_buckets, created_folder

app = Flask(__name__)
BUCKET = "tiger-mle-pg"

@app.route("/")
def entry_point():
    return render_template("index.html")


@app.route("/storage")
def storage():
    contents = list_buckets()
    return render_template("layout.html", contents=contents)


@app.route("/files")
def myfiles():
    f = created_folder()
    return render_template("storage.html", contents=f)

if __name__=="__main__":
    app.run(host='0.0.0.0', port=5003, debug=True)