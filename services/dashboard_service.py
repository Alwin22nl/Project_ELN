

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
        if self.repository.afterstorage_place_exists(sample_id):
            raise ValueError("Deze Batch is al in de oven geplaatst!")

        self.repository.place_afterstorage(sample_id, oven_location)

    def remove_afterstorage(self, sample_id, afterstorage_id):
        if self.repository.afterstorage_remove_exists(sample_id):
            raise ValueError("Deze Batch is al uit de oven gehaald!")
            
        self.repository.remove_afterstorage(afterstorage_id)
        