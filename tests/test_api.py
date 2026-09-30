import pytest

from app import create_app

VALIDO = {
    "especie": "colibrí",
    "lugar": "Parque Simón Bolívar",
    "fecha": "2026-09-20",
    "observador": "Ana",
}


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    return app.test_client()


def crear(client, **cambios):
    return client.post("/avistamientos", json={**VALIDO, **cambios})


def test_lista_vacia(client):
    r = client.get("/avistamientos")
    assert r.status_code == 200
    assert r.get_json() == []


def test_crear_devuelve_201_y_id(client):
    r = crear(client)
    assert r.status_code == 201
    cuerpo = r.get_json()
    assert cuerpo["id"] == 1
    assert cuerpo["especie"] == "colibrí"


@pytest.mark.parametrize("campo", ["especie", "lugar", "fecha", "observador"])
def test_crear_sin_campo_devuelve_400(client, campo):
    datos = {k: v for k, v in VALIDO.items() if k != campo}
    assert client.post("/avistamientos", json=datos).status_code == 400


def test_crear_fecha_invalida_400(client):
    assert crear(client, fecha="20/09/2026").status_code == 400
    assert crear(client, fecha="2026-13-40").status_code == 400


def test_crear_sin_json_400(client):
    assert client.post("/avistamientos", data="hola").status_code == 400


def test_ver_existente_y_no_existente(client):
    crear(client)
    assert client.get("/avistamientos/1").status_code == 200
    assert client.get("/avistamientos/99").status_code == 404


def test_listar_devuelve_los_creados(client):
    crear(client)
    crear(client, especie="águila")
    r = client.get("/avistamientos")
    assert [a["especie"] for a in r.get_json()] == ["colibrí", "águila"]


def test_actualizar(client):
    crear(client)
    r = client.put("/avistamientos/1", json={**VALIDO, "lugar": "Chicaque"})
    assert r.status_code == 200
    assert r.get_json()["lugar"] == "Chicaque"
    assert client.get("/avistamientos/1").get_json()["lugar"] == "Chicaque"


def test_actualizar_inexistente_404(client):
    assert client.put("/avistamientos/99", json=VALIDO).status_code == 404


def test_actualizar_datos_invalidos_400(client):
    crear(client)
    assert client.put("/avistamientos/1", json={"especie": "x"}).status_code == 400


def test_eliminar(client):
    crear(client)
    assert client.delete("/avistamientos/1").status_code == 204
    assert client.get("/avistamientos/1").status_code == 404
    assert client.delete("/avistamientos/1").status_code == 404


def test_resumen_por_especie(client):
    crear(client)
    crear(client)
    crear(client, especie="águila")
    r = client.get("/avistamientos/resumen")
    assert r.status_code == 200
    assert r.get_json() == {"colibrí": 2, "águila": 1}
