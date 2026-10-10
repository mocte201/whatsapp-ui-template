# Referencia canónica — Web Push PWA (patrón Hermes)

Basado en la implementación productiva de **Compra Acebal**. Usar como canon de forma, no como copia literal de textos de producto ni de rutas de negocio.

## Idea rectora

Separar **encolar** de **enviar**:

1. Algo de dominio (trigger SQL o código servidor) inserta filas en `notification_events` con `delivery_status = 'queued'`.
2. Un worker HTTP en la app (Route Handler) lee la cola con **service role**, resuelve `push_subscriptions` activas del destinatario y envía con la librería `web-push` + VAPID.
3. El **service worker** solo pinta la notificación y navega al `url` del payload.

Eso evita HTTP saliente desde Postgres (plan free / límites) y mantiene el secreto VAPID privado solo en el servidor de despacho.

## Diagrama E2E

```mermaid
sequenceDiagram
  participant User
  participant UI
  participant SW as ServiceWorker
  participant API as Next API
  participant DB as Supabase
  participant Cron as Cron/GitHub

  User->>UI: Activar notificaciones
  UI->>User: Notification.requestPermission
  UI->>SW: register + ready (timeout)
  UI->>API: GET vapid-public-key
  UI->>SW: pushManager.subscribe
  UI->>API: POST subscriptions (session)
  API->>DB: upsert push_subscriptions

  Note over DB: Evento de dominio
  DB->>DB: INSERT notification_events queued

  Cron->>API: POST dispatch + x-cron-secret
  API->>DB: SELECT queued + active subs
  API->>SW: web-push sendNotification
  API->>DB: sent|failed|expired; deactivate 410
  SW->>User: showNotification
  User->>SW: notificationclick
  SW->>User: focus/openWindow(url)
```

## Inventario de piezas (ejemplo de proyecto de referencia)

| Pieza | Responsabilidad típica |
| --- | --- |
| `public/sw.js` | Cache opcional + `push` + `notificationclick` |
| Register SW en layout | Registro temprano scope `/` |
| Card/UI de suscripción | Permiso, timeout SW, VAPID, POST/DELETE |
| `GET /api/push/vapid-public-key` | Solo clave pública |
| `POST|DELETE /api/push/subscriptions` | Auth usuario; upsert por `endpoint`; baja lógica |
| `POST /api/push/dispatch` | Auth cron secret; llama dispatcher |
| `lib/push/env.ts` | Lee `VAPID_*` y `PUSH_CRON_SECRET` |
| `lib/push/web-push.ts` | `setVapidDetails` una vez |
| `lib/push/dispatch.ts` | Cola → envío → estados + 410 |
| Migración tablas + RLS | Ver schema abajo |
| Trigger `queue_*` | Solo INSERT queued |
| Cron (GH Actions o Vercel) | POST periódico |
| `docs/api/web-push-spec.md` | Contrato de API y payloads |

## Schema mínimo

### `push_subscriptions`

- `id` uuid PK
- `user_id` → profiles/users
- `endpoint` text **unique**
- `p256dh`, `auth` text
- `user_agent`, `device_label` opcionales
- `last_seen_at`, `is_active`, `created_at`

Baja = `is_active = false` (no borrar físico por defecto). Upsert por `endpoint` (un endpoint puede reasignarse al usuario actual).

### `notification_events`

- `id` uuid PK
- `type` text (check de dominio del producto)
- `request_id` / entidad opcional
- `recipient_user_id`
- `payload` jsonb
- `delivery_status`: `queued` | `sent` | `failed` | `expired`
- `sent_at`, `error_message`, `created_at`

Dedup opcional (unique parcial) para tipos “una vez por entidad/usuario/tipo”.

### RLS (patrón)

- Subscriptions: CRUD propias (`user_id = auth.uid()`); admin opcional.
- Events: SELECT propias; escritura de insert vía trigger SECURITY DEFINER o service role; admin write opcional.
- Dispatch: **service role** en servidor (no JWT del usuario).

## Payload hacia el SW

JSON mínimo:

```json
{
  "type": "domain_event_code",
  "title": "Título visible",
  "body": "Cuerpo corto",
  "url": "/ruta/deep-link"
}
```

El SW no interpreta negocio: `title`/`body`/`data.url` + iconos del producto.

## Variables de entorno (nombres)

| Nombre | Dónde |
| --- | --- |
| `VAPID_PUBLIC_KEY` | Runtime que sirve GET pública + client subscribe |
| `VAPID_PRIVATE_KEY` | Solo runtime de dispatch |
| `VAPID_SUBJECT` | `mailto:...` de contacto |
| `PUSH_CRON_SECRET` | Header `x-cron-secret` en dispatch + secret del cron |

Generar: `npx web-push generate-vapid-keys` (o API equivalente).

## Orden de implementación recomendado

1. Env + spec doc  
2. Tablas + RLS + grants service_role  
3. Encolar (trigger o helper)  
4. Lib web-push + dispatch  
5. Rutas API  
6. SW push/click  
7. UI subscribe (+ register SW global)  
8. Cron  
9. Prueba E2E real en dispositivo  

## Qué es genérico vs de dominio

| Genérico (skill) | De dominio (proyecto) |
| --- | --- |
| VAPID, SW push/click, upsert endpoint | Textos de `type` y copy de title/body |
| Cola `queued` → dispatch | Qué filas de negocio generan eventos |
| Soft-delete 410 | Rutas deep link (`/requests/...`) |
| Cron + secret | Frecuencia y host de producción |
| UX activar/desactivar | Dónde se muestra la card |

## Reintentos

- Columna `notification_events.attempt_count` (int, default 0).
- Constante de app `PUSH_MAX_DISPATCH_ATTEMPTS = 2` (incluye el primer intento).
- Fallo transitorio o sin suscripciones: `attempt_count++`, si `< max` permanece `queued`; si no → `failed`.
- Todas las suscripciones gone (404/410): `expired` (sin reintento).
- Al menos un device OK: `sent`.
- Respuesta de dispatch debe reportar `requeued` cuando deje eventos en cola.

## Cron portable (GitHub Actions)

No hardcodear el host de producción como única opción:

- Repo **variable** `PUSH_DISPATCH_URL` = origen (`https://mi-app.vercel.app`) o URL completa de dispatch.
- Repo **secret** `PUSH_CRON_SECRET` = header `x-cron-secret`.
- Si falta la variable, fallar o loguear WARNING + fallback solo en el proyecto legacy que lo documente.

## Criterios de done (proyecto nuevo)

- [ ] PWA/instalable o al menos SW en origen HTTPS  
- [ ] Activar guarda suscripción activa  
- [ ] Evento de dominio encola (no envía desde SQL)  
- [ ] Dispatch con secret produce `sent` / `requeued` / error trazable  
- [ ] `attempt_count` respeta el máximo documentado  
- [ ] Click abre URL real de la app (no rutas inventadas en la spec)  
- [ ] Desactivar + 410 limpian suscripciones  
- [ ] Cron usa `PUSH_DISPATCH_URL` (variable), no un host fijo de otro producto  
- [ ] Spec documentada; secretos solo por nombre en repo  

## Anti-patrones

- Guardar VAPID private en cliente  
- Encolar y enviar en el mismo request de usuario sin cola (dificulta reintentos y cron)  
- Marcar `failed` al primer 5xx sin `attempt_count`  
- URL de dispatch hardcodeada al dominio de otro proyecto  
- Spec con deep links que no existen en el router  
- Borrar hard subscriptions en cada error transitorio  
- Dependencia exclusiva de Vercel Cron en Hobby (frecuencia sub-diaria)  
- Omitir timeout de `serviceWorker.ready` en iOS  
- Copiar nombres de producto (“Compra Acebal”) a otras apps  
