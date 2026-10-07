import time

from flask import (
    session,
    request,
    redirect,
    url_for,
    jsonify
)

INACTIVITY_TIMEOUT = 60 * 60 

def register_session_timeout(app):

    @app.before_request
    def check_session_timeout():

        if "user_id" not in session:
            return None

        now = time.time()

        last_activity = session.get(
            "last_activity"
        )

        if last_activity is not None:

            inactive_seconds = (
                now - last_activity
            )

            if inactive_seconds > INACTIVITY_TIMEOUT:
                session.clear()

                if (
                    request.endpoint
                    == "notifications.get_notifications"
                ):

                    return jsonify({
                        "session_expired": True
                    }), 401

                return redirect(
                    url_for(
                        "authentication.login"
                    )
                )

        ignored_endpoints = {
            "notifications.get_notifications"
        }

        if request.endpoint not in ignored_endpoints:

            session["last_activity"] = now

        return None