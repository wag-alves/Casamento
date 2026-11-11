# Save the Date — Larissa & Wagner 💍

Site em Django para o casamento de Larissa & Wagner:
- Página inicial com vídeo em loop (preto e branco) e confirmação de presença (RSVP)
- Lista de presentes com pagamento via **Pix (QR Code gerado automaticamente)**
- E-mail automático para **wagfalcon@gmail.com** a cada confirmação de presença ou presente escolhido
- Totalmente responsivo (preenche a tela em qualquer celular, sem espaços vazios)

## 1. Instalar

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar o `.env`

```bash
cp .env.example .env
```

Abra o `.env` e preencha:

- **E-mail** (para receber as notificações):
  - `EMAIL_HOST_USER`: conta Gmail que vai enviar o e-mail
  - `EMAIL_HOST_PASSWORD`: uma **senha de app** do Gmail (Conta Google →
    Segurança → Verificação em duas etapas → Senhas de app)
  - `NOTIFICATION_EMAIL`: já vem com `wagfalcon@gmail.com`
- **Pix** (para o QR Code da lista de presentes):
  - `PIX_KEY`: a chave Pix de vocês (CPF, e-mail, telefone ou chave aleatória)
  - `PIX_NOME`: nome do titular da chave, sem acento, até 25 letras (ex: `LARISSA E WAGNER`)
  - `PIX_CIDADE`: cidade do titular da chave, sem acento, até 15 letras (ex: `NATAL`)

⚠️ **Muito importante:** depois de configurar o Pix, teste escaneando o QR Code
com o app do seu próprio banco antes de divulgar o site, para garantir que
o valor e a chave aparecem certinhos.

Enquanto `DJANGO_DEBUG=True`, os e-mails só aparecem no terminal (não são
enviados de verdade) — é só para testar. Para ativar o envio de verdade,
mude para `DJANGO_DEBUG=False` no `.env`.

## 3. Rodar o site localmente

```bash
python manage.py migrate
python manage.py createsuperuser   # opcional, para acessar o /admin/
python manage.py runserver
```

Acesse:
- **http://127.0.0.1:8000/** → site principal (Save the Date + RSVP)
- **http://127.0.0.1:8000/presentes/** → lista de presentes
- **http://127.0.0.1:8000/admin/** → ver confirmações e presentes escolhidos,
  e também para **editar a lista de presentes** (adicionar, remover, mudar
  valores e nomes)

A lista de presentes já vem com 10 itens de exemplo (jogo de panelas,
liquidificador, cota lua de mel, etc). Edite, remova ou adicione itens
livremente pelo `/admin/`, na seção "Lista de presentes".

## 4. Estrutura do projeto

```
casamento_larissa_wagner/
├── manage.py
├── requirements.txt
├── .env.example
├── wedding/            -> configurações do projeto Django
└── rsvp/               -> app principal
    ├── models.py       -> Confirmacao (RSVP) e Presente (lista de presentes)
    ├── forms.py        -> formulários do site
    ├── views.py        -> lógica das páginas + envio de e-mail
    ├── pix.py           -> gerador do QR Code / código Pix "Copia e Cola"
    ├── admin.py         -> painel para gerenciar tudo (/admin/)
    ├── templates/        -> HTML do site (tema "jornal Extra!")
    └── static/
        ├── css/style.css -> visual responsivo (mobile-first)
        └── video/        -> vídeo do casal em loop, preto e branco
```

## 5. Executar com Docker Compose

O ambiente Docker usa três containers independentes: Nginx (`frontend`), Django/Gunicorn (`backend`) e PostgreSQL (`database`).
O banco usa o volume nomeado `postgres_data`. Só o Nginx publica porta no host; o banco fica numa rede `internal`
(`rede-banco`) que o Nginx nem enxerga. Para rodar direto com `python manage.py runserver`, o `.env.example` mantém SQLite
como padrão; o Compose sobrescreve isso e usa PostgreSQL.

```bash
cp .env.example .env
# Edite .env: defina POSTGRES_PASSWORD, DJANGO_SECRET_KEY e os dados de e-mail/Pix.
docker compose up --build -d
```

Acesse `http://localhost:8080/` (porta configurável em `HOST_PORT`). Logs: `docker compose logs -f backend frontend database`.
Parar sem apagar o banco: `docker compose down`. **Não use `docker compose down -v`** se quiser preservar o volume PostgreSQL.

### Variáveis de ambiente

Toda configuração que muda entre ambientes está em variáveis (veja `.env.example`, comentado):

| Grupo | Variáveis |
|---|---|
| Django | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (padrão **False**), `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_TIME_ZONE`, `DJANGO_LANGUAGE_CODE`, `DJANGO_LOG_LEVEL`, `DJANGO_SECURE_COOKIES` |
| E-mail / Pix | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `NOTIFICATION_EMAIL`, `PIX_KEY`, `PIX_NOME`, `PIX_CIDADE` |
| Banco | `DATABASE_ENGINE`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `DATABASE_CONN_MAX_AGE`, `DB_WAIT_TIMEOUT`, `POSTGRES_IMAGE`, `POSTGRES_BIND_ADDRESS` (VM) |
| Container do backend | `RUN_MIGRATIONS`, `RUN_COLLECTSTATIC`, `CREATE_SUPERUSER` + `DJANGO_SUPERUSER_*`, `GUNICORN_BIND`, `GUNICORN_WORKERS`, `GUNICORN_TIMEOUT`, `GUNICORN_LOG_LEVEL`, `HEALTHCHECK_HOST` |
| Nginx (frontend) | `BACKEND_SCHEME`, `BACKEND_HOST`, `BACKEND_PORT` |
| Imagens / Compose | `DOCKERHUB_USERNAME` (`wagnernoronha`), `IMAGE_TAG` (`v1.0.0`), `HOST_PORT` |

No pipeline, o usuário do Docker Hub, os nomes das imagens e a versão estão na seção `variables:` do `azure-pipelines.yml`.

### Testes ponta a ponta (Playwright)

Com a stack no ar (`docker compose up --build -d`):

```bash
cd e2e
npm ci
npx playwright install chromium
npx playwright test                                              # contra http://localhost:8080
BASE_URL=https://SEU-FRONTEND.azurewebsites.net npx playwright test   # contra o Azure
```

Cobre a cadeia navegador → Nginx → Django → PostgreSQL: `/api/health/`, arquivos estáticos pelo Nginx, lista de presentes
(video game, liquidificador, casinha do cachorro), API de confirmações, timer da home e o formulário de presença.

### Endpoints REST

- `GET /api/health/`: saúde da aplicação e conectividade com o banco.
- `GET /api/presentes/`: lista de presentes em JSON.
- `POST /api/confirmacoes/`: cria uma confirmação em JSON (público).
- `GET /api/confirmacoes/`, `GET|DELETE /api/confirmacoes/<id>/`: **somente administradores** (sessão do `/admin/`), porque trazem nome, e-mail e telefone dos convidados.

```bash
curl -X POST http://localhost:8080/api/confirmacoes/ \
  -H 'Content-Type: application/json' \
  -d '{"nome":"Convidado de teste","email":"teste@example.com","presenca":"sim","acompanhantes":"Maria"}'
```

## 6. Arquitetura de produção no Azure

- **Frontend:** imagem Nginx em um Azure App Service Linux. O Nginx serve os arquivos estáticos e encaminha páginas e chamadas de API ao backend.
- **Backend:** imagem Django + Django REST Framework + Gunicorn em outro Azure App Service Linux.
- **Banco:** imagem oficial PostgreSQL 16 em uma VM Linux, com volume persistente e porta 5432 acessível somente pela rede privada ao backend.
- **Registro:** Docker Hub (`wagnernoronha/casamento-backend` e `wagnernoronha/casamento-frontend`), com tags semânticas `vX.Y.Z` (sem `latest`).
- **CI:** Azure Pipeline YAML (`azure-pipelines.yml`) valida o Django, sobe a stack e roda o Playwright, e então constrói e publica as imagens.
- **CD:** Classic Release Pipeline configurado pela interface do Azure DevOps.

A configuração passo a passo está em [`docs/CLASSIC_RELEASE.md`](docs/CLASSIC_RELEASE.md). A configuração do container PostgreSQL da VM está em `database/compose.yaml`.

### Atenção sobre dados existentes

O arquivo `db.sqlite3` do ZIP original foi preservado como referência, mas não é montado no container. O PostgreSQL começa vazio e as migrações Django criam as tabelas e os presentes definidos nas migrations. Se o SQLite original já tiver confirmações reais ou presentes editados, exporte esses dados e importe-os para PostgreSQL antes de colocar a versão nova em produção. Não apague o SQLite até validar a migração.

### Limites desta primeira adaptação

As páginas HTML continuam sendo renderizadas pelos templates Django para preservar o site atual. O Nginx serve os arquivos estáticos e atua como proxy reverso; a API REST já existe para permitir a evolução do frontend desacoplado sem reescrever tudo de uma vez.
