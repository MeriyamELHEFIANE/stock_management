from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

class Utilisateur(models.Model):
    ROLE_CHOICES = [('admin', 'Administrateur'), ('gestionnaire', 'Gestionnaire'), ('employe', 'Employé')]
    
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    motDePasse = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    def save(self, *args, **kwargs):
        # Hasher le mot de passe avant de sauvegarder si ce n'est pas déjà hashé
        if not self.motDePasse.startswith('pbkdf2_'):
            self.motDePasse = make_password(self.motDePasse)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom


class ActionUtilisateur(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    action = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    quantite = models.FloatField()
    unite = models.CharField(max_length=20)
    seuil_critique = models.FloatField()
    date_peremption = models.DateField()

    def est_critique(self):
        return self.quantite <= self.seuil_critique

    def est_proche_peremption(self):
        return self.date_peremption - timezone.now().date() <= timedelta(days=3)

    def est_epuise(self):
        return self.quantite <= 0

    def generer_alertes(self):
        alertes = []
        if self.est_epuise():
            alertes.append(f"🚨 Le produit '{self.nom}' est épuisé.")
        elif self.est_critique():
            alertes.append(f"⚠️ Le produit '{self.nom}' a atteint le seuil critique.")
        if self.est_proche_peremption():
            alertes.append(f"⏳ Le produit '{self.nom}' approche de sa date de péremption.")
        return alertes


    def __str__(self):
        return self.nom


class Plat(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom


class IngredientPlat(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name="ingredients")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite_necessaire = models.FloatField()

    def __str__(self):
        return f"{self.quantite_necessaire} {self.produit.unite} de {self.produit.nom} pour {self.plat.nom}"
#LE 1ER CODE

# class Commande(models.Model):
#     plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
#     date_commande = models.DateTimeField(auto_now_add=True)

class Commande(models.Model):
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    date_commande = models.DateTimeField(auto_now_add=True)

    def valider_et_enregistrer(self):
        # Vérifier stock
        for ingredient in self.plat.ingredients.all():
            total_necessaire = ingredient.quantite_necessaire * self.quantite
            if ingredient.produit.quantite < total_necessaire:
                raise ValidationError(
                    f"❌ Produit '{ingredient.produit.nom}' insuffisant."
                )
        
        # Sauvegarder la commande
        self.save()

        # Déduire le stock
        for ingredient in self.plat.ingredients.all():
            produit = ingredient.produit
            produit.quantite -= ingredient.quantite_necessaire * self.quantite
            produit.save()
        # Génération des alertes
        for produit in Produit.objects.all():
            messages = produit.generer_alertes()
            for message in messages:
                type_alerte = "info"
                if "épuisé" in message:
                    type_alerte = "epuise"
                elif "critique" in message:
                    type_alerte = "critique"
                elif "péremption" in message:
                    type_alerte = "peremption"
                Notification.objects.create(message=message, type=type_alerte)


class Notification(models.Model):
    message = models.TextField()
    type = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.type}]- {self.date.strftime('%Y-%m-%d %H:%M:%S')}] {self.message[:50]}"

    
class Rapport(models.Model):
    dateDebut = models.DateField()
    dateFin = models.DateField()
    contenu = models.TextField()

