from wagtail.core.models import Page
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "remove all users that do not have content created or admin access"

    def handle(self, *args, **options):
        pages = Page.objects.all()
        keep_users = []
        orphaned_books = []

        # we want to save all superuser accounts and content creator accounts
        save_groups = ["Blogger", "Content Development Intern", "Content Managers", "Content Provider", "Customer Service", "Editors"]
        save_users_in_groups = User.objects.filter(groups__name__in=save_groups)
        for user in save_users_in_groups:
            keep_users.append(user.pk) # keeping all users in the above groups
        print("Keeping {} users in administrative roles.".format(save_users_in_groups.count()))

        supserusers = User.objects.filter(is_superuser=True)
        for user in supserusers:
            keep_users.append(user.pk) # keeping all superusers
        print("Keeping {} users with the superuser delegation.".format(supserusers.count()))

        owner_count = 0
        for page in pages:
            try:
                if page.owner:
                    keep_users.append(page.owner.pk) # keeping all page owners
                    owner_count = owner_count + 1
            except User.DoesNotExist:
                # TODO: Should we do something about this here - assign to existing user?
                orphaned_books.append(page)
                #print("Owner for {} for page does not exist on this system.".format(page.title))
        print("Keeping {} users that have authored content in the CMS.".format(owner_count))
        print("Found {} books that have no owner (owner deleted previously).".format(len(orphaned_books)))


        keep_users = set(keep_users) # convert list to set so we have a unique list of users to keep
        print("Converging unique users. {} users will be kept.".format(len(keep_users)))

        users_all = User.objects.all()
        print("{} - Total users on the system".format(users_all.count()))

        users_slated_for_removal = User.objects.all().exclude(pk__in=set(keep_users))
        print("{} - Total users slated for removal".format(users_slated_for_removal.count()))

        users_slated_for_removal.delete()
        print("Users have been successfully pruned!")
