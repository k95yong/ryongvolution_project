from flask import Blueprint, jsonify, redirect, url_for, render_template

common_bp = Blueprint('common', __name__)

@common_bp.route("/health_check")
def health_check():
    return jsonify(status="ok"), 200

@common_bp.route('/')
def index_redirect():
    return redirect(url_for('common.home'))

@common_bp.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")
