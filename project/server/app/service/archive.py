import redis

from rq import Queue, Connection
from flask import current_app
from project.server.app.util.tasks import start_archiving, prepare_task_status_response, prepare_task_acceptance_response
from project.server.app.constant.constants import WORKING_DIRECTORY
from flask import send_file


def create_archive(urls):
    try:
        with Connection(redis.from_url(current_app.config["REDIS_URL"])):
            archiving_queue = Queue()
            task = archiving_queue.enqueue(start_archiving, urls)

        response = prepare_task_acceptance_response(True, task.get_id(), None)
        status_code = 202
    except Exception as e:
        response = prepare_task_acceptance_response(False, None, e)
        status_code = 500

    return response, status_code


def get_task_status(task_id):
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        archiving_queue = Queue()
        task = archiving_queue.fetch_job(task_id)

    status = "error"
    task_result = None
    if task:
        status = "completed"
        task_result = None
        if task.is_finished:
            task_result = task.result
        elif task.is_queued:
            status = 'in-queue'
        elif task.is_started:
            status = 'in-progress'
        elif task.is_failed:
            status = 'failed'
    else:
        status = 'task with id %s does not exist' % task_id

    return prepare_task_status_response(status, task_result)


def download_local_file(file_name):
    path = WORKING_DIRECTORY + file_name
    return send_file(path)