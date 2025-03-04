import requests
import importlib.util
import ast
import inspect
import os
import json
from typing import Dict


class APIObject:
    def __init__(self, module_path):
        spec = importlib.util.spec_from_file_location("api_module", module_path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.url = self.module.url
        self.params = getattr(self.module, "params", {})
        self.headers = getattr(self.module, "headers", {})
        self.data = getattr(self.module, "data", None)
        self.json_data = json.dumps(getattr(self.module, "payload", None))
        self.method = self._detect_method(module_path).upper()  # 自动检测请求方法

    def _detect_method(self, module_path):
        """
        使用 AST 自动检测 requests 调用方法，默认返回 "GET"
        """
        try:
            with open(module_path, "r") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "response":
                            if isinstance(node.value, ast.Call) and isinstance(
                                node.value.func, ast.Attribute
                            ):
                                if (
                                    isinstance(node.value.func.value, ast.Name)
                                    and node.value.func.value.id == "requests"
                                ):
                                    method = node.value.func.attr.upper()
                                    if method in [
                                        "GET",
                                        "POST",
                                        "PUT",
                                        "DELETE",
                                        "PATCH",
                                    ]:
                                        return method
        except Exception as e:
            print(f"Error detecting method: {e}")
        return "GET"  # 默认 GET

    def modify(self, params=None, headers=None, data=None, json=None):
        updated_params = self.params.copy() if self.params else {}
        updated_headers = self.headers.copy() if self.headers else {}
        updated_data = self.data.copy() if self.data else None
        updated_json = self.json_data.copy() if self.json_data else None

        if params:
            updated_params.update(params)
        if headers:
            updated_headers.update(headers)
        if data:
            updated_data = data
        if json:
            updated_json = json

        if self.method == "POST":
            response = requests.post(
                self.url,
                data=updated_data,
                json=updated_json,
                headers=updated_headers,
                params=updated_params,
            )
        elif self.method == "PUT":
            response = requests.put(
                self.url,
                data=updated_data,
                json=updated_json,
                headers=updated_headers,
                params=updated_params,
            )
        elif self.method == "DELETE":
            response = requests.delete(
                self.url,
                headers=updated_headers,
                params=updated_params,
                data=updated_data,
                json=updated_json,
            )
        elif self.method == "PATCH":
            response = requests.patch(
                self.url,
                headers=updated_headers,
                params=updated_params,
                data=updated_data,
                json=updated_json,
            )
        else:
            response = requests.get(
                self.url, params=updated_params, headers=updated_headers
            )

        return response

    def replace(self, params=None, headers=None, data=None, json=None):

        if params:
            self.params = params
        if headers:
            self.headers = headers
        if data:
            self.data = data
        if json:
            self.json_data = json
        response = requests.get(
            self.url, params=updated_params, headers=updated_headers
        )
        return response

    def send(self):
        if self.method == "POST":
            response = requests.post(
                self.url,
                data=self.data,
                json=self.json_data,
                headers=self.headers,
                params=self.params,
            )
        elif self.method == "PUT":
            response = requests.put(
                self.url,
                data=self.data,
                json=self.json_data,
                headers=self.headers,
                params=self.params,
            )
        elif self.method == "DELETE":
            response = requests.delete(
                self.url,
                headers=self.headers,
                params=self.params,
                data=self.data,
                json=self.json_data,
            )
        elif self.method == "PATCH":
            response = requests.patch(
                self.url,
                headers=self.headers,
                params=self.params,
                data=self.data,
                json=self.json_data,
            )
        else:
            response = requests.get(self.url, params=self.params, headers=self.headers)
        return response


def load_api_objects(api_dir) -> Dict[str, APIObject]:
    api_objects = {}
    for root, _, files in os.walk(api_dir):
        for file in files:
            if file.endswith(".py"):
                module_name = file[:-3]  # 移除 .py 后缀
                module_path = os.path.join(root, file)
                api_objects[module_name] = APIObject(module_path)
    return api_objects


if __name__ == "__main__":
    # if there is getcode.py under aom/
    api_objects = load_api_objects("aom/")
    getcode = api_objects["getcode"]  # 通过名称获取 APIObject
    response = getcode.modify(params={"code": "BB"})
    print(response.url)
