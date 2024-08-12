from flask import Flask, jsonify, request
from tools import Repository, RepositoryManager


repositoryManager = RepositoryManager()

app = Flask(__name__)


# Index endpoint
@app.route('/')
def index():
    return "Hello, this is the index page!"


# Endpoint to add new repository to be tracked
@app.route('/add-repository/<profile_name>/<repository_name>', methods=['POST'])
def add_repository(profile_name, repository_name):
    repository = Repository(profile_name, repository_name)
    success, message = repositoryManager.add_repository(repository)
    status_code = 200 if success else 400
    return jsonify({"message": message}), status_code


# Endpoint to show all currently tracked repositories
@app.route('/get-repositories', methods=['GET'])
def get_repositories():
    tracked_repos = []
    for repository in repositoryManager.get_repositories():
        tracked_repos.append(repository.get_info())
    return jsonify({"tracked_repositories": tracked_repos}), 200


# Endpoint to delete a tracked repository
@app.route('/delete-repository/<profile_name>/<repository_name>', methods=['DELETE'])
def delete_repository(profile_name, repository_name):
    repository = Repository(profile_name, repository_name)
    success, message = repositoryManager.delete_repository(repository)
    status_code = 200 if success else 400
    return jsonify({"message": message}), status_code


# Endpoint get average times (in seconds) between consecutive events grouped by event types
@app.route('/get-event-times', methods=['GET'])
def get_event_times():
    result = []
    for repository in repositoryManager.get_repositories():
        print(f'repisotory {repository.get_info()} included')
        result.append((repository.get_info(), repository.times_between_events()))
    return jsonify({"average times between events": result}), 200


# endpoint for grouped event info by offset
@app.route('/get-events-by-offset/<minutes>', methods=['GET'])
def get_events_by_offset(minutes):
    minutes = int(minutes)
    result = []
    for repository in repositoryManager.get_repositories():
        result.append((repository.get_info(), repository.group_events(minutes)))
    return jsonify({f'events grouped by event type, repo for the last {minutes} minutes': result}), 200


# Endpoint to send GitHub access token in a header
@app.route('/send-token', methods=['POST'])
def send_token():
    token_set, message = repositoryManager.set_token(request.headers.get('Authorization'))
    status_code = 200 if token_set else 400
    return jsonify({"message": message}), status_code