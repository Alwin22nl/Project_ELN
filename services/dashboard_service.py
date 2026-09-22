

class DashboardService:
    def __init__(self, repository):
        self.repository = repository

    def get_dashboard_context(self):
        data = self.repository.get_dashboard_data()

        return {
            key: value
            for key, value in data.items()
            if value
        }

    def place_afterstorage(self, sample_id, oven_location):
        self.repository.place_afterstorage(sample_id, oven_location)

    def remove_afterstorage(self, afterstorage_id):
        self.repository.remove_afterstorage(afterstorage_id)
        