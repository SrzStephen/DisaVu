
import json


with open('amenities.geojson', 'rb') as fp:
    data = json.load(fp)


filtered = []
for d in data['features']:
    if d['properties']['amenity'] in [
        'bank',
        'bus_station',
        'childcare',
        'cinema',
        'clinic',
        'college',
        'community_centre',
        'courthouse',
        'dentist',
        'doctors',
        'ferry_terminal',
        'fire_station',
        'fuel',
        'hospital',
        'kindergarten',
        'library',
        'nursing_home',
        'pharmacy',
        'place_of_worship',
        'police',
        'post_office',
        'prep_school',
        'prison',
        'public_building',
        'school',
        'shelter',
        'townhall',
        'university',
    ]:
        filtered.append(d)

data['features'] = filtered
with open('amenities_filtered.geojson', 'w') as fp:
    json.dump(data, fp)
