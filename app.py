# import full library's
import os
import secrets
import string
import calendar
import re

# import partial library's
from dotenv import load_dotenv
from flask import session, Flask, render_template, request, redirect, url_for, jsonify
from database import get_connection, get_dict_cursor
from datetime import date, timedelta, datetime
from numbers import Real
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# importing other Py files
from config.test import TEST_PAGES, OVERVIEW_TESTS
from helper import log_change, login_required, admin_required, generate_temp_password, format_datetime

#importing routes
from routes.authentication import authentication_bp
from routes.admin import admin_bp
from routes.samples import sample_bp
from routes.dashboard import dashboard_bp
from routes.products import product_bp
from routes.overview import overview_bp
from routes.batch_search import batch_search_bp

# importing Test Routes
from routes.tests import test_bp
from routes.rheology import rheology_bp
from routes.skinformation import skinformation_bp
from routes.initial_tack import initial_tack_bp
from routes.density import density_bp
from routes.shore_a import shore_a_bp
from routes.adhesion import adhesion_bp
from routes.epdm_adhesion import epdm_adhesion_bp
from routes.curability import curability_bp
from routes.tensile import tensile_bp

load_dotenv()
today = date.today()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(hours=1)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

# routes
app.register_blueprint(authentication_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(sample_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(product_bp)
app.register_blueprint(overview_bp)
app.register_blueprint(batch_search_bp)

# test routes
app.register_blueprint(test_bp)
app.register_blueprint(rheology_bp)
app.register_blueprint(skinformation_bp)
app.register_blueprint(initial_tack_bp)
app.register_blueprint(density_bp)
app.register_blueprint(shore_a_bp)
app.register_blueprint(adhesion_bp)
app.register_blueprint(epdm_adhesion_bp)
app.register_blueprint(curability_bp)
app.register_blueprint(tensile_bp)

@app.route("/users")
@login_required
def users():

    return "Users page"

if __name__ == "__main__":
    app.run(debug=True)