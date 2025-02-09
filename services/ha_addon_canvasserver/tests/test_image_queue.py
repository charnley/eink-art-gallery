from canvasserver.models.content import Prompt
from canvasserver.routes.prompts import prefix as prompt_prefix


def test_main(tmp_client):

    response = tmp_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

    return


def test_image_upload(tmp_client):

    response0 = tmp_client.get(prompt_prefix)
    print(response0.json())

    # Create prompt
    prompt = Prompt(prompt="Test prompt", model="")

    response1 = tmp_client.post(prompt_prefix, json=prompt.model_dump())
    print(response1.json())
    assert response1.status_code == 200
    assert response1.json()

    prompt_id = response1.json()["id"]
    assert prompt_id is not None

    response2 = tmp_client.get(prompt_prefix)
    assert response2.status_code == 200

    assert response2.json()["count"] == 1

    return
