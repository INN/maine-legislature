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
    leg = None
    for legislator in legislators:
        if slugify(legislator['name']) == slug:
            leg = legislator
            break

    return leg

def get_legislator_id_by_slug(slug):
    leg = get_legislator_by_slug(slug)
    return leg['id']

def get_legislator_income_by_slug(slug):
    context = make_context()
    COPY = context['COPY']
    income = {}
    leg_id = get_legislator_id_by_slug(slug)

    for row in COPY['honoraria']:
        if row['sh_number'] == leg_id:
            try:
                income['honoraria']
            except KeyError:
                income['honoraria'] = []

            if row['Source_of_Honoraria'] != '':
                income['honoraria'].append(row['Source_of_Honoraria'])

#    for row in COPY['gifts']:
#        if row['sh_number'] == leg_id:
#            try:
#                income['gifts']
#            except NameError:
#                income['gifts'] = []
#
#            if row['Source_of_Gift'] != '':
#                income['gifts'].append(row['Source_of_Gift'])
#
#    for row in COPY['loans']:
#        if row['sh_number'] == leg_id:
#            try:
#                income['loans']
#            except NameError:
#                income['loans'] = []
#
#            if row['Name_of_Lender'] != '':
#                income['loans'].append(
#                    row['Name_of_Lendor'] + ', ' +
#                    row['City_of_Lender'] + ', ' +
#                    format_zip(row['Zip_of_Lender'])
#                )
#
#    for row in COPY['income_employmnet']:
#        if row['sh_number'] == leg_id:
#            try:
#                income['income_employment']
#            except NameError:
#                income['income_employment'] = []
#
#            if row['Name_Employer'] != '':
#                income['employment'].append(
#                    row['Position'] + ', ' +
#                    row['Name_Employer'] + ', ' +
#                    row['Employer_City'] + ', ' +
#                    format_zip(row['Employer_Zip'])
#                )
    
    return income

def rep_sen(id):
    if id.startswith( 's' ):
        return u"Sen."
    elif id.startswith( 'h' ):
        return u"Rep."
    else:
        return ''

def format_district(district):
    try:
        float(district)
        return u"District " + district
    except ValueError:
        return district

def format_zip(zip):
    try:
        zip =  zip.striptags()
        #stripzero = re.sub(u'.0', u'')
        zip = zip.replace('.0', '')
        return u"0" + zip
    except ValueError:
        return zip

# Other helpers
def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
