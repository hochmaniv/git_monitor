import requests
from datetime import datetime, timedelta
from itertools import product


WANTED_EVENTS = {'WatchEvent', 'PullRequestEvent', 'IssuesEvent'}
EVENTS_LIMIT = 500


def get_repository_events(profile, repo):
    url = f"https://api.github.com/repos/{profile}/{repo}/events"
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
            
            # Check if there's a next page of events
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None
        else:
            print(f"Failed to fetch events: {response.status_code}")
            break

    return all_events


def filter_events(events):
    return [event for event in events if event.get('type') in WANTED_EVENTS]


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


def group_events(events):
    event_types = {e: 0 for e in WANTED_EVENTS}

    for event in events:
        event_types[event.get('type')] += 1
    
    return event_types


def times_between_events(events):
    pairs = list(product(WANTED_EVENTS, repeat=2))
    result = {pair: [] for pair in pairs}

    if len(events) < 2:
        print("Repository XY does not have enough events (less than 2)")
        return result
    
    for i in range(len(events)-2):
        event1, event2 = events[i], events[i+1]
        event_types = (event1.get('type'), event2.get('type'))
        event1_created_at = datetime.strptime(event1['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        event2_created_at = datetime.strptime(event2['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        time_difference = (event1_created_at - event2_created_at).total_seconds()
        result[event_types].append(time_difference)

    for key, value in result.items():
        result[key] = average(value)

    return result


def average(times):
    if not times:
        return None
    return sum(times) / len(times)


def get_events(profile, repo):
    events = get_repository_events(profile, repo)

    if events:        
        events = filter_events(events)
        if len(filter_events_last_7_days(events)) > EVENTS_LIMIT:
            events = events[:EVENTS_LIMIT]
    
    return events