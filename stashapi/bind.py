from .oauth2 import OAuth2Request
from .models import ApiModel
import urllib
import re

re_path_template = re.compile('{\w+}')


def encode_string(value):
    return str(value)


class StashClientError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        return self.error_message


class StashAPIError(Exception):

    def __init__(self, status_code, error_type, error_message, *args, **kwargs):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message

    def __str__(self):
        return "(%s) %s-%s" % (self.status_code, self.error_type, self.error_message)


def bind_method(**config):

    class StashAPIMethod(object):

        path = config['path']
        method = config.get('method', 'GET')
        accepts_parameters = config.get("accepts_parameters", [])
        requires_target_user = config.get('requires_target_user', False)
        paginates = config.get('paginates', False)
        root_class = config.get('root_class', ApiModel)
        accepts_file = config.get('accepts_file', False)
        response_type = config.get("response_type", "empty")
        include_secret = config.get("include_secret", False)
        objectify_response = config.get("objectify_response", True)

        def __init__(self, api, *args, **kwargs):
            self.api = api
            self.as_generator = kwargs.pop("as_generator", False)
            self.return_json = kwargs.pop("return_json", False)
            self.max_pages = kwargs.pop("max_pages", 3)
            self.parameters = {}
            self.file = None
            self._build_parameters(args, kwargs)
            self._build_path()

        def _build_parameters(self, args, kwargs):
            # via tweepy https://github.com/joshthecoder/tweepy/
            for index, value in enumerate(args):
                if value is None:
                    continue

                try:
                    self.parameters[self.accepts_parameters[index]] = encode_string(value)
                except IndexError:
                    raise StashClientError("Too many arguments supplied")

            for key, value in kwargs.items():
                if value is None:
                    continue
                if key in self.parameters:
                    raise StashClientError("Parameter %s already supplied" % key)
                if key == 'file':
                    if self.accepts_file:
                        self.file = {'file' : value}
                    else:
                        raise StashClientError("Method does not support files")
                    continue
                self.parameters[key] = encode_string(value)
            if 'user_id' in self.accepts_parameters and not 'user_id' in self.parameters \
               and not self.requires_target_user:
                self.parameters['user_id'] = 'self'

        def _build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                try:
                    value = urllib.quote(self.parameters[name])
                except KeyError:
                    raise Exception('No parameter value found for path variable: %s' % name)
                del self.parameters[name]

                self.path = self.path.replace(variable, value)
            self.path = self.path

        def _do_api_request(self, url, method="GET", body=None, headers=None, files=None):
            headers = headers or {}
            response = OAuth2Request(self.api).make_request(url, method=method, body=body, headers=headers, files=files)
            if response.status_code == 503:
                raise StashAPIError(response.status_code, "Rate limited", "Your client is making too many request per second")

            try:
                content_obj = response.json()
            except ValueError:
                raise StashClientError('Unable to parse response, not valid JSON.')

            api_responses = []
            status_code = response.status_code
            if status_code == 200:
                if not self.objectify_response:
                    return content_obj, None

                if self.response_type == 'list':
                    for entry in content_obj['entries']:
                        if self.return_json:
                            api_responses.append(entry)
                        else:
                            obj = self.root_class.object_from_dictionary(entry)
                            api_responses.append(obj)
                elif self.response_type == 'entry':
                    data = content_obj
                    if self.return_json:
                        api_responses = data
                    else:
                        api_responses = self.root_class.object_from_dictionary(data)
                elif self.response_type == 'empty':
                    pass
                return api_responses, content_obj.get('pagination', {}).get('next_url')
            else:
                raise StashAPIError(status_code, content_obj['error'], content_obj['error_description'])

        def _paginator_with_url(self, url, method="GET", body=None, headers=None):
            headers = headers or {}
            pages_read = 0
            while url and pages_read < self.max_pages:
                api_responses, url = self._do_api_request(url, method, body, headers)
                pages_read += 1
                yield api_responses, url
            return

        def execute(self):
            url, method, body, headers = OAuth2Request(self.api).prepare_request(self.method,
                    self.path, self.parameters, accepts_file=self.accepts_file, include_secret=self.include_secret)
            if self.as_generator:
                return self._paginator_with_url(url, method, body, headers)
            else:
                content, next = self._do_api_request(url, method, body, headers, self.file)
            if self.paginates:
                return content, next
            else:
                return content

    def _call(api, *args, **kwargs):
        method = StashAPIMethod(api, *args, **kwargs)
        return method.execute()

    return _call
