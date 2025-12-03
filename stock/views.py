from django.db import connection  # ← Ce manque probablement
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import ExtractYear
from rest_framework.decorators import api_view
from .models import ActionUtilisateur, Produit, Plat, IngredientPlat, Commande, Notification, Rapport, Utilisateur
from .serializers import ActionUtilisateurSerializer, ProduitSerializer, PlatSerializer, IngredientPlatSerializer, CommandeSerializer, NotificationSerializer, RapportSerializer, UtilisateurSerializer
from django.db.models import Sum
from django.contrib.auth.hashers import check_password
from datetime import timedelta
from django.utils import timezone


from django.shortcuts import render

def home(request):
    return render(request, "dist/index.html")  # car index.html est dans templates/dist/

def login_page(request):
    return render(request, "dist/pages/samples/login.html")

def plat(request):
    return render(request, "dist/pages/forms/plat.html")

def plats(request):
    return render(request, "dist/pages/forms/plats.html")

def produit(request):
    return render(request, "dist/pages/forms/basic_elements.html")

def produits(request):
    return render(request, "dist/pages/forms/listProduits.html")

def user(request):
    return render(request, "dist/pages/forms/user.html")

def users(request):
    return render(request, "dist/pages/forms/users.html")

def commande(request):
    return render(request, "dist/pages/forms/commande.html")

def notification(request):
    return render(request, "dist/pages/forms/notification.html")

def comEm(request):
    return render(request, "dist/pages/forms/comEm.html")

def commandes(request):
    return render(request, "dist/pages/forms/commandes.html")

@api_view(['GET'])
def plats_par_quantite(request):
    plats = Plat.objects.all()
    data = []

    for plat in plats:
        total = Commande.objects.filter(plat=plat).aggregate(total=Sum('quantite'))['total'] or 0
        data.append({
            'nom': plat.nom,
            'quantite': total
        })

    return JsonResponse(data, safe=False)

@api_view(['POST'])
def test_create_commande(request):
    print("🚀 test_create_commande appelée")
    return Response({"message": "Test create OK"})
class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer

    
class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    



class PlatViewSet(viewsets.ModelViewSet):
    queryset = Plat.objects.all()
    serializer_class = PlatSerializer


class IngredientPlatViewSet(viewsets.ModelViewSet):
    queryset = IngredientPlat.objects.all()
    serializer_class = IngredientPlatSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-date')
    serializer_class = NotificationSerializer

    @action(detail=False, methods=['post'])
    def delete_selected(self, request):
        ids = request.data.get('ids', [])
        Notification.objects.filter(id__in=ids).delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
    
    def create_unique_notification(message, type, hours_window=24):
        """
        Crée une notification uniquement si une notification identique n'existe pas
        dans les dernières `hours_window` heures.
        """
        recent_time = timezone.now() - timedelta(hours=hours_window)
        
        # Vérifie si une notification du même message et type existe déjà
        if not Notification.objects.filter(
            message=message,
            type=type,
            date__gte=recent_time
        ).exists():
            Notification.objects.create(message=message, type=type)
    



class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

    def create(self, request, *args, **kwargs):
        plat_id = request.data.get("plat")
        quantite = int(request.data.get("quantite", 1))
        plat = Plat.objects.get(id=plat_id)
        commande = Commande(plat=plat, quantite=quantite)
        try:
            commande.valider_et_enregistrer()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Générer alertes ici aussi si nécessaire

        serializer = self.get_serializer(commande)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def dashboard_view(request):
    total_commandes = Commande.objects.count()
    total_produits = Produit.objects.count()
    total_plats = Plat.objects.count()

    seuil_critique = Produit.objects.filter(quantite__lte=10).count()  # seuil critique = 10

    commandes_par_mois = (
        Commande.objects
        .extra(
            select={
                'mois': "EXTRACT(MONTH FROM date_commande)" if 'sqlite' not in connection.vendor 
                       else "strftime('%%m', date_commande)"
            }
        )
        .values('mois')
        .annotate(nombre=Count('id'))
        .order_by('mois')
    )

    data = {
        'total_commandes': total_commandes,
        'total_produits': total_produits,
        'total_plats': total_plats,
        'seuil_critique': seuil_critique,
        'commandes_par_mois': list(commandes_par_mois),
    }
    

    return JsonResponse(data)

class AvailableYearsView(APIView):
    def get(self, request):
        # Extraire les années distinctes à partir du champ date_commande
        years = Commande.objects.annotate(year=ExtractYear('date_commande')) \
                               .values_list('year', flat=True) \
                               .distinct() \
                               .order_by('-year')
        years_list = list(years)
        return Response(years_list, status=status.HTTP_200_OK)


class RapportViewSet(viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer

class ActionUtilisateurViewSet(viewsets.ModelViewSet):
    queryset = ActionUtilisateur.objects.all()
    serializer_class = ActionUtilisateurSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        motDePasse = request.data.get("motDePasse")

        try:
            user = Utilisateur.objects.get(email=email)
            if check_password(motDePasse, user.motDePasse):
                return Response({
                    "message": "Connexion réussie",
                    "token": "FAKE_TOKEN",  # ici tu peux générer un vrai token si besoin
                    "nom": user.nom,
                    "email": user.email,
                    "role": user.role
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        except Utilisateur.DoesNotExist:
            return Response({"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)

