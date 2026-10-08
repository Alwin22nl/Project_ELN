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

    notifications = (
        service.get_notification_summary(
            session["user_id"]
        )
    )

    has_unread = any(
        notification["unread_count"] > 0
        for notification in notifications
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