import os
import time
import subprocess
import sys

counter = 60

def kill_analysis_service():
    if sys.platform == "win32":
        # Utilisation de wmic sur Windows pour tuer le processus Python spécifique
        cmd = 'wmic process where "commandline like \'%app/analysis/main.py%\' and name like \'%python%\'" call terminate'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if "ReturnValue = 0" in result.stdout or "Method execution successful" in result.stdout:
            return True
        return False
    else:
        # Pour Linux/Mac
        cmd = "pkill -f 'python.*app/analysis/main.py'"
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0

if __name__ == "__main__":
    print("="*60)
    print("   DÉMONSTRATION DU CIRCUIT BREAKER & FALLBACK")
    print("="*60)
    print("\n1. Arrêt brutal de l'AnalysisService (Simulation de Crash)...")
    
    if kill_analysis_service():
        print("[+] Service d'analyse arrêté avec succès.")
    else:
        print("[-] Avertissement : Impossible de confirmer l'arrêt. Le service est peut-être déjà arrêté.")
        
    print("\n[!] L'AnalysisService est maintenant HORS-LIGNE.")
    print("--> Action requise : Allez VITE sur l'interface Web (http://127.0.0.1:8000)")
    print("--> Soumettez un e-mail pour voir le FALLBACK en action (le disjoncteur s'ouvrira).")
    print(f"\nAttente {counter} de secondes avant de redémarrer le service...")
    
    for i in range(counter, 0, -1):
        sys.stdout.write(f"\rRedémarrage dans {i} secondes... ")
        sys.stdout.flush()
        time.sleep(1)
        
    print("\n\n2. Redémarrage de l'AnalysisService (Simulation de rétablissement)...")
    
    # Configuration du chemin d'accès Python de l'environnement virtuel
    if sys.platform == "win32":
        python_bin = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
    else:
        python_bin = os.path.join(os.path.dirname(__file__), ".venv", "bin", "python")
        
    if not os.path.exists(python_bin):
        python_bin = sys.executable

    # Relancer le service en arrière-plan sans bloquer
    subprocess.Popen(
        [python_bin, "app/analysis/main.py"],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print("[+] L'AnalysisService est de nouveau EN LIGNE.")
    print("--> Le Circuit Breaker passera en mode HALF-OPEN (Test) à la prochaine requête, puis CLOSED.")
    print("--> Retournez soumettre un e-mail sur la Web UI pour constater le retour au système normal sans FALLBACK.")
    print("="*60)
