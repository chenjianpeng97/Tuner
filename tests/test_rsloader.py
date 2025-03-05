import pytest
from tuner.rsloader import ReqScriptObject, load_api_objects
from tuner.utils import file

@pytest.fixture(scope="class")
def api_objects():
    # 读取测试接口脚本
    TESTDATA_DIR = file.join(file.dir, "testdata")
    api_objects = load_api_objects(TESTDATA_DIR)
    yield api_objects

class TestReqScriptObject:
    def test_all_methods_loads_from_folder_send(self,api_objects):
        # supported method:["GET","POST","PUT","DELETE","PATCH",]
        
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

    def test_all_methods_update_request(self,api_objects):
        # supported method:["GET","POST","PUT","DELETE","PATCH",]
        # METHOD:GET
        get_api = api_objects["get_api"]
        response = get_api.update(params={"q1":"v0","q3":"v3"})
        assert response.json()["args"] == {"q1": "v0", "q2": "v2","q3":"v3"}
        # METHOD:POST
        post_api = api_objects["post_api"]
        response = post_api.update(params={"q1":"v0","q3":"v3"},payload={"ddd":"new data"})
        assert response.json()["args"] == {"q1": "v0","q2": "v2","q3": "v3"}
        assert response.json()['json'] == {'d': 'deserunt', 'dd': 'adipisicing enim deserunt Duis','ddd':'new data'}
        # METHOD:PUT
        put_api = api_objects["put_api"]
        # 若payload为字符串,update时等同于replace
        response = put_api.update(payload = "updated strings")
        assert response.json()["data"] == "updated strings"
        # METHOD:DELETE
        delete_api = api_objects["delete_api"]
        response = delete_api.update(payload = {'b1':'v0','b3':'v3'})
        assert response.json()["form"] == {'b1': 'v0', 'b2': 'v2', 'b3': 'v3'}
        # METHOD:PATCH
        patch_api = api_objects["patch_api"]
        response = patch_api.update(params = {'q1':'v0','q3':'v3'})
        assert response.json()["args"] == {"q1": "v0", "q3": "v3"}
    
    def test_all_methods_replace_request(self,api_objects):
        # METHOD:POST
        post_api = api_objects["post_api"]
        response = post_api.replace(params={"q1":"v0","q3":"v3"},payload={"ddd":"new data"})
        assert response.json()["args"] == {"q1":"v0","q3":"v3"}
        assert response.json()['json'] == {"ddd":"new data"}
        # METHOD:PUT
        put_api = api_objects["put_api"]
        # 若payload为字符串,update时等同于replace
        response = put_api.replace(payload = "updated strings")
        assert response.json()["data"] == "updated strings"
        # METHOD:DELETE
        delete_api = api_objects["delete_api"]
        response = delete_api.replace(payload = {'b1':'v0','b3':'v3'})
        assert response.json()["form"] == {'b1':'v0','b3':'v3'}
        # METHOD:PATCH
        patch_api = api_objects["patch_api"]
        response = patch_api.replace(params = {'q1':'v0','q3':'v3'})
        assert response.json()["args"] == {"q1": "v0", "q3": "v3"}