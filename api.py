from flask import Flask, jsonify, request, Response
from tools import Repository, RepositoryManager

import matplotlib.pyplot as plt
import numpy as np
import io
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend


repositoryManager = RepositoryManager()

app = Flask(__name__)


# Index endpoint
@app.route('/')
def index():
    return  "Available endpoints:\n\n" +\
            "/send-token\n" +\
            "/add-repository/profile_name/repository_name\n" +\
            "/get-repositories\n" +\
            "/delete-repository/profile_name/repository_name\n" +\
            "/get-event-times\n" +\
            "/get-events-by-offset/minutes\n" +\
            "/visual-events-by-offset/minutes\n"


# Endpoint to send GitHub access token in a header
@app.route('/send-token', methods=['POST'])
def send_token():
    token_set, message = repositoryManager.set_token(request.headers.get('Authorization'))
    status_code = 200 if token_set else 400
    return jsonify({"message": message}), status_code


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
        result.append((repository.get_info(), 
                       repository.times_between_events(repositoryManager.get_token())))
    return jsonify({"average times between events": result}), 200


# Endpoint for grouped repopositories' event info by offset
@app.route('/get-events-by-offset/<minutes>', methods=['GET'])
def get_events_by_offset(minutes):
    result = []
    for repository in repositoryManager.get_repositories():
        result.append((repository.get_info(), 
                       repository.group_events(minutes, repositoryManager.get_token())))
    return jsonify({f'events grouped by repository and event type for the last {minutes} minutes': result}), 200


# Endpoint for grouped repopositories' event info by offset visualization
@app.route('/visual-events-by-offset/<minutes>', methods=['GET'])
def visual(minutes): 
    repo_names = [repo.get_info() for repo in repositoryManager.get_repositories()]
    watch_events, pull_request_events, issues_events = [], [], []
    
    for repository in repositoryManager.get_repositories():
        repo_events = repository.group_events(minutes, repositoryManager.get_token())
    
        watch_events.append(repo_events.get('WatchEvent', 0))
        pull_request_events.append(repo_events.get('PullRequestEvent', 0))
        issues_events.append(repo_events.get('IssuesEvent', 0))
    
    x = np.arange(len(repo_names))
    width = 0.2

    _, ax = plt.subplots()
    ax.bar(x - width, watch_events, width, label='WatchEvent', color='r')
    ax.bar(x, pull_request_events, width, label='PullRequestEvent', color='g')
    ax.bar(x + width, issues_events, width, label='IssuesEvent', color='b')

    ax.set_xticks(x)
    ax.set_xticklabels(repo_names, rotation=45, ha='right')
    ax.legend()

    img = io.BytesIO()  # Save the plot to a BytesIO object
    plt.savefig(img, format='png') # Save as PNG in memory
    img.seek(0)
    plt.close()  # Close the plot to free up memory

    return Response(img.getvalue(), mimetype='image/png')