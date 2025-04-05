

def test_status(tmp_client):
    response1 = tmp_client.get("/status")
    assert response1.status_code == 200


def test_text_input(tmp_client):

    text_dump = {
        "text": "This is me testing",
    }

    response1 = tmp_client.post("/display/text", json=text_dump)
    assert response1.status_code == 200
