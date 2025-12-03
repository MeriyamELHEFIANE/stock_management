"""
URL configuration for stock_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from stock import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stock.urls')),
    path('', views.home,name='home'), 
    path('login/', views.login_page,name='login'),
    path('ajout_plat/', views.plat,name='ajout_plat'),
    path('plats/', views.plats,name='plats'),
    path('ajout_produit/', views.produit,name='ajout_produit'),
    path('produits/', views.produits,name='produits'),
    path('add_user/', views.user,name='add_user'),
    path('users/', views.users,name='users'),
    path('commande/', views.commande,name='commande'),
    path('notifications/', views.notification,name='notification'),
    path('comEm/', views.comEm,name='comEm'),
    path('commandes/', views.commandes,name='commandes'),
    
]
