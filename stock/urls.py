from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvailableYearsView, LoginView, ProduitViewSet, PlatViewSet, IngredientPlatViewSet, CommandeViewSet, NotificationViewSet, UtilisateurViewSet, dashboard_view,  plats_par_quantite
from stock import views

router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'plats', PlatViewSet)
router.register(r'ingredients', IngredientPlatViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'utilisateurs', UtilisateurViewSet)





urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/years/', AvailableYearsView.as_view(), name='available_years'),
    path('login/', LoginView.as_view(), name='login'),
    path('plats-par-quantite/', plats_par_quantite, name='plats_par_quantite'),

]
