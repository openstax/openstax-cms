from logging import Filter

class HealthCheckFilter(Filter):
    def filter(self, record):
        # Should return True for all requests except successful healthcheck requests
        return record.status_code != 204 or not (
            record.args[0].startswith('GET /ping ') or
            record.args[0].startswith('GET /ping/')
        )
