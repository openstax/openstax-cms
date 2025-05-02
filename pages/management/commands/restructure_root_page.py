from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from pages.models import HomePage, RootPage

class Command(BaseCommand):
    help = (
        "Move children of HomePage to RootPage, elevate RootPage to site root, and delete HomePage.\n"
        "⚠️ DRY RUN BY DEFAULT — use --commit to make changes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            help="Apply the changes. Without this flag, the command runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        commit = options['commit']

        old_home = HomePage.objects.first()
        new_root = RootPage.objects.first()

        if not old_home or not new_root:
            self.stderr.write(self.style.ERROR("Missing HomePage or RootPage instance."))
            return

        self.stdout.write(self.style.WARNING(
            f"{'[COMMIT MODE]' if commit else '[DRY RUN]'} Starting restructure..."
        ))

        # Move children of HomePage (except RootPage) under RootPage
        for child in old_home.get_children().exclude(id=new_root.id):
            self.stdout.write(f" - Would move {child.title} (ID: {child.id}) under RootPage")
            if commit:
                child.move(new_root, pos='last-child')

        # Move RootPage to root
        wagtail_root = Page.get_first_root_node()
        self.stdout.write(f" - Would move RootPage (ID: {new_root.id}) to be child of root")
        if commit:
            new_root.move(wagtail_root, pos='last-child')

        # Update Site root
        site = Site.objects.get(is_default_site=True)
        self.stdout.write(f" - Would set Site.root_page to RootPage (ID: {new_root.id})")
        if commit:
            site.root_page = new_root
            site.save()

        if commit:
            self.stdout.write(self.style.SUCCESS("✅ Restructure complete. Site root updated."))
        else:
            self.stdout.write(self.style.WARNING("Dry run complete. No changes were made."))
