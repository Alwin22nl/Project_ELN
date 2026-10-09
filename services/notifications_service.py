from config.test import NOTIFICATION_CONFIG

class NotificationsService:
    def __init__(self, repository):
        self.repository = repository

    def get_active_notifications(self, user_id):
        return self.repository.get_active_notifications(user_id)

    def has_active_notifications(self, user_id):
        return self.repository.has_active_notifications(user_id)

    def create_notification(
            self,
            user_id,
            notification_type,
            title,
            message=None,
            reference_type=None,
            reference_id=None,
            link=None
    ):
        self.repository.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
            link=link
        )

    def close_notification(self, reference_type, reference_id):
        self.repository.deactivate_notification(
            reference_type,
            reference_id
        )

    def get_other_users(self, exclude_user_id):
        return self.repository.get_other_users(exclude_user_id)

    def mark_notifications_read(self, user_id):
        self.repository.mark_notifications_read(user_id)

    def has_unread_active_notifications(self, user_id):
        return (
            self.repository.has_unread_active_notifications(user_id)
        )

    def close_change_request_notifications(self, change_request_id):
        self.repository.close_notifications(
            reference_type="change_request",
            reference_id=change_request_id
        )

    def get_notification_summary(self, user_id):
        rows = self.repository.get_notification_summary(user_id)

        notifications = []

        for row in rows:
            notification_type = row["notification_type"]
            config = NOTIFICATION_CONFIG.get(notification_type)

            if config is None:
                continue

            notifications.append({
                "type": notification_type,
                "title": config["title"],
                "message": config["message"],
                "link": config["link"],
                "count": row["active_count"],
                "unread_count": row["unread_count"]
            })

        return notifications