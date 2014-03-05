from . import oauth2
from .bind import bind_method
from .models import Media, User, Location, Tag, Comment, Relationship

MEDIA_ACCEPT_PARAMETERS = ["count", "max_id"]
SEARCH_ACCEPT_PARAMETERS = ["q", "count"]

SUPPORTED_FORMATS = ['json']


class StashAPI(oauth2.OAuth2API):

    host = "www.deviantart.com"
    base_path = "/api/oauth2/stash"
    access_token_field = "access_token"
    authorize_url = "https://www.deviantart.com/oauth2/authorize"
    access_token_url = "https://www.deviantart.com/oauth2/token"
    protocol = "https"
    api_name = "Stash"

    def __init__(self, *args, **kwargs):
        format = kwargs.get('format', 'json')
        if format in SUPPORTED_FORMATS:
            self.format = format
        else:
            raise Exception("Unsupported format")
        super(StashAPI, self).__init__(*args, **kwargs)

    submit = bind_method(
                path='/submit',
                method="POST",
                accept_parameters=['title', 'artist_comments', 'keywords',
                    'stashid', 'folder', 'folderid'],
                accepts_file=True,
                objectify_response=False)

    delete = bind_method(
                path='/delete',
                method="POST",
                accept_parameters=['stashid'],
                objectify_response=False)

    move_file = bind_method(
                path='/move/file',
                method="POST",
                accept_parameters=['stashid', 'folder', 'folderid', 'targetid', 
                    'position'],
                objectify_response=False)

    move_folder = bind_method(
                path='/move/folder',
                method="POST",
                accept_parameters=['stashid', 'folder', 'folderid', 'targetid', 
                    'position'],
                objectify_response=False)

    rename = bind_method(
                path='/folder',
                method="POST",
                accept_parameters=['folder', 'folderid'],
                objectify_response=False)

    space = bind_method(
                path='/space',
                accept_parameters=[],
                objectify_response=False)

    list = bind_method(
                path='/delta',
                accept_parameters=['cursor', 'offset'],
                objectify_response=False)

    metadata = bind_method(
                path='/metadata',
                method='POST',
                accepts_parameters=['stashid', 'folderid', 'list'],
                objectify_response=False)

    media = bind_method(
                path='/media',
                accepts_parameters=['stashid'],
                objectify_response=False)
