from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register('menus', views.MenusViewSet)
urlpatterns = router.urls