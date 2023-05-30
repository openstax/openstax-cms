from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register('oxmenus', views.OXMenusViewSet)
urlpatterns = router.urls