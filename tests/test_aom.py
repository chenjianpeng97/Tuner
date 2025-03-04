import pytest
from tuner.aoloader import APIObject, load_api_objects
from tuner.utils import file


class TestAOM:
    def test_all_methods_loads_from_folder_send(self):
        # supported method:["GET","POST","PUT","DELETE","PATCH",]
        TESTDATA_DIR = file.join(file.dir, "testdata")
        api_objects = load_api_objects(TESTDATA_DIR)
        # METHOD:GET
        get_api = api_objects["get_api"]
        response = get_api.send()
        assert response.json()["args"] == {"q1": "v1", "q2": "v2"}
        # METHOD:POST
        post_api = api_objects["post_api"]
        response = post_api.send()
        assert response.json()["args"] == {"q1": "v1", "q2": "v2"}
        # METHOD:PUT
        put_api = api_objects["put_api"]
        response = put_api.send()
        assert response.json()["args"] == {"q1": "v1"}
        # METHOD:DELETE
        delete_api = api_objects["delete_api"]
        response = delete_api.send()
        assert response.json()["args"] == {"q1": "v1"}
        # METHOD:PATCH
        patch_api = api_objects["patch_api"]
        response = patch_api.send()
        assert response.json()["args"] == {"q1": "v1"}

    def test_all_methods_modified_request(self):
        # supported method:["GET","POST","PUT","DELETE","PATCH",]
        TESTDATA_DIR = file.join(file.dir, "testdata")
        api_objects = load_api_objects(TESTDATA_DIR)
        # METHOD:GET
        get_api = api_objects["get_api"]
        response = get_api.send()
        assert response.json()["args"] == {"q1": "v1", "q2": "v2"}
        # METHOD:POST
        post_api = api_objects["post_api"]
        response = post_api.send()
        assert response.json()["args"] == {"q1": "v1", "q2": "v2"}
        # METHOD:PUT
        put_api = api_objects["put_api"]
        response = put_api.send()
        assert response.json()["args"] == {"q1": "v1"}
        # METHOD:DELETE
        delete_api = api_objects["delete_api"]
        response = delete_api.send()
        assert response.json()["args"] == {"q1": "v1"}
        # METHOD:PATCH
        patch_api = api_objects["patch_api"]
        response = patch_api.send()
        assert response.json()["args"] == {"q1": "v1"}