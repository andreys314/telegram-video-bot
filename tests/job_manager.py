from bot.job_manager import JobManager


def test_job_lifecycle():
    manager = JobManager()
    user_id = 123

    assert manager.acquire(user_id) is True
    assert manager.is_active(user_id) is True

    assert manager.acquire(user_id) is False

    manager.release(user_id)

    assert manager.is_active(user_id) is False
    assert manager.acquire(user_id) is True
