from sys import argv
from flask import Flask, request
from stash import StashAPI
import subprocess

app = Flask(__name__)

api = StashAPI()
redirect_uri_mount = 'http://localhost:5000/auth'
redirect_uri_nomount = 'http://localhost:5000/auth-nomount'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
        func()

@app.route('/')
def root():
    return '<a href="%s">Authenticate</a><br><a href="%s">Authenticate (no mount)</a>' % (api.auth_url(redirect_uri_mount), api.auth_url(redirect_uri_nomount))

@app.route('/auth')
def auth():
    code = request.args.get('code', '')
    subprocess.call(['python', 'stashfs.py', mountpoint, code, redirect_uri_mount])
    return 'code = "%s" <br> redirect_uri = "%s"' % (code, redirect_uri_mount)

@app.route('/auth-nomount')
def auth_nomount():
    code = request.args.get('code', '')
    return 'code = "%s" <br> redirect_uri = "%s"' % (code, redirect_uri_nomount)

if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s <mountpoint>' % argv[0])
        exit(1)

    global mountpoint
    mountpoint = argv[1]
    app.run(debug=True)
