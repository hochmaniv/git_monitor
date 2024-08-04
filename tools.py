import requests
import json
from datetime import datetime, timedelta



def get_repository_events():
    url = f"https://api.github.com/repos/sindresorhus/awesome/events"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'requests'  # GitHub recommends setting a User-Agent header
    }

    all_events = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            all_events.extend(events)
            
            # Check if there's a next page
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            print(f"Failed to fetch events: {response.status_code}")
            break

    return all_events

def filter_events(events):
    return [event for event in events if event.get('type') in {'WatchEvent', 'PullRequestEvent', 'IssuesEvent'}]

def filter_events_last_minutes(events, minutes):
    time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
    filtered_events = []
    for event in events:
        created_at = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        if created_at > time_threshold:
            filtered_events.append(event)
    return filtered_events


def filter_events_last_7_days(events):
    return filter_events_last_minutes(events, 1080) # 1080 minutes in 7 days 


def print_events(events):
    for event in events:
        event_type = event.get('type')
        created_at = event.get('created_at')
        repo_name = event.get('repo', {}).get('name')
        
        print(f"Repo: {repo_name}")
        print(f"Event: {event_type}")
        print(f"Created at: {created_at}")
        print("-" * 40)

if __name__ == "__main__":

    events = get_repository_events()

    if events:
        #print_events(filter_events(events))
        print("total:", len(events))
        print("last seven days:", len(filter_events_last_7_days(events)))
        print("last 60 minutes:", len(filter_events_last_minutes(events, 60)))
