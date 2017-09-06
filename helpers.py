# _*_ coding:utf-8 _*_
# Helper functions for the Maine Legislature project
import app_config
import collections
import copytext
import re
import json

from unicodedata import normalize

CACHE = {}

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def get_legislators():
    copy = get_copy()
    return copy['senators']._sheet + copy['house_reps']._sheet


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
    copy = get_copy()
    income = collections.OrderedDict()
    leg_id = get_legislator_id_by_slug(slug)

    for row in copy['income_employment']:
        if row['sh_number'] == leg_id:
            try:
                income['income_employment']
            except KeyError:
                income['income_employment'] = []

            if row['Name_Employer'] != u'':
                income['income_employment'].append(
                    row['Position'] + ', '
                    + row['Name_Employer'] + ', '
                    + row['Employer_City']
                    # + format_zip(row['Employer_Zip'])
                )

    for row in copy['income_self']:
        if row['sh_number'] == leg_id:
            try:
                income['income_self']
            except KeyError:
                income['income_self'] = []

            if row['Name_of_Self_Employment_Business'] != u'':
                income['income_self'].append(
                    row['Name_of_Self_Employment_Business'] + ', '
                    + row['City_of_Self_Employment_Business']
                    # + format_zip(row['Zip_of_Self_Employment'])
                )

    for row in copy['income_business']:
        if row['sh_number'] == leg_id:
            try:
                income['income_business']
            except KeyError:
                income['income_business'] = []

            if row['Name_of_Business'] != u'':
                income['income_business'].append(
                    row['Name_of_Business'] + ', '
                    + row['City_of_Business']
                    # + format_zip(row['Zip_of_Business'])
                )

    for row in copy['income_law']:
        if row['sh_number'] == leg_id:
            try:
                income['income_law']
            except KeyError:
                income['income_law'] = []

            if row['Name_of_Practice'] != u'':
                income['income_law'].append(
                    row['Position_in_Practice'] + ', '
                    + row['Name_of_Practice'] + ', '
                    + row['City_of_Practice']
                    # + format_zip(row['Zip_of_Practice'])
                )

    for row in copy['income_other']:
        if row['sh_number'] == leg_id:
            try:
                income['income_other']
            except KeyError:
                income['income_other'] = []

            if row['Name_of_Source'] != u'':
                line = row['Name_of_Source']
                line += ', ' + row['City_of_Source']
                # line += ', ' + format_zip(row['Zip_of_Source'])
                if row['Description_of_income_type'] != u'':
                    line += " (%s)" % row['Description_of_income_type']

                income['income_other'].append(line)

    for row in copy['honoraria']:
        if row['sh_number'] == leg_id:
            try:
                income['honoraria']
            except KeyError:
                income['honoraria'] = []

            if row['Source_of_Honoraria'] != u'':
                income['honoraria'].append(row['Source_of_Honoraria'] + ' (honorarium)')

    for row in copy['loans']:
        if row['sh_number'] == leg_id:
            try:
                income['loans']
            except KeyError:
                income['loans'] = []

            if row['Name_of_Lender'] != u'' and row['City_of_Lender'] != u'' and row['Zip_of_Lender'] != u'':
                income['loans'].append(
                    row['Name_of_Lender'] + ', '
                    + row['City_of_Lender'] + ' (loan)'
                    # + ', ' + format_zip(row['Zip_of_Lender']) + ' (Loan)'
                )

    for row in copy['gifts']:
        if row['sh_number'] == leg_id:
            try:
                income['zgifts']
            except KeyError:
                income['zgifts'] = []

            if row['Source_of_Gift'] != u'':
                income['zgifts'].append(row['Source_of_Gift'] + ' (gifts)')

    return income


def get_legislator_positions_by_slug(slug):
    copy = get_copy()
    positions = {}
    leg_id = get_legislator_id_by_slug(slug)

    for row in copy['position_political']:
        if row['sh_number'] == leg_id:
            try:
                positions['position_political']
            except KeyError:
                positions['position_political'] = []

            if row['Name_of_Committee'] != u'':
                if row['Name_of_Official'] == u'':
                    # the official is the legislator,
                    # per https://github.com/INN/maine-legislature/issues/68
                    positions['position_political'].append(
                        row['Title_in_Committee'] + ', ' +
                        row['Name_of_Committee']
                    )

    for row in copy['position_org']:
        if row['sh_number'] == leg_id:
            try:
                positions['position_org']
            except KeyError:
                positions['position_org'] = []

            # this checks row['Relationship_to_Legislator'] to make sure it's self
            # otherwise, this goes in family member positions
            if unicode(row['Relationship_to_Legislator']).lower() == u'self':
                line = row['Title_in_Organization'] + ', '
                line += row['Organization']
                if unicode(row['City_of_Organization']) != u'':
                    line += ', ' + row['City_of_Organization']
                # line += format_zip(row['Zip_of_Organization'])
                if unicode(row['Compensated']).lower() == u'yes':
                    line += ' (paid position)'
                positions['position_org'].append(line)

    return positions


def get_legislator_family_by_slug(slug):
    copy = get_copy()
    family = {}
    leg_id = get_legislator_id_by_slug(slug)

    for row in copy['position_org']:
        if row['sh_number'] == leg_id:
            try:
                family['position_org']
            except KeyError:
                family['position_org'] = []

            # this checks row['Relationship_to_Legislator'] to make sure it's a family
            # otherwise, this goes in family member positions
            # The values used here are spouse and self, and u'' for self.
            if unicode(row['Relationship_to_Legislator']).lower() == u'spouse':
                line = row['Name_of_Position_Holder']
                line += " (%s)" % unicode(row['Relationship_to_Legislator']).lower()
                if row['Title_in_Organization']:
                    line += ', ' + row['Title_in_Organization']
                if row['Organization']:
                    line += ', ' + row['Organization']
                if row['City_of_Organization']:
                    line += ', ' + row['City_of_Organization']
                # Not doing zips this app
                # line += ', ' + format_zip(row['Zip_of_Organization'])
                if unicode(row['Compensated']).lower() == u'yes':
                    line += ' (paid position)'
                family['position_org'].append(line)

    for row in copy['family_income_compensation']:
        if row['sh_number'] == leg_id:
            try:
                family['family_income_compensation']
            except KeyError:
                family['family_income_compensation'] = []

            if unicode(row['Name_of_family_member']).lower() != u'':
                line = row['Name_of_family_member']
                if unicode(row['Position_of_family_member']) != u'':
                    line += ', ' + row['Position_of_family_member']
                if unicode(row['Family_Member_Employers_Name']) != u'':
                    line += ', ' + row['Family_Member_Employers_Name']
                if unicode(row['Employers_City']) != u'':
                    line += ', ' + row['Employers_City']
                # if unicode(row['Employers_Zip']) != u'':
                #    line += ', ' + format_zip(row['Employers_Zip'])
                family['family_income_compensation'].append(line)

    for row in copy['family_other_income']:
        if row['sh_number'] == leg_id:
            try:
                family['family_other_income']
            except KeyError:
                family['family_other_income'] = []

            # This column is also used for other family members
            if unicode(row['Name_of_spouse']) != u'':
                line = row['Name_of_spouse']
                if unicode(row['Source_of_family_member_income']) != u'':
                    line += ', ' + row['Source_of_family_member_income']
                if unicode(row['City_of_other_source']) != u'':
                    line += ', ' + row['City_of_other_source']
                # if unicode(row['Zip_of_other_source']) != u'':
                #    line += ', ' +  format_zip(row['Zip_of_other_source'])
                if unicode(row['Type_of_Income']) != u'':
                    line += ' (%s)' % row['Type_of_Income']
                family['family_other_income'].append(line)

    for row in copy['position_political']:
        if row['sh_number'] == leg_id:
            try:
                family['position_political']
            except KeyError:
                family['position_political'] = []

            if row['Name_of_Committee'] != u'':
                if row['Name_of_Official'] != u'':
                    # the official is the legislator,
                    # per https://github.com/INN/maine-legislature/issues/68
                    family['position_political'].append(
                        row['Name_of_Official'] + ', ' +
                        row['Title_in_Committee'] + ', ' +
                        row['Name_of_Committee']
                    )

    return family


def rep_sen(id):
    if id.startswith('s'):
        return u"Sen."
    elif id.startswith('h'):
        return u"Rep."
    else:
        return u''


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
        zip = zip.replace('.0', u'')
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
    copy = get_copy()
    for bill in copy['bills']:
        if bill['sh_number'] == leg_id:
            counter = counter + 1

    return counter


def get_copy():
    if not CACHE.get('copy', None):
        CACHE['copy'] = copytext.Copy(app_config.COPY_PATH)
    return CACHE['copy']


def legislators_json():
    legislators = get_legislators()

    json_data = []
    for legislator in legislators:
        json_data.append({
            'id': legislator['id'],
            'name': legislator['name'],
            'district': format_district(legislator['district_number']),
            'party': legislator['party'],
            'town': legislator['home_city'],
            'slug': slugify(legislator['name']),
            'rep_sen': rep_sen(legislator['id'])
        })

    with open('www/assets/data/legislators.json', 'w+') as f:
        print "Writing www/assets/data/legislators.json"
        f.write(json.dumps(json_data))
