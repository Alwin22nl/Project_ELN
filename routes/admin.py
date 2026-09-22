from flask import(
    Blueprint,
    render_template,
    request
)

from helper import login_required, admin_required

from repositories.admin_repository import AdminRepository
from services.admin_service import AdminService

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

repository = AdminRepository()
service = AdminService(repository)

@admin_bp.route("/")
@login_required
@admin_required
def admin_page():

    users = service.get_admin_overview()

    return render_template(
        "admin/admin.html",
        users=users
    )

@admin_bp.route("/audit_logs")
@login_required
@admin_required
def audit_logs_admin():

    logs = service.get_audit_logs()

    return render_template(
        "admin/audit_logs.html",
        logs=logs
    )

@admin_bp.route("/reset_password/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def reset_password(user_id):
    temp_password = service.reset_password(user_id)

    return render_template(
        "admin/password_reset.html",
        password=temp_password
    )

@admin_bp.route("/create_user", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        role = request.form["user_role"]

        temp_password = service.create_user(
            username=username,
            name=name,
            role=role
        )

        return render_template(
            "admin/user_created.html",
            username=username,
            password=temp_password
        )
    return render_template("admin/create_user.html")