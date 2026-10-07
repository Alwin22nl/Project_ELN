from flask import Blueprint, jsonify, session
from helper import login_required

from repositories.notifications_repository import NotificationsRepository
from services.notifications_service import NotificationsService

notification_bp = Blueprint(
    "notifications",
    __name__
)

repository = NotificationsRepository()
service = NotificationsService(repository)

@notification_bp.route("/notifications")
@login_required
def get_notifications():

    user_id = session["user_id"]

    rows = service.get_active_notifications(
        user_id
    )

    notifications = []

    for row in rows:
        notifications.append({
            "id": row["notification_id"],
            "type": row["notification_type"],
            "title": row["title"],
            "message": row["message"],
            "link": row["link"],
            "is_read": row["is_read"]
        })

    has_unread = (
        service.has_unread_active_notifications(
            user_id
        )
    )

    return jsonify({
        "has_unread": has_unread,
        "notifications": notifications
    })

@notification_bp.route("/notifications/mark-read",methods=["POST"])
@login_required
def mark_notifications_read():
    service.mark_notifications_read(
        session["user_id"]
    )

    return jsonify({
        "success": True
    })