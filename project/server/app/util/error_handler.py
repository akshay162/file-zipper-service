from flask import Blueprint, jsonify, make_response

error_blueprint = Blueprint("error_blueprint", __name__)


@error_blueprint.errorhandler(404)
def handle_404_error(_error):
    return make_response(jsonify({'error': 'Not Found'}), 404)


@error_blueprint.errorhandler(500)
def handle_404_error(_error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)