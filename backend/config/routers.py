from rest_framework.routers import DefaultRouter
from calc.views import MortgageViewSet

router = DefaultRouter()
router.register('offer', MortgageViewSet, basename='CRUD_mortgage')
