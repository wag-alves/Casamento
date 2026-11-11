# Configuração do Classic Release no Azure DevOps

O `azure-pipelines.yml` faz a **CI**: valida o Django, sobe a stack e roda o Playwright, constrói as imagens e publica no
Docker Hub com tag semântica (`v1.0.1`, `v1.0.2`, …; **nunca `latest`**). A **CD** é criada pela interface
**Pipelines > Releases**, conforme exigido pelo trabalho. Os nomes de menus abaixo podem variar um pouco conforme a versão do Azure DevOps.

## Pré-requisitos

1. Repositório Git conectado ao Azure DevOps (branch `main`).
2. Conta Docker Hub `wagnernoronha` com repositórios **públicos** `casamento-backend` e `casamento-frontend`.
3. Service connection do tipo **Docker Registry** (Docker Hub), com o nome `dockerhub-service-connection` (o mesmo de `dockerRegistryServiceConnection` no YAML).
4. Service connection do tipo **Azure Resource Manager** com acesso ao grupo de recursos.
5. VM Linux na mesma VNet executando `database/compose.yaml` (ver abaixo).

## Criar os App Services (uma vez)

```bash
az login
az group create -n rg-casamento -l brazilsouth
az appservice plan create -g rg-casamento -n plan-casamento --is-linux --sku B1

# Em versões novas da CLI a opção -i chama-se --deployment-container-image-name
az webapp create -g rg-casamento -p plan-casamento -n NOME-DO-APP-BACKEND \
  -i wagnernoronha/casamento-backend:v1.0.1
az webapp create -g rg-casamento -p plan-casamento -n NOME-DO-APP-FRONTEND \
  -i wagnernoronha/casamento-frontend:v1.0.1
```

Use a tag da primeira build publicada. Depois disso, o Release passa a trocar a tag.

## Variáveis no App Service backend

Em **Configuration > Application settings** (ou pelo Release, veja abaixo):

| Variável | Valor |
|---|---|
| `WEBSITES_PORT` | `8000` |
| `DJANGO_SECRET_KEY` | chave longa e aleatória, exclusiva de produção |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `nome-do-app-backend.azurewebsites.net,nome-do-app-frontend.azurewebsites.net` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://nome-do-app-backend.azurewebsites.net,https://nome-do-app-frontend.azurewebsites.net` |
| `DATABASE_ENGINE` | `postgresql` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | credenciais do banco da VM |
| `POSTGRES_HOST` | IP privado da VM PostgreSQL |
| `POSTGRES_PORT` | `5432` |
| `RUN_MIGRATIONS` | `true` (instância única; com várias réplicas, rode `migrate` como etapa única do Release) |
| `CREATE_SUPERUSER`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | cria o usuário do `/admin/` na 1ª subida (depois pode voltar `CREATE_SUPERUSER` para `false`) |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `NOTIFICATION_EMAIL`, `PIX_KEY`, `PIX_NOME`, `PIX_CIDADE` | como no `.env.example` |

Opcionais (têm padrão): `GUNICORN_WORKERS`, `GUNICORN_TIMEOUT`, `DB_WAIT_TIMEOUT`, `DJANGO_TIME_ZONE`, `DJANGO_LOG_LEVEL`, `EMAIL_HOST`, `EMAIL_PORT`.

O entrypoint espera o banco ficar disponível (até `DB_WAIT_TIMEOUT` segundos), executa `collectstatic` e, com
`RUN_MIGRATIONS=true`, aplica `migrate` antes de iniciar o Gunicorn.

## Variáveis no App Service frontend

| Variável | Valor |
|---|---|
| `WEBSITES_PORT` | `80` |
| `BACKEND_SCHEME` | `https` |
| `BACKEND_HOST` | `nome-do-app-backend.azurewebsites.net` (somente o hostname, sem `https://`) |
| `BACKEND_PORT` | `443` |

O Nginx entrega `/static/` (incluindo o CSS do admin, coletado durante o build) e encaminha as demais rotas ao backend,
usando o hostname do backend no cabeçalho `Host` e no SNI TLS. O domínio público do frontend segue em `X-Forwarded-Host`
(com a porta, quando houver).

## Criar a definição de Release

1. **Pipelines > Releases > New pipeline** > **Empty job**; nome `Deploy casamento`.
2. **Artifacts > Add an artifact** > **Build**: escolha a pipeline que executa o `azure-pipelines.yml`, versão *Latest* e alias `Build`.
   (Opcional, para evidenciar o registro: adicione também dois artefatos **Docker Hub** com a service connection
   `dockerhub-service-connection`, namespace `wagnernoronha` e repositórios `casamento-backend` e `casamento-frontend`.)
3. Habilite o **Continuous deployment trigger** (ícone de raio) no artefato, se quiser deploy automático a cada build.
4. Em **Variables** do Release, crie: `DOCKERHUB_NAMESPACE=wagnernoronha`, `BACKEND_APP_NAME`, `FRONTEND_APP_NAME` e as
   variáveis da tabela do backend; marque como **secretas** `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, `EMAIL_HOST_PASSWORD`,
   `DJANGO_SUPERUSER_PASSWORD` e `PIX_KEY`.
5. Crie o stage `Deploy containers` e adicione as tarefas, todas com a service connection do Azure Resource Manager:
   1. **Azure Web App for Containers** (backend): *App name* `$(BACKEND_APP_NAME)`; *Image name*
      `$(DOCKERHUB_NAMESPACE)/casamento-backend:v$(Release.Artifacts.Build.BuildNumber)`; em *App settings*, as variáveis do backend
      (`-WEBSITES_PORT 8000 -DJANGO_DEBUG False -POSTGRES_PASSWORD $(POSTGRES_PASSWORD) ...`).
   2. **Azure Web App for Containers** (frontend): *App name* `$(FRONTEND_APP_NAME)`; *Image name*
      `$(DOCKERHUB_NAMESPACE)/casamento-frontend:v$(Release.Artifacts.Build.BuildNumber)`; *App settings*
      `-WEBSITES_PORT 80 -BACKEND_SCHEME https -BACKEND_HOST $(BACKEND_APP_NAME).azurewebsites.net -BACKEND_PORT 443`.
   3. **Bash** (validação), para o Release falhar se o site não subir:
      ```bash
      for i in $(seq 1 30); do
        code=$(curl -s -o /dev/null -w '%{http_code}' "https://$(FRONTEND_APP_NAME).azurewebsites.net/api/health/" || true)
        echo "tentativa $i: HTTP $code"; [ "$code" = "200" ] && exit 0; sleep 10
      done
      exit 1
      ```
6. Salve e crie uma Release. Se a variável `Release.Artifacts.Build.BuildNumber` não aparecer com esse nome, confira o alias do
   artefato em **Variables/Logs** da Release (o formato é `Release.Artifacts.<alias>.BuildNumber`).

> A CI nomeia cada execução `1.0.N` e publica a imagem como `v1.0.N`; por isso a tag do Release é `v` + `BuildNumber`.
> Para subir de versão maior ou menor, altere `majorMinor` no `azure-pipelines.yml`.

## VM PostgreSQL

1. Crie a VM Linux e associe-a à VNet usada pelo backend.
2. Copie `database/.env.example` para `database/.env`, preencha a senha e o IP privado da VM.
3. Execute `docker compose --env-file .env -f compose.yaml up -d` dentro da pasta `database`.
4. No NSG da VM, permita TCP/5432 somente a partir da sub-rede/rede privada do backend. Não crie regra `Any/Internet` para 5432.
5. Configure VNet Integration no App Service backend para alcançar a VNet da VM.
6. Faça backup periódico do volume PostgreSQL. Um volume Docker não é backup.

## Validação após o Release

- `https://nome-do-app-frontend.azurewebsites.net/` deve abrir o site (com o timer até 10/06/2027 15:30).
- `https://nome-do-app-frontend.azurewebsites.net/api/health/` deve retornar `{"status":"ok","database":"ok"}`.
- `https://nome-do-app-frontend.azurewebsites.net/api/presentes/` deve retornar JSON com a lista de presentes.
- Rode o Playwright contra o Azure: `BASE_URL=https://nome-do-app-frontend.azurewebsites.net npx playwright test` (pasta `e2e`).
- Envie uma confirmação de teste e confira o registro no `/admin/` (pelo endereço do **frontend**, que serve o CSS do admin).
- Teste o QR Code Pix sem divulgar o site. A reserva de presente existente ainda é manual e não comprova pagamento.

## Evidências para a entrega

Docker Hub (imagens com tags `vX.Y.Z`), Service Connection, visão geral do stage do Release, App Service (configuração de container
e variáveis, sem mostrar segredos), aplicação na URL pública e Log stream do backend e do frontend.
