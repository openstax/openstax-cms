import ast
from django.core.management.base import BaseCommand
from salesforce.models import School, MapBoxDataset
from django.core.files.storage import get_storage_class
from mapbox import Uploader
from django.conf import settings

import json
import os
import tempfile


class Command(BaseCommand):
    help = "upload geoJSON school data to Mapbox"

    def handle(self, *args, **options):

        try:
            # Try to load the tileset with tileset information from Django database.
            print("Trying to load the tileset from Django database...")

            # Retrieving the first record.
            mapbox_tileset = MapBoxDataset.objects.first()
            tileset_id = mapbox_tileset.tileset_id
            tileset_name = mapbox_tileset.name

            print("Found tileset:", tileset_id)

        except IndexError:
            # If there is no such tileset, we are going to create one.
            print("Could not find a tileset. Please create a tileset in Django database before this process.")

            tileset_id = None
        
        # Stopping if no tileset is found.
        if not tileset_id:
            pass
        
        # Initializing uploader service.
        service = Uploader(access_token=settings.MAPBOX_TOKEN)

        # Retrieving schools list.
        schools = School.objects.all()
        
        # Initializing json response.
        allfeatures = {
            "features": [],
            "type": "FeatureCollection"
        }

        # Loading all school information to the json response.
        for school in schools:
            if school.lat and school.long:
                if school.lat != 0 or school.long != 0:
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': "Point",
                            'coordinates': [float(school.long), float(school.lat)]
                        },
                        'properties': {
                            'name': school.name,
                            'id': school.id
                        }
                    }
                    allfeatures["features"].append(feature)

        file_storage = get_storage_class()()

        with tempfile.TemporaryDirectory() as tempdir:
            fname = os.path.join(tempdir, 'schools.geojson')
            with open(fname, 'w') as f:
                f.write(json.dumps(allfeatures))
                
            with open(fname, 'rb') as f:
                upload_resp = service.upload(f, tileset_id, name=tileset_name)
                
                if upload_resp.status_code == 201:
                    print("Upload successful.")
                else:
                    print("Upload failed with code:", upload_resp.status_code)