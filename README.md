## Prerequisites
Python3 (ideally 3.9.2rc1 or newer)
pip 

## Intro
Use `pip install -r requirements`to install all necessary libraries.
Start the app by running `python ./main.py`

This application runs as Flask application, by default on http://127.0.0.1:5000.
You can use any tool you would like for the REST API requests. I developed this using Postman.

## Endpoints
The app serves 7 endpoints besides index:
### Github repository managing endpoints:
- /add-repository/<profile_name>/<repository_name>
Make a POST request to track a new repository
- /get-repositories
Make a GET request to get a list of tracked repositories
- /delete-repository/<profile_name>/<repository_name>
Make a DELETE request to stop tracking a repository
### Data processing endpoints:
- /get-event-times
Make a GET request to get the average time between consecutive events, separately for each combination of event type and repository name
- /get-events-by-offset/<minutes>
Make a GET request to get the total number of events grouped by the event type and repository name for a given offset. Offset is set in minutes
### Visualization endpoint:
- /visual-events-by-offset/<minutes>
Make a GET request to see the visualization of total number of events grouped by the event type and repository name for a given offset. Offset is set in minutes
### Endpoint to deliver authentication token
- /send-token
Make a POST request that includes "Authorization: YOUR-TOKEN" in header to authenticate in order to get higher rate limit for requests per hour

## Example usage
To track a new repository called project-based-learning by user practical-tutorials, make the following POST request: 
`http://127.0.0.1:5000/add-repository/practical-tutorials/project-based-learning`

> [!NOTE]
> Known issues: 
1) The GitHub API is set to fetch 10 pages of events with 30 events per page on default. Even after increasing the number of events
per page (to 100) and pagination (https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28), 
the maximum of fetched events still sits at 300 after some basic testing.
Based on https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28 it looks like it is not possible to fetch more than 300 events or events older than 90 days for a repository. 

2) Fetching events without authentication token.
There is a limited number of requests per minute (60) per IP address. Using an authorization token increases this number.
More detailes at https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28
and at https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28
To fix this, the /send-token API endpoint was implemented. 

_TODO_:
- fetching more than 300 events for a repository
- better handling of status codes
- write better code for visualization endpoint (especially (re)move the logic from api.py to another script)
