from tools import get_events, times_between_events, group_events, filter_events_last_minutes
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
    # Return the received strings as a JSON response
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


# index to show info

# endpoint for average times between events
# endpoint for grouped event info by offset

# times_between_events(events)
# group_events(filter_events_last_minutes(events, 60))