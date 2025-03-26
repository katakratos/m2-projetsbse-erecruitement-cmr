from app.services.database import Base, engine

# Charge les modèles ici pour s'assurer qu'ils sont bien pris en compte
# import app.models.user.user

print("Création des tables dans la base de données...")
Base.metadata.create_all(bind=engine)
print("Tables créées avec succès !")
def init_db():
    """Initialise la base de données (utile uniquement en développement)."""
    print("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)  # Crée les tables si elles n'existent pas encore

if __name__ == "__main__":
    init_db()

