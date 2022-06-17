from flask import Blueprint, jsonify, request, make_response
from project.server.app.service.archive import create_archive, get_task_status, download_local_file

main_blueprint = Blueprint("main_blueprint", __name__)


@main_blueprint.route("/api/archive/create", methods=["POST"])
def run_archive():
    url_json = request.json
    urls = url_json["urls"]
    return create_archive(urls)


@main_blueprint.route("/api/archive/status/<task_id>", methods=["GET"])
def get_status(task_id):
    return jsonify(get_task_status(task_id))


@main_blueprint.route("/archive/get/<file_name>", methods=["GET"])
def get_file(file_name):
    return download_local_file(file_name)