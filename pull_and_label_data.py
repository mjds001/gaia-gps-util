"""
this file is used to rename and save images from a .geojson file exported from Gaia GPS.
To get this file, go to Gaia GPS, log in, click on "saved items", click the folder you want to export, 
under the overview tab click on "export", and select the format as .geojson
"""

import json
import requests
import os


##### inputs ######
# the name of the .geojson file exported from Gaia GPS
WALL_FILE = os.getenv('WALL_FILE') or 'walls.geojson'
# local folder name to save the images in
IMAGES_FOLDER = os.getenv('IMAGES_FOLDER') or 'wall_images'
# the SESSION_ID cookie is needed to authenticate the request to download the images
# without it the request will return a 403 error (assuming the images are private)
# to get the cookie, open gaia gps in a browser, log in, open the dev tools (right click, inspect), go to the application tab,
# click on COOKIES, click on the gaia gps cookie, find the sessionid key and export the value to an env var
SESSION_ID = os.getenv('SESSION_ID')
if not SESSION_ID:
    print('no session id cookie provided')
    exit()

COOKIES = {
    'sessionid': SESSION_ID
}

def main():
    # open the walls file
    with open(WALL_FILE) as f:
        data = json.load(f)

    # itterate through each waypoint
    for feature in data['features']:
        feature_title = feature['properties']['title']
        print(f'Getting images for {feature_title}...')

        # if there are no photos, skip
        if 'photos' not in feature['properties']:
            continue

        # if there is only one photo
        if len(feature['properties']['photos']) == 1:
            photo = feature['properties']['photos'][0]
            photo_fullsize_url = photo['fullsize_url']
            photo_name = f'{IMAGES_FOLDER}/{feature_title}.jpg'
            if photo_name in os.listdir(IMAGES_FOLDER):
                print(f'{photo_name} already exists, skipping...')
                continue
            save_image(photo_fullsize_url, photo_name)

        # if there are multiple photos
        else:
            # create a folder for the images for that wall if it doesn't already exist
            if feature_title not in os.listdir(IMAGES_FOLDER):
                os.mkdir(f'{IMAGES_FOLDER}/{feature_title}')
            for idx, photo in enumerate(feature['properties']['photos'], start=1):
                photo_fullsize_url = photo['fullsize_url']
                photo_name = f'{IMAGES_FOLDER}/{feature_title}/{feature_title}{idx}.jpg'
                if photo_name in os.listdir(IMAGES_FOLDER):
                    print(f'{photo_name} already exists, skipping...')
                    continue
                save_image(photo_fullsize_url, photo_name)

def save_image(photo_url, name):
    response = requests.get(photo_url, cookies=COOKIES)
    if response.status_code == 200:
        with open(name, 'wb') as f:
            f.write(response.content)
    else:
        print(f'!!!!!! Error downloading {photo_url}. Status code: {response.status_code} !!!!!!')
        

if __name__ == '__main__':
    main()
