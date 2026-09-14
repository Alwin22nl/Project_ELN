from flask import(
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    session
)

from helper import login_required

from repositories.authentication_repository import AuthenticationRepository
from services.authentication_service import AuthenticationService

authentication_bp = Blueprint(
    "authenication",
    __name__
)

repository = AuthenticationRepository()
service = AuthenticationService(repository)

@authentication_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        user = service.authenticate(
            username=request.form["username"],
            password=request.form["password"]
        )

        if not user:
            return render_template(
                "login.html",
                error="Onjuist Username of Wachtwoord"
            )

        #clear old session before login
        session.clear()

        session.permanent = True

        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["name"] = user["name"]

        if user["must_change_password"]:
            return redirect(
                url_for("authentication.change_password")
            )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html",
    )

@authentication_bp.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        password_changed = service.change_password(
            user_id=session["user_id"],
            password1=request.form["password1"],
            password2=request.form["password2"]
        )

        if not password_changed:
            return render_template(
                "change_password.html",
                error="Wachtwoorden komen niet overeen"
            )

        return redirect("dashboard")

    return render_template(
        "change_password.html"
    )