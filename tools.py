import requests
from datetime import datetime, timedelta
from itertools import product


WANTED_EVENTS = {'WatchEvent', 'PullRequestEvent', 'IssuesEvent'}
EVENTS_LIMIT = 500
REPOSITORIES_LIMIT = 5


class Repository:
    def __init__(self, profile_name, repo_name):
        self.profile_name = profile_name
        self.repo_name = repo_name
    
    def get_profile_name(self):
        return self.profile_name
    
    def get_repo_name(self):
        return self.repo_name
    
    def get_info(self):
        return self.profile_name + '/' + self.repo_name
    
    def __eq__(self, other):
        if not isinstance(other, Repository):
            return False
        return self.profile_name == other.get_profile_name() and self.repo_name == other.get_repo_name()
        
    

class RepositoryManager:
    def __init__(self):
        self.repositories = []

    def add_repository(self, repo):
        if len(self.repositories) >= REPOSITORIES_LIMIT:
            return False, "Maximum number of tracked repositories reached"
        
        for repository in self.repositories:
            if repository.__eq__(repo):
                return False, "Repository" + repository.get_info() + "is already being tracked"

        self.repositories.append(repo)
        return True, "Repository " + repo.get_info() + " added successfully"

    def delete_repository(self, repo):
        if repo in self.repositories:
            self.repositories.remove(repo)
            return True, "Repository " + repo.get_info() + " deleted successfully"
        return False, "Repository" + repo.get_info() + " not found"

    def get_repositories(self):
        return self.repositories


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
        # TODO
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