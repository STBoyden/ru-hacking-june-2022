from flask import Flask, request, jsonify

app = Flask("poké-phone")

@app.get("/")
def root():
    return jsonify("Hello, world!")
