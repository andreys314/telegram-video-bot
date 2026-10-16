class JobManager:
    def __init__(self):
        self._active_jobs: set[int] = set()

    def is_active(self, user_id: int) -> bool:
        return user_id in self._active_jobs

    def acquire(self, user_id: int) -> bool:
        if self.is_active(user_id):
            return False

        self._active_jobs.add(user_id)
        return True

    def release(self, user_id: int) -> None:
        self._active_jobs.discard(user_id)
