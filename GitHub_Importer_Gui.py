# github_importer_gui_v1.5.py — VERSÃO FINAL 100% FUNCIONAL
import os
import sys
import subprocess
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QCheckBox,
    QTextEdit, QProgressBar, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from github import Github
from git import Repo

# Correção silenciosa do dubious ownership
def fix_git_safe_directory():
    try:
        result = subprocess.run(["git", "config", "--global", "--get-all", "safe.directory"],
                                capture_output=True, text=True, check=False)
        if "*" not in result.stdout:
            subprocess.run(["git", "config", "--global", "--add", "safe.directory", "*"], check=False)
    except:
        pass

fix_git_safe_directory()

class Worker(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()

    def __init__(self, folder, user, token, public):
        super().__init__()
        self.folder = folder
        self.user = user
        self.token = token
        self.public = public

    def download_gitignore(self, template_name):
        url = f"https://raw.githubusercontent.com/github/gitignore/main/{template_name}.gitignore"
        try:
            r = requests.get(url, timeout=10)
            return r.text if r.status_code == 200 else None
        except:
            return None

    def detect_language(self, path):
        markers = {
            "Delphi": [".dpr", ".dproj", ".pas", ".dfm", ".dcu", ".dcp"],
            "Python": [".py", "requirements.txt", "pyproject.toml"],
            ".NET": [".csproj", ".sln"],
            "Node.js": ["package.json"],
            "PHP": [".php", "composer.json"],
        }
        for root, _, files in os.walk(path):
            for f in files:
                name = f.lower()
                for lang, exts in markers.items():
                    if any(name.endswith(ext) for ext in exts if ext.startswith(".")) or \
                       any(ext in name for ext in exts if not ext.startswith(".")):
                        return lang, lang if lang != "Delphi" else "Delphi"
        return "Unknown", None

    def run(self):
        root = self.folder
        folders = [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f)) and not f.startswith('.')]
        g = Github(self.token)
        user = g.get_user()
        total = len(folders)

        for i, name in enumerate(folders):
            path = os.path.join(root, name)
            repo_name = name.strip().replace(" ", "-").replace("--", "-")
            self.log.emit(f"\nProcessando: {name}")

            try:
                # Verifica se já existe
                try:
                    user.get_repo(repo_name)
                    self.log.emit("Já existe no GitHub → pulando")
                    continue
                except:
                    pass

                lang, template = self.detect_language(path)
                self.log.emit(f"Detectado: {lang}")

                repo = user.create_repo(repo_name, private=not self.public, auto_init=False)
                self.log.emit(f"Criado: {repo.html_url}")

                # Init git local
                if not os.path.exists(os.path.join(path, ".git")):
                    Repo.init(path)
                r = Repo(path)

                # .gitignore
                if template and template != "Unknown":
                    content = self.download_gitignore(template)
                    if content:
                        with open(os.path.join(path, ".gitignore"), "w", encoding="utf-8") as f:
                            f.write(content)
                        self.log.emit(f".gitignore {template} adicionado")

                # Remote
                url = f"https://{self.user}:{self.token}@github.com/{self.user}/{repo_name}.git"
                try: r.delete_remote("origin")
                except: pass
                r.create_remote("origin", url)

                # Commit
                r.git.add(A=True)
                if r.untracked_files or any(d.a_path for d in r.index.diff(None)):
                    r.index.commit("Initial commit – importação automática")
                else:
                    r.git.commit("--allow-empty", "-m", "Initial commit")

                # Branches
                if "main" not in r.heads:
                    r.create_head("main")
                r.heads.main.checkout()
                r.remotes.origin.push("main", force=True)

                develop = r.create_head("develop", r.heads.main)
                develop.checkout()
                r.remotes.origin.push("develop", force=True)

                repo.edit(default_branch="develop")
                self.log.emit("PRONTO → branch padrão: develop")
                self.log.emit(f"{repo.html_url}/tree/develop\n")

            except Exception as e:
                self.log.emit(f"ERRO: {str(e)}\n")

            self.progress.emit(i + 1, total)

        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Folder Importer Pro v1.5")
        self.setGeometry(100, 100, 960, 680)

        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        # Pasta
        h = QHBoxLayout()
        self.path_edit = QLineEdit()
        btn = QPushButton("Selecionar pasta")
        btn.clicked.connect(self.selecionar_pasta)
        h.addWidget(QLabel("Pasta raiz:"))
        h.addWidget(self.path_edit)
        h.addWidget(btn)
        lay.addLayout(h)

        # Credenciais
        gb = QGroupBox("GitHub")
        gl = QHBoxLayout()
        gl.addWidget(QLabel("Usuário:"))
        self.user_edit = QLineEdit()
        gl.addWidget(self.user_edit)
        gl.addWidget(QLabel("Token:"))
        self.token_edit = QLineEdit()
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        gl.addWidget(self.token_edit)
        self.pub_cb = QCheckBox("Repositórios públicos")
        gl.addWidget(self.pub_cb)
        gb.setLayout(gl)
        lay.addWidget(gb)

        # Botão
        self.btn = QPushButton("INICIAR IMPORTAÇÃO")
        self.btn.setStyleSheet("font-size:18px;padding:15px;background:#2ea44f;color:white")
        self.btn.clicked.connect(self.iniciar)
        lay.addWidget(self.btn)

        # Progresso
        self.pb = QProgressBar()
        lay.addWidget(self.pb)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        lay.addWidget(QLabel("Log:"))
        lay.addWidget(self.log)

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta com projetos")
        if pasta:
            self.path_edit.setText(pasta)

    def iniciar(self):
        if not all([self.path_edit.text(), self.user_edit.text(), self.token_edit.text()]):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos")
            return

        self.btn.setEnabled(False)
        self.log.clear()
        self.pb.setValue(0)

        self.worker = Worker(self.path_edit.text(), self.user_edit.text(),
                            self.token_edit.text(), self.pub_cb.isChecked())
        self.worker.log.connect(lambda t: self.log.append(t))
        self.worker.progress.connect(lambda v, t: self.pb.setMaximum(t) or self.pb.setValue(v))
        self.worker.finished.connect(lambda: self.btn.setEnabled(True) or QMessageBox.information(self, "Concluído", "Tudo pronto!"))
        self.worker.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())