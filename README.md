# API REST de Avistamientos de Aves

Trabajo en clase, Sesión 17 – Ingeniería de Software 2 (ISW-2).
API REST para registrar avistamientos de aves. Hecha con **Python 3 + Flask** y **SQLite** (módulo `sqlite3` incluido en Python; los datos se guardan en el archivo `avistamientos.db`, que se crea solo).

## Uso de IA

Se usó **Claude** (Anthropic), modelo **Sonnet 5.5**, para generar la versión inicial del código. Fue revisado y probado por el autor.

<!-- TODO: escribe aquí tu nombre y cualquier cosa que hayas cambiado o entendido por tu cuenta -->

## Requisitos

- Python 3.10 o superior
- Git (para clonar)

## Instalación y ejecución

```bash
git clone <URL-DEL-REPOSITORIO>
cd api-avistamientos

# 1. Crear y activar el entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\Activate.ps1     # Windows (PowerShell)
# .venv\Scripts\activate.bat     # Windows (CMD)

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar la API
python app.py
```

La API queda disponible en **http://127.0.0.1:5000**.
(Opcional: la variable de entorno `DB_PATH` cambia la ruta del archivo de base de datos.)

## Modelo

```json
{
  "id": 1,
  "especie": "colibrí",
  "lugar": "Jardín Botánico",
  "fecha": "2026-09-20",
  "observador": "Ana"
}
```

`id` lo asigna el sistema. `especie`, `lugar`, `fecha` (AAAA-MM-DD, fecha válida) y `observador` son obligatorios y no pueden ir vacíos.

## Endpoints

| Operación | Petición | Respuesta |
|---|---|---|
| Listar | `GET /avistamientos` | 200 |
| Ver uno | `GET /avistamientos/{id}` | 200 / 404 |
| Registrar | `POST /avistamientos` | 201 / 400 |
| Actualizar | `PUT /avistamientos/{id}` | 200 / 400 / 404 |
| Eliminar | `DELETE /avistamientos/{id}` | 204 / 404 |
| Resumen (bonus) | `GET /avistamientos/resumen` | 200 |

Los errores se devuelven en JSON: `{"error": "mensaje"}`.
`PUT` reemplaza el avistamiento completo, así que hay que enviar los cuatro campos.

### Ejemplos con curl

> En Windows PowerShell usa `curl.exe` en vez de `curl`, y comillas dobles escapadas en el JSON, o usa CMD / Git Bash.

**Listar todos** → 200
```bash
curl http://127.0.0.1:5000/avistamientos
```

**Ver uno** → 200 (404 si no existe)
```bash
curl http://127.0.0.1:5000/avistamientos/1
```

**Registrar** → 201 (400 si faltan datos)
```bash
curl -X POST http://127.0.0.1:5000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie":"colibrí","lugar":"Jardín Botánico","fecha":"2026-09-20","observador":"Ana"}'
```

**Actualizar** → 200 (404 si no existe, 400 si datos inválidos)
```bash
curl -X PUT http://127.0.0.1:5000/avistamientos/1 \
  -H "Content-Type: application/json" \
  -d '{"especie":"colibrí","lugar":"Parque Simón Bolívar","fecha":"2026-09-21","observador":"Ana"}'
```

**Eliminar** → 204 sin cuerpo (404 si no existe)
```bash
curl -i -X DELETE http://127.0.0.1:5000/avistamientos/1
```

**Resumen por especie (bonus)** → 200
```bash
curl http://127.0.0.1:5000/avistamientos/resumen
```
Respuesta de ejemplo: `{"colibrí": 2, "águila": 1}`

## Pruebas (bonus)

```bash
python -m pytest
```

Hay 15 pruebas de integración que cubren los cinco endpoints, el resumen, los códigos 200/201/400/404/204 y la validación de datos. Usan una base de datos temporal, no tocan `avistamientos.db`.

## Estructura

```
app.py              # API, base de datos y endpoints
tests/test_api.py   # pruebas de integración
requirements.txt    # dependencias
```
