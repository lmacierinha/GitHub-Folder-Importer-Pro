# GitHub Folder Importer Pro — Migração em Massa para o GitHub

Ferramenta gratuita e open-source para **migrar dezenas/centenas de projetos antigos de uma vez só** para o GitHub, com apenas alguns cliques.

Perfeita para quem tem uma pasta cheia de projetos antigos (Delphi, Python, .NET, PHP, Node.js, querys SQL, etc.) e quer colocar tudo no GitHub de forma organizada, com:

- Repositório criado automaticamente (se não existir)
- Detecção automática da linguagem/tecnologia
- .gitignore correto baixado do GitHub oficial
- Branches `main` e `develop` criados
- Branch padrão já configurado como `develop`
- Suporte a pastas com milhares de arquivos .sql ou qualquer outra linguagem
- Interface gráfica simples e em português
- Totalmente offline depois da primeira execução (opcional .exe)

Desenvolvido por **Luis Claudio Silveira Macierinha** com ajuda valiosa do Grok (xAI) — 2025

## Funcionalidades

- Detecta automaticamente: Delphi, Python, .NET/C#, Java, Node.js, PHP, Go, Ruby, React, Vue, etc.
- Cria repositórios privados ou públicos
- Adiciona .gitignore oficial da linguagem
- Corrige automaticamente problemas comuns do Windows (dubious ownership, 408 RPC failed, etc.)
- Funciona com pastas enormes de querys SQL, backups, fontes antigos, etc.

## Download (pronto para usar — sem instalar Python)

**Versão Windows (executável único — 82 MB):**

[GitHub-Folder-Importer-Pro-v1.6.exe](https://drive.google.com/file/d/1q8xY8z8v8k8x9j0k1l2m3n4o5p6q7r8s/view?usp=sharing)

Ou baixe a última versão na aba Releases → https://github.com/lmacierinha/GitHub-Folder-Importer-Pro/releases

## Como usar (3 passos)

1. Baixe e execute o `.exe` (ou rode com Python)
2. Preencha:
   - Pasta raiz com seus projetos
   - Seu usuário do GitHub
   - Um Personal Access Token (classic) com permissão `repo`
3. Clique em **INICIAR IMPORTAÇÃO**

Pronto! Todos os projetos serão criados e enviados automaticamente.

## Token do GitHub — como gerar

1. Acesse: https://github.com/settings/tokens
2. Generate new token → Generate new token (classic)
3. Dê um nome (ex: "Importer Pro")
4. Marque apenas a caixa **`repo`** (acesso completo)
5. Gere e copie o token (começa com `ghp_`)

## Requisitos (apenas se for rodar com Python)

```bash
pip install PyQt6 PyGithub gitpython requests tqdm