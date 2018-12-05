import ast
from django.core.management.base import BaseCommand
from salesforce.models import School, MapBoxDataset
from mapbox import Datasets
from django.conf import settings


class Command(BaseCommand):
    help = "upload geoJSON school data to Mapbox"

    def handle(self, *args, **options):
        datasets = Datasets(access_token=settings.MAPBOX_TOKEN)
        try:
            mapbox_dataset = MapBoxDataset.objects.all()[0] #check if a dataset was already created
            dataset_id = mapbox_dataset.dataset_id
            dataset = datasets.read_dataset(dataset_id).json()
        except IndexError: #it wasn't, let's do that
            dataset = datasets.create(name='os-schools', description='A listing of OpenStax Adoptions')
            dataset_decoded = ast.literal_eval(dataset.content.decode())

            mapbox_dataset_created, _ = MapBoxDataset.objects.get_or_create(name=dataset_decoded["name"],
                                                                            dataset_id=dataset_decoded["id"])
            dataset_id = mapbox_dataset_created.dataset_id


        #cool - we have a dataset, now let's fill it with school location data
        schools = School.objects.all()
        total_schools = 0
        uploaded_schools = 0

        for school in schools:
            total_schools = total_schools + 1
            if school.lat and school.long:
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
                datasets.update_feature(dataset_id, school.pk, feature)
                uploaded_schools = uploaded_schools + 1


        self.stdout.write("Total schools: {}".format(total_schools))
        self.stdout.write("Total schools uploaded: {}".format(uploaded_schools))
        self.stdout.write("fin")
