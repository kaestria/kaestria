# Nexus - Terminal Virtual Machine

Uma máquina virtual de terminal escrita em C# que roda dentro do Windows e gerencia múltiplos sistemas operacionais virtuais.

## Requisitos

- .NET 8.0 ou superior
- Windows 10/11

## Compilação

### Via Terminal PowerShell:

```powershell
cd Nexus
dotnet build -c Release
```

### Executável gerado:
```
Nexus/bin/Release/net8.0/Nexus.exe
```

## Estrutura de Pastas

O Nexus cria automaticamente a seguinte estrutura:

```
C:\nexus\
├── machine\ (padrão)
│   ├── config.json
│   ├── OS\
│   └── Users\
│       └── [usuario]\
│           ├── profile.json
│           └── guard.json
├── [outras_maquinas]\
```

## Primeira Execução

1. Execute `Nexus.exe`
2. Selecione a máquina de boot (primeira vez terá apenas "machine")
3. Faça login com as credenciais padrão (nenhum usuário padrão é criado)
4. Use o comando `user new` como admin para criar novos usuários

## Comandos Principais

- `cd <path>` - Navegar entre diretórios
- `dir [path]` - Listar conteúdo
- `cat <file>` - Exibir arquivo
- `wget <url>` - Baixar arquivo
- `import -F/-D <caminho>` - Importar do Windows
- `export -F/-D <caminho>` - Exportar para Windows
- `user <new|list|delete>` - Gerenciar usuários
- `vm <list|new|delete>` - Gerenciar máquinas virtuais
- `guard <status|toggle|backup>` - Nexus Guard
- `run <script.task>` - Executar scripts
- `boot` - Carregar SO virtual
- `help` - Mostrar ajuda
- `exit` - Sair

## Arquitetura

### API HTTP Embutida

Porta: 6969
Endpoints (localhost apenas):
- POST /login
- POST /encrypt
- POST /decrypt
- POST /backup/create
- POST /backup/list
- POST /backup/delete
- POST /cmd/open
- POST /cmd/exec
- POST /cmd/read
- POST /cmd/close
- POST /cmd/list
- POST /boot

### Criptografia

Todos os arquivos da máquina (config.json, profile.json, guard.json) são criptografados usando a criptografia customizada.

### Nexus Guard

Sistema de proteção que oferece:
- Confirmação antes de executar scripts sensíveis
- Backups automáticos configuráveis
- Logs de operações

## Estrutura do Projeto

```
Nexus/
├── Encryption/       - Criptografia de dados
├── Machine/          - Gerenciamento de VMs
├── Users/            - Sistema de usuários
├── FileSystem/       - Sistema de arquivos virtual
├── Terminal/         - Terminal interativo
├── Guard/            - Proteção Nexus Guard
├── API/              - API HTTP embutida
├── System/           - Utilitários (Neofetch)
└── Program.cs        - Entry point
```

## Uso da API

Exemplo de login via HTTP:

```json
POST http://localhost:6969/login
{
  "username": "admin",
  "password": "senha"
}
```

Resposta:
```json
{
  "token": "uuid-aqui",
  "username": "admin",
  "role": "admin"
}
```

## Notas Importantes

- A pasta `OS/` não é criptografada (gerenciada pelo SO virtual)
- Apenas admins podem criar/deletar usuários e máquinas virtuais
- Tokens da API são armazenados em memória e destruídos ao encerrar
- Backups automáticos respeitam o intervalo configurado no guard.json

## Compilação para Release

```powershell
dotnet publish -c Release -r win-x64 --self-contained false
```

O executável estará em `bin/Release/net8.0/win-x64/publish/`
