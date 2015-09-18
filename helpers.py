# Helper functions for the Maine Legislature project
import app_config
import copytext
import re

from render_utils import make_context
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def get_legislators():
    context = make_context()
    COPY = context['COPY']
    senators = COPY['senators']
    reps = COPY['house_reps']
    legislators = senators
    # This is probably safe, but will fail if the variable name changes for
    # the list of rows that copytext uses within the Sheet object.
    legislators._sheet = legislators._sheet + reps._sheet
    return legislators

def get_legislator_slugs():
    legislators = get_legislators()
    slugs = []
    for legislator in legislators:
        slugs.append(slugify(legislator['name']))
    return slugs

def get_legislator_by_slug(slug):
    legislators = get_legislators()
    for legislator in legislators:
        if slugify(legislator['name']) == slug:
            return legislator
    endfor

def rep_sen(id):
    if id.startswith( 's' ):
        return u"Sen."
    elif id.startswith( 'h' ):
        return u"Rep."
    else:
        return ''

# Other helpers
def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
