import Pyro5.api

TOKEN = "secret-tp10-2026"  # Token valide

def main():
    print("\n=== CLIENT DOCUMENT SERVICE ===\n")
    
    try:
        ns = Pyro5.api.locate_ns()
        uri = ns.lookup("document.service")
        service = Pyro5.api.Proxy(uri)
        print("Connecte au service\n")
    except:
        print("Erreur: Serveur non trouve")
        return
    
    while True:
        print("\n" + "-"*30)
        print("MENU")
        print("-"*30)
        print("1. Lister les documents")
        print("2. Voir un document (avec token)")
        print("3. Quitter")
        print("-"*30)
        
        choix = input("Votre choix: ")
        
        if choix == "1":
            print("\nDocuments:")
            docs = service.list_documents()
            for doc in docs:
                print(f"  - {doc}")
        
        elif choix == "2":
            nom = input("\nNom du document: ")
            try:
                # Envoyer le token avec la requete
                contenu = service.get_document_content(nom, TOKEN)
                print(f"\n--- {nom} ---")
                print(contenu)
            except PermissionError as e:
                print(f"Erreur permission: {e}")
            except KeyError as e:
                print(f"Erreur: {e}")
        
        elif choix == "3":
            print("Au revoir!")
            break
        
        else:
            print("Choix invalide")
        
        input("\nAppuyez sur Entree...")

if __name__ == "__main__":
    main()