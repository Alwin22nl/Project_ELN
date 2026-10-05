from flask import session

from repositories.change_request_repository import ChangeRequestRepository
from services.change_request_service import ChangeRequestService

def register_notifications_context(app):
    repository = ChangeRequestRepository()
    service = ChangeRequestService(repository)

    @app.context_processor
    def inject_notifications():
        if "user_id" not in session:
            return {
                "show_change_request_bell": False
            }

        show_bell = service.has_open_requests_for_user(
            session["user_id"]
        )

        return {
            "show_change_request_bell": show_bell
        }