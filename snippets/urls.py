from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'subjects', views.SubjectList, basename="Subjects")
router.register(r'erratacontent', views.ErrataContentViewSet, basename="ErrataContent")
router.register(r'subjectcategory', views.SubjectCategoryViewSet, basename="SubjectCategory")
router.register(r'givebanner', views.GiveBannerViewSet, basename="GiveBanner")
router.register(r'blogcontenttype', views.BlogContentTypeViewSet, basename="BlogContentType")
router.register(r'blogcollection', views.BlogCollectionViewSet, basename="BlogCollection")
urlpatterns = router.urls
