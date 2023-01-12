from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register('roles', views.RoleViewSet)
router.register('subjects', views.SubjectList, basename="Subjects")
router.register('erratacontent', views.ErrataContentViewSet, basename="ErrataContent")
router.register('subjectcategory', views.SubjectCategoryViewSet, basename="SubjectCategory")
router.register('givebanner', views.GiveBannerViewSet, basename="GiveBanner")
router.register('blogcontenttype', views.BlogContentTypeViewSet, basename="BlogContentType")
router.register('blogcollection', views.BlogCollectionViewSet, basename="BlogCollection")
urlpatterns = router.urls
