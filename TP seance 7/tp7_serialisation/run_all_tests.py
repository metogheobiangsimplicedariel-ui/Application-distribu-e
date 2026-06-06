import sys
import subprocess
import os

def get_python_exec():
    # Cherche l'environnement virtuel au niveau parent (dossier TP7)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_python_win = os.path.join(parent_dir, "venv", "Scripts", "python.exe")
    venv_python_unix = os.path.join(parent_dir, "venv", "bin", "python")
    
    if os.path.exists(venv_python_win):
        return venv_python_win
    elif os.path.exists(venv_python_unix):
        return venv_python_unix
    return sys.executable

def compile_protobuf(python_exe):
    proto_dir = os.path.join(os.path.dirname(__file__), "tp7.3_protobuf")
    proto_src = os.path.join(proto_dir, "proto", "document.proto")
    proto_out = os.path.join(proto_dir, "generated")
    proto_include = os.path.join(proto_dir, "proto")
    
    if not os.path.exists(proto_out):
        os.makedirs(proto_out)
        
    print(f"\n{'='*60}")
    print(f"Compilation de Protobuf avec {python_exe}...")
    print(f"{'='*60}")
    
    # On se place dans le dossier contenant le fichier proto pour que le chemin généré soit correct
    result = subprocess.run([
        python_exe, "-m", "grpc_tools.protoc",
        f"-I={proto_include}",
        f"--python_out={proto_out}",
        proto_src
    ])
    if result.returncode != 0:
        print("⚠️ Avertissement: La compilation Protobuf a echoue (grpcio-tools n'est peut-etre pas installe ?)")

def run_module(python_exe, script_path):
    print(f"\n{'='*60}")
    print(f"Execution de {script_path}")
    print(f"{'='*60}")
    script_abs_path = os.path.join(os.path.dirname(__file__), script_path)
    result = subprocess.run([python_exe, script_abs_path])
    return result.returncode == 0

if __name__ == "__main__":
    python_exe = get_python_exec()
    compile_protobuf(python_exe)

    scripts = [
        "tp7.1_contrat_json/main.py",
        "tp7.2_versioning_json/main.py",
        "tp7.3_protobuf/main.py",
        "tp7.4_pickle_policy/main.py",
    ]

    for script in scripts:
        run_module(python_exe, script)
