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

# I apologize for the length of this function.
def get_legislator_income_by_slug(slug):
    context = make_context()
    COPY = context['COPY']
    income = {}
    leg_id = get_legislator_id_by_slug(slug)

    for row in COPY['gifts']:
        if row['sh_number'] == leg_id:
            try:
                income['gifts']
            except KeyError:
                income['gifts'] = []

            if row['Source_of_Gift'] != '':
                income['gifts'].append(row['Source_of_Gift'] + ' (Gifts)')

    for row in COPY['honoraria']:
        if row['sh_number'] == leg_id:
            try:
                income['honoraria']
            except KeyError:
                income['honoraria'] = []

            if row['Source_of_Honoraria'] != '':
                income['honoraria'].append(row['Source_of_Honoraria'] + ' (honorarium)')

    for row in COPY['loans']:
        if row['sh_number'] == leg_id:
            try:
                income['loans']
            except KeyError:
                income['loans'] = []

            if row['Name_of_Lender'] != '' and row['City_of_Lender'] != '' and row['Zip_of_Lender'] != '':
                income['loans'].append( \
                    row['Name_of_Lender'] + ', ' \
                    + row['City_of_Lender'] + ', ' \
                    #+ format_zip(row['Zip_of_Lender']) + ' (Loan)' \
                )

    for row in COPY['income_employmnet']:
        if row['sh_number'] == leg_id:
            try:
                income['income_employment']
            except KeyError:
                income['income_employment'] = []

            if row['Name_Employer'] != '':
                income['income_employment'].append( \
                    row['Position'] + ', ' \
                    + row['Name_Employer'] + ', ' \
                    + row['Employer_City'] + ', ' \
                    #+ format_zip(row['Employer_Zip']) \
                )

    for row in COPY['income_self']:
        if row['sh_number'] == leg_id:
            try:
                income['income_self']
            except KeyError:
                income['income_self'] = []

            if row['Name_of_Self_Employment_Business'] != '':
                income['income_self'].append( \
                    row['Name_of_Self_Employment_Business'] + ', ' \
                    + row['City_of_Self_Employment_Business'] + ', ' \
                    #+ format_zip(row['Zip_of_Self_Employment']) \
                )

    for row in COPY['income_business']:
        if row['sh_number'] == leg_id:
            try:
                income['income_business']
            except KeyError:
                income['income_business'] = []

            if row['Name_of_Business'] != '':
                income['income_business'].append( \
                    row['Name_of_Business'] + ', ' \
                    + row['City_of_Business'] + ', ' \
                    #+ format_zip(row['Zip_of_Business']) \
                )

    for row in COPY['income_law']:
        if row['sh_number'] == leg_id:
            try:
                income['income_law']
            except KeyError:
                income['income_law'] = []

            if row['Name_of_Practice'] != '':
                income['income_law'].append( \
                    row['Position_in_Practice'] + ', ' \
                    + row['Name_of_Practice'] + ', ' \
                    + row['City_of_Practice'] + ', ' \
                    #+ format_zip(row['Zip_of_Practice']) \
                )

    for row in COPY['income_other']:
        if row['sh_number'] == leg_id:
            try:
                income['income_other']
            except KeyError:
                income['income_other'] = []

            if row['Name_of_Source'] != '':
                line = row['Name_of_Source']
                line += ', ' + row['City_of_Source']
                #line += ', ' + format_zip(row['Zip_of_Source'])
                if row['Description_of_income_type'] != '':
                    line += " (%s)" % row['Description_of_income_type']

                income['income_other'].append(line)

    return income

def get_legislator_positions_by_slug(slug):
    context = make_context()
    COPY = context['COPY']
    positions = {}
    leg_id = get_legislator_id_by_slug(slug)


    for row in COPY['position_political']:
        if row['sh_number'] == leg_id:
            try:
                positions['position_political']
            except KeyError:
                positions['position_political'] = []

            if row['Name_of_Committee'] != '':
                if row['Name_of_Official'] == '':
                    # the official is the legislator, per https://github.com/INN/maine-legislature/issues/68
                    positions['position_political'].append(
                        row['Title_in_Committee'] + ', ' +
                        row['Name_of_Committee']
                    )

    for row in COPY['position_org']:
        if row['sh_number'] == leg_id:
            try:
                positions['position_org']
            except KeyError:
                positions['position_org'] = []

            # this checks row['Relationship_to_Legislator'] to make sure it's self
            # otherwise, this goes in family member positions
            if str(row['Relationship_to_Legislator']).lower() == 'self':
                line = row['Title_in_Organization'] + ', '
                line += row['Organization'] + ', '
                line += row['City_of_Organization'] + ', '
                #line += format_zip(row['Zip_of_Organization'])
                if str(row['Compensated']).lower() == 'yes':
                    line += ' (paid position)'
                positions['position_org'].append(line)

    return positions

def get_legislator_family_by_slug(slug):
    context = make_context()
    COPY = context['COPY']
    family = {}
    leg_id = get_legislator_id_by_slug(slug)

    for row in COPY['position_org']:
        if row['sh_number'] == leg_id:
            try:
                family['position_org']
            except KeyError:
                family['position_org'] = []

            # this checks row['Relationship_to_Legislator'] to make sure it's a family
            # otherwise, this goes in family member positions
            if str(row['Relationship_to_Legislator']).lower() == 'spouse': # The values used here are spouse and self, and '' for self.
                line = row['Name_of_Position_Holder']
                line += " (%s)" % str(row['Relationship_to_Legislator']).lower()
                if row['Title_in_Organization']:
                    line += ', ' + row['Title_in_Organization']
                if row['Organization']:
                    line += ', ' + row['Organization']
                if row['City_of_Organization']:
                    line += ', ' + row['City_of_Organization']
                # Not doing zips this app
                #line += ', ' + format_zip(row['Zip_of_Organization'])
                if str(row['Compensated']).lower() == 'yes':
                    line += ' (paid position)'
                family['position_org'].append(line)

    for row in COPY['family_income_compensation']:
        if row['sh_number'] == leg_id:
            try:
                family['family_income_compensation']
            except KeyError:
                family['family_income_compensation'] = []

            if str(row['Name_of_family_member']).lower() != '':
                line = row['Name_of_family_member']
                if str(row['Position_of_family_member']) != '':
                    line += ', ' + row['Position_of_family_member']
                if str(row['Family_Member_Employers_Name']) != '':
                    line += ', ' + row['Family_Member_Employers_Name']
                if str(row['Employers_City']) != '':
                    line += ', ' + row['Employers_City']
                #if str(row['Employers_Zip']) != '':
                #    line += ', ' + format_zip(row['Employers_Zip'])
                family['family_income_compensation'].append(line)

    for row in COPY['family_other_income']:
        if row['sh_number'] == leg_id:
            try:
                family['family_other_income']
            except KeyError:
                family['family_other_income'] = []

            if str(row['Name_of_spouse']) != '': # This column is also used for other family members
                line = row['Name_of_spouse']
                if str(row['Source_of_family_member_income']) != '':
                    line += ', ' +  row['Source_of_family_member_income']
                if str(row['City_of_other_source']) != '':
                    line += ', ' +  row['City_of_other_source']
                #if str(row['Zip_of_other_source']) != '':
                #    line += ', ' +  format_zip(row['Zip_of_other_source'])
                if str(row['Type_of_Income']) != '':
                    line += ' (%s)' % row['Type_of_Income']
                family['family_other_income'].append(line)

    for row in COPY['position_political']:
        if row['sh_number'] == leg_id:
            try:
                family['position_political']
            except KeyError:
                family['position_political'] = []

            if row['Name_of_Committee'] != '':
                if row['Name_of_Official'] != '':
                    # the official is the legislator, per https://github.com/INN/maine-legislature/issues/68
                    family['position_political'].append(
                        row['Name_of_Official'] + ', ' +
                        row['Title_in_Committee'] + ', ' +
                        row['Name_of_Committee']
                    )

    return family

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

# Not actually used anymore, since we removed the zip codes from display.
# Please test the first two lines against "01234-4567": it should not return "001234-4567"
def format_zip(zip):
    if type(zip) == str:
        return zip

    try:
        zip = str(zip)
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

def is_really_iterable(var):
    if not hasattr(var, '__iter__'):
        return False

    count = 0
    for k in var:
        if hasattr(var[k], '__iter__'):
            for j in var[k]:
                count += 1

    if count >= 1:
        return True
    else:
        return False

def leg_bills_count(leg_id):
    counter = 0
    context = make_context()
    for bill in context['COPY']['bills']:
        if bill['sh_number'] == leg_id:
            counter = counter + 1

    return counter
