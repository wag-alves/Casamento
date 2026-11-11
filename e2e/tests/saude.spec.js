const { test, expect } = require('@playwright/test');

// Cadeia testada: navegador -> Nginx (frontend) -> Django/Gunicorn (backend) -> PostgreSQL

test('healthcheck ponta a ponta: Nginx -> backend -> banco', async ({ request }) => {
  const resp = await request.get('/api/health/');
  expect(resp.status()).toBe(200);
  expect(await resp.json()).toEqual({ status: 'ok', database: 'ok' });
});

test('Nginx entrega os arquivos estáticos sem passar pelo Django', async ({ request }) => {
  const css = await request.get('/static/rsvp/css/style.css');
  expect(css.status()).toBe(200);
  expect(css.headers()['content-type']).toContain('text/css');
});

test('lista de presentes na API traz os itens pedidos', async ({ request }) => {
  const resp = await request.get('/api/presentes/');
  expect(resp.status()).toBe(200);
  const nomes = (await resp.json()).map((p) => p.nome);
  expect(nomes.length).toBeGreaterThanOrEqual(10);
  for (const esperado of ['Video game', 'Liquidificador', 'Casinha do cachorro']) {
    expect(nomes).toContain(esperado);
  }
});

test('API de confirmações: POST público; GET e DELETE só para administradores', async ({ request }) => {
  const criada = await request.post('/api/confirmacoes/', {
    data: { nome: `Teste e2e ${Date.now()}`, presenca: 'sim' },
  });
  expect(criada.status()).toBe(201);
  const { id } = await criada.json();

  // Dados de convidados não podem ser lidos nem apagados sem login
  expect([401, 403]).toContain((await request.get('/api/confirmacoes/')).status());
  expect([401, 403]).toContain((await request.delete(`/api/confirmacoes/${id}/`)).status());

  // Validação do backend
  const invalida = await request.post('/api/confirmacoes/', { data: { presenca: 'sim' } });
  expect(invalida.status()).toBe(400);
});

test('páginas renderizadas pelo Django aparecem via Nginx', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('#timer')).toHaveAttribute('data-alvo', '2027-06-10T15:30:00-03:00');
  await expect(page.locator('#t-seg')).toHaveText(/^\d+$/); // o timer está contando

  await page.goto('/presentes/');
  await expect(page.locator('.presente-card')).not.toHaveCount(0);
  await expect(page.locator('.presente-card', { hasText: 'Casinha do cachorro' })).toBeVisible();
});

test('formulário de confirmação de presença (CSRF + banco) pelo navegador', async ({ page }) => {
  await page.goto('/');
  await page.locator('#id_nome').fill(`Convidado e2e ${Date.now()}`);
  await page.getByRole('button', { name: 'Confirmar presença' }).click();
  await expect(page).toHaveURL(/\/obrigado\/$/);
});
