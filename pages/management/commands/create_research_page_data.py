import json
from django.core.management.base import BaseCommand
from pages.models import ResearchPage


# Questions for ed:
# - Time between setting up data & deploying the public page
# - How to link out to images
# - How to handle nested sets of data (research_areas_list -> research_areas)

class Command(BaseCommand):
	help = "Populate research pages after a deployment"

	def handle(self, *args, **options):
		research_page = ResearchPage(
			mission_header='Research Mission',
			mission_body='Advancing interdisciplinary research in learning sciences, education, and allied disciplines, to improve learner success.',
			banner_header='',
			banner_body='',
			bannerCTA='',
			bannerURL='',
			research_area_header='Areas of Research Focus',
			research_area_description='Our team has significant expertise in <strong>learning science, education research, and AI/ML in education.</strong> We use a multidisciplinary approach to examine who our learners are, what are they learning, and how are they learning; to provide appropriate supports when and where learners need them. To enable large-scale rapid cycle research, we are developing Kinetic, a research infrastructure connecting researchers with adult higher ed learners in the US.',
			research_areas_list=json.dumps([
				{
					"type": "research_area_section",
					"value": [
						{
							"research_area_title": "Placeholder category",
							"research_area_blurb": "Placeholder text",
							"research_area_blurb_mobile": "Placeholder text",
							"research_areas": [
								{
									"header": "",
									"description": "",
									"short_description": "",
									"photo": "",
									"cta_text": "",
									"cta_link": "",
									"publication": "",
									"github": "",
								}
							]
						}
					]
				}
			]),
			people_header='Team Members',
			current_members=json.dumps([
				{
					"type": "person",
					"value": [
						{
							"first_name": "",
							"last_name": "",
							"title": "",
							"long_title": "",
							"bio": "",
							"education": "",
							"specialization": "",
							"research_interest": "",
							"photo": "",
							"website": "",
							"linked_in": "",
							"google_scholar": ""
						}
					]
				}
			]),
			collaborating_researchers=json.dumps([
				{
					"type": "person",
					"value": [
						{
							"first_name": "",
							"last_name": "",
							"title": "",
							"long_title": "",
							"bio": "",
							"education": "",
							"specialization": "",
							"research_interest": "",
							"photo": "",
							"website": "",
							"linked_in": "",
							"google_scholar": ""
						}
					]
				}
			]),
			alumni=json.dumps([
				{
					"type": "person",
					"value": [
						{
							"name": "",
							"title": "",
							"linked_in": ""
						}
					]
				}
			]),
			publication_header="Publications",
			publications=json.dumps([
				{
					"type": "publication",
					"value": [
						{
							"authors": "",
							"date": "",
							"title": "",
							"excerpt": "",
							"pdf": "",
							"github": "",
						}
					]
				}
			])
		)
		revision = research_page.save_revision()
		revision.publish()
		research_page.save()
