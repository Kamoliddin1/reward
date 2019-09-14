from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, DispatcherViewSet, DriverViewSet, RelationshipViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'dispatchers', DispatcherViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'relationships', RelationshipViewSet)

urlpatterns = router.urls
