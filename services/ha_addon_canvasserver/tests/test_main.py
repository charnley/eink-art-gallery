def test_main(tmp_client):
    """Basic test. Does anythin work?"""
    response = tmp_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
