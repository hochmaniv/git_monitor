import requests
from datetime import datetime, timedelta
from itertools import product
from statistics import mean

WANTED_EVENTS = {'WatchEvent', 'PullRequestEvent', 'IssuesEvent'}
EVENTS_LIMIT = 500
REPOSITORIES_LIMIT = 5


class RepositoryManager:
    def __init__(self):
        self.repositories = []
        self.token = None

    def add_repository(self, repo):
        if len(self.repositories) >= REPOSITORIES_LIMIT:
            return False, "Maximum number of tracked repositories reached"
        
        for repository in self.repositories:
            if repo.__eq__(repository):
                return False, "Repository" + repository.get_info() + " is already being tracked"

        self.repositories.append(repo)
        return True, "Repository " + repo.get_info() + " added successfully"

    def delete_repository(self, repo):
        for repository in self.repositories:
            if repository.__eq__(repo):
                self.repositories.remove(repository)
                return True, "Repository " + repo.get_info() + " deleted successfully"
        return False, "Repository " + repo.get_info() + " not found"

    def get_repositories(self):
        return self.repositories
    
    def set_token(self, token):
        old_token = self.token
        self.token = token
        if self.token:
            if old_token != token:
                return True, "New token set successfully"
            else:
                return True, "This token is already being used"
        return False, "No token set"
    
    def get_token(self):
        return self.token
    

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
    
    def __fetch_events(self, token=None):
        url = f"https://api.github.com/repos/{self.profile_name}/{self.repo_name}/events"
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        events = []

        if token:
            headers['Authorization'] = f'token {token}'
        
        reached_repo_limit = False
        while url:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch events: {response.status_code}")
                print(response.json()) 
                response.raise_for_status()
            
            filtered_fetched_page = self.__filter_events(list(response.json()))
            filtered_fetched_page = self.__filter_events_last_7_days(filtered_fetched_page)
            
            for event in filtered_fetched_page:
                if len(events) >= EVENTS_LIMIT:
                    reached_repo_limit = True
                    break
                events.append(event)

            if reached_repo_limit:
                break

            # Check for the 'Link' header to get the next page URL as explained at
            # https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api?apiVersion=2022-11-28
            if 'Link' in response.headers:
                links = response.headers['Link']
                next_link = None
                for link in links.split(','):
                    if 'rel="next"' in link:
                        next_link = link.split(';')[0].strip('<> ')
                        break
                url = next_link
            else:
                url = None

        return events
    
    def __filter_events(self, events):
        return [event for event in events if event.get('type') in WANTED_EVENTS]
    
    def __filter_events_last_minutes(self, minutes, events):
        time_threshold = datetime.now() - timedelta(minutes=int(minutes))
        filtered_events = []

        for event in events:
            created_at = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            if created_at > time_threshold:
                filtered_events.append(event)

        return filtered_events

    def __filter_events_last_7_days(self, events):
        return self.__filter_events_last_minutes(1080, events) # 1080 minutes in 7 days 
    
    def group_events(self, minutes, token):
        minutes = int(minutes)
        event_types = {event: 0 for event in WANTED_EVENTS}

        events = self.__filter_events_last_minutes(minutes, self.__fetch_events(token))
        for event in events:
            event_types[event.get('type')] += 1
        
        return event_types
    
    def times_between_events(self, token):
        pairs = list(product(WANTED_EVENTS, repeat=2)) # get all possible combinations of events
        result = {str(pair): [] for pair in pairs}

        events = self.__fetch_events(token)
        if len(events) < 2:
            print(f'Failed to fetch events for {self.get_info()}')
            return None
        
        for i in range(len(events)-2):
            event1, event2 = events[i], events[i+1]
            event_types = (event1.get('type'), event2.get('type'))
            event1_created_at = datetime.strptime(event1['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            event2_created_at = datetime.strptime(event2['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            time_difference = (event1_created_at - event2_created_at).total_seconds()
            result[str(event_types)].append(time_difference)

        for key, value in result.items():
            result[key] = mean(value) if value else None

        return result