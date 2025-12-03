from django.contrib import admin
from django.forms import ValidationError
from stock.models import ActionUtilisateur, Commande, IngredientPlat, Notification, Plat, Produit, Rapport, Utilisateur


class IngredientPlatInline(admin.TabularInline):
    model = IngredientPlat
    extra = 1

class PlatAdmin(admin.ModelAdmin):
    inlines = [IngredientPlatInline]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "type", "date")
    list_filter = ("type", "date")
    ordering = ("-date",)
    search_fields = ("message",)

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        plat = obj.plat

        # Vérifie la disponibilité des ingrédients
        for ingredient in plat.ingredients.all():
            if ingredient.produit.quantite < ingredient.quantite_necessaire:
                raise ValidationError(
                    f"❌ Impossible d'ajouter la commande : le produit '{ingredient.produit.nom}' est insuffisant ou épuisé."
                )

        # Si tu as une méthode valider_et_enregistrer(), appelle-la ici
        obj.valider_et_enregistrer()

        # Déduction du stock
        # for ingredient in plat.ingredients.all():
        #     produit = ingredient.produit
        #     produit.quantite -= ingredient.quantite_necessaire
        #     produit.save()

        # # Génération des alertes
        # for produit in Produit.objects.all():
        #     messages = produit.generer_alertes()
        #     for message in messages:
        #         type_alerte = "info"
        #         if "épuisé" in message:
        #             type_alerte = "epuise"
        #         elif "critique" in message:
        #             type_alerte = "critique"
        #         elif "péremption" in message:
        #             type_alerte = "peremption"
        #         Notification.objects.create(message=message, type=type_alerte)



# Register your models here.
admin.site.register(Produit)
admin.site.register(Plat, PlatAdmin)
admin.site.register(IngredientPlat)
admin.site.register(Utilisateur)
admin.site.register(Rapport)
admin.site.register(ActionUtilisateur)