from rest_framework import serializers
from .models import ActionUtilisateur, Produit, Plat, IngredientPlat, Commande, Notification, Rapport, Utilisateur


from rest_framework import serializers
from .models import Utilisateur

class UtilisateurSerializer(serializers.ModelSerializer):
    motDePasse = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Utilisateur
        fields = ['id', 'nom', 'email', 'motDePasse', 'role']

    def update(self, instance, validated_data):
        # empêcher la mise à jour du mot de passe si non envoyé
        password = validated_data.pop('motDePasse', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.motDePasse = password  # ou hash si nécessaire

        instance.save()
        return instance


    
class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class IngredientPlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientPlat
        fields = '__all__'

class PlatSerializer(serializers.ModelSerializer):
    ingredients = IngredientPlatSerializer(many=True, read_only=True)

    class Meta:
        model = Plat
        fields = '__all__'
#le 1er code
# class CommandeSerializer(serializers.ModelSerializer):
#     plat = PlatSerializer(read_only=True)
#     class Meta:
#         model = Commande
#         fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    plat = PlatSerializer(read_only=True)
    plat_id = serializers.PrimaryKeyRelatedField(queryset=Plat.objects.all(), source='plat', write_only=True)
    
    class Meta:
        model = Commande
        fields = ['id', 'plat', 'plat_id', 'quantite', 'date_commande']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = '__all__'

class ActionUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionUtilisateur
        fields = '__all__'



        


