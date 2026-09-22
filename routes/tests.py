from flask import Blueprint, render_template

from helper import login_required
from config.test import TEST_PAGES

test_bp = Blueprint(
    "tests",
    __name__
)

@test_bp.route("/tests")
@login_required
def tests():
    return render_template(
        "tests.html",
        tests=TEST_PAGES
    )