#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
Example application views.

Note that `render_template` is wrapped with `make_response` in all application
routes. While not necessary for most Flask apps, it is required in the
App Template for static publishing.
"""

import app_config
import oauth
import static

from flask import Flask, make_response, render_template
from render_utils import make_context, smarty_filter, urlencode_filter
from werkzeug.debug import DebuggedApplication

from helpers import slugify, rep_sen, format_district, format_zip, \
    is_really_iterable, get_legislator_slugs, leg_bills_count, \
    get_legislator_by_slug, get_legislator_income_by_slug, \
    get_legislator_positions_by_slug, get_legislator_family_by_slug, \
    get_legislator_business_by_slug, get_legislator_political_positions_by_slug

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')
app.jinja_env.filters['slugify'] = slugify
app.jinja_env.filters['rep_sen'] = rep_sen
app.jinja_env.filters['format_district'] = format_district
app.jinja_env.filters['format_zip'] = format_zip
app.jinja_env.filters['is_really_iterable'] = is_really_iterable
app.jinja_env.filters['leg_bills_count'] = leg_bills_count


@app.route('/')
def index():
    context = make_context()
    return make_response(render_template('index.html', **context))


legislator_slugs = get_legislator_slugs()
for slug in legislator_slugs:
    @app.route('/legislator/%s/' % slug)
    def legislator():
        context = make_context()
        from flask import request

        slug = request.path.split('/')[2]

        context['legislator'] = get_legislator_by_slug(slug)
        context['income'] = get_legislator_income_by_slug(slug)
        context['business'] = get_legislator_business_by_slug(slug)
        context['positions'] = get_legislator_positions_by_slug(slug)
        context['political_positions'] = get_legislator_political_positions_by_slug(slug)
        context['family'] = get_legislator_family_by_slug(slug)
        return make_response(render_template('legislator.html', **context))


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
