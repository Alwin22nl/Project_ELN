from flask import session, current_app

from repositories.notifications_repository import NotificationsRepository
from services.notifications_service import NotificationsService

def register_notifications_context(app):
    repository = NotificationsRepository()
    service = NotificationsService(repository)

    @app.context_processor
    def inject_notifications():
        if "user_id" not in session:
            return {
                "show_change_request_bell": False
            }

        try:
            show_bell = service.has_active_notifications(
                session["user_id"]
            )

        except Exception:
            current_app.logger.exception(
                "Could not load notifications"
            )

            show_bell = False

        return {
            "show_notifications_bell": show_bell
        }