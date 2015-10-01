#!/usr/bin/env python
"""
Example application views.

Note that `render_template` is wrapped with `make_response` in all application
routes. While not necessary for most Flask apps, it is required in the
App Template for static publishing.
"""

import app_config
import json
import oauth
import static

from flask import Flask, make_response, render_template
from render_utils import make_context, smarty_filter, urlencode_filter
from werkzeug.debug import DebuggedApplication

from helpers import *

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')
app.jinja_env.filters['slugify'] = slugify
app.jinja_env.filters['rep_sen'] = rep_sen
app.jinja_env.filters['format_district'] = format_district
app.jinja_env.filters['format_zip'] = format_zip
app.jinja_env.filters['is_really_iterable'] = is_really_iterable


@app.route('/')
@oauth.oauth_required
def index():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    context = make_context()
    context['legislators'] = get_legislators()

    with open('data/featured.json') as f:
        context['featured'] = json.load(f)

    return make_response(render_template('index.html', **context))

legislator_slugs = get_legislator_slugs()
for slug in legislator_slugs:
    @app.route('/legislator/%s/' % slug, endpoint=slug)
    def legislator():
        context = make_context()

        from flask import request
        slug = request.path.split('/')[2]

        context['legislator'] = get_legislator_by_slug(slug)
        context['income'] = get_legislator_income_by_slug(slug)
        context['positions'] = get_legislator_positions_by_slug(slug)
        context['family'] = get_legislator_family_by_slug(slug)
        with open('data/featured.json') as f:
            context['featured'] = json.load(f)

        return make_response(render_template('legislator.html', **context))

@app.route('/comments/')
def comments():
    """
    Full-page comments view.
    """
    return make_response(render_template('comments.html', **make_context()))

@app.route('/widget.html')
def widget():
    """
    Embeddable widget example page.
    """
    return make_response(render_template('widget.html', **make_context()))

@app.route('/test_widget.html')
def test_widget():
    """
    Example page displaying widget at different embed sizes.
    """
    return make_response(render_template('test_widget.html', **make_context()))

app.register_blueprint(static.static)
app.register_blueprint(oauth.oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab app" instead!'
