from Context_processors.notifications import register_notifications_context

def register_context_processors(app):
    register_notifications_context(app)