from pyoauth2 import Client

class StashError(Exception):
    def __init__(self, value):
        self.value = value
    def __str(self):
        return repr(self.value)

class StashItem(object):
    def __init__(self):
        self.stashid = None
        self.title = None
        self.creation_time = None
        self.coments = None
        self.folderid = None
        self.file = None

class StashAPI(object):
    # configure these to match your developer settings
    client_id = '977'
    client_secret = '1eb3b5a5b401ac680d5b59ba972d56b2'

    def __init__(self):
        self.client = Client(self.client_id, self.client_secret, site='https://www.deviantart.com',
                authorize_url='/oauth2/authorize', token_url='/oauth2/access_token')
        self.auth_code = None
        self.access_token = None
        self.refresh_token = None
        self.expires = None
        self.redirect_uri = None
        self.list_cursor = None
        self.items = []
        self.connected = False
        self = list()

    def auth_url(self, redirect_uri):
        self.redirect_uri = redirect_uri
        return self.client.auth_code.authorize_url(redirect_uri=self.redirect_uri)

    def access_endpoint(self, path, parameters):
        # make sure our token is valid
        #  test with /placebo
        # if not refresh it
        # ensure the api call went through successfully
        # return the json data
        pass

    def authenticate(self, auth_code):
        self.auth_code = auth_code
        self.access_token = self.client.auth_code.get_token(auth_code, redirect_uri=self.redirect_uri)
        self.test_token()
        self.list()
        self.connected = True
        
    def test_token(self):
        if self.access_token is None or not self.token_valid():
            self.retrieve_token()

    def token_valid(self):
        url_placebo = 'https://www.deviantart.com/api/oauth2/placebo'
        url_placebo_params = {'access_token': self.access_token}
        placebo_response = requests.get(addparams(url_placebo, url_placebo_params))
        return placebo_response.json()['status'] == 'success'

    def retrieve_token(self):
        url_token = 'https://www.deviantart.com/oauth2/token'
        url_token_params = {'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'authorization_code', 'code': self.auth_code, 'redirect_uri': self.redirect_uri}
        url_token_refresh_params = {'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}
        if self.access_token is None:
            token_response = requests.get(addparams(url_token, url_token_params))
        else:
            token_response = requests.get(addparams(url_token, url_token_refresh_params))

        if token_response.json()['status'] == 'error':
            raise StashError('token retrieval unsuccessful, "%s"' % token_response.json()['error_description'])
        self.access_token = token_response.json()['access_token']
        self.refresh_token = token_response.json()['refresh_token']
        self.expires = token_response.json()['expires_in']

    def submit(self):
        url_submit = 'https://www.deviantart.com/api/oauth2/stash/submit'
        url_submit_params = {'access_token': self.access_token}

    def list(self):
        self.test_token()
        url_list = 'https://www.deviantart.com/api/oauth2/stash/delta'
        url_list_params = {'access_token': self.access_token}
        list_response = requests.get(addparams(url_list, url_list_params))
        if list_response.json().get('status') == 'error':
            raise StashError('token retrieval unsuccessful, "%s"' % list_response.json()['error_description'])
        self.list_cursor = list_response.json()['cursor']
        for entry in list_response.json()['entries']:
            if not entry['metadata']['is_folder']:
                i = StashItem()
                i.stashid = entry['metadata']['stashid']
                i.title = entry['metadata']['title']
                i.creation_time = entry['metadata']['creation_time']
                i.coments = entry['metadata']['artist_comments']
                i.folderid = entry['metadata']['folderid']
                self.items.append(i)

    def get_items(self):
        if len(self.items) == 0:
            self.list()
        return self.items
