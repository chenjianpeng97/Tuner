import requests
import importlib.util
import ast
import inspect
import os
import json
from typing import Dict


class ReqScriptObject:
    # requert script.py 文件对象
    def __init__(self, module_path):
        spec = importlib.util.spec_from_file_location("api_module", module_path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.url = self.module.url
        self.params = getattr(self.module, "params", {})
        self.headers = getattr(self.module, "headers", {})
        self.payload = getattr(self.module, "payload", None)
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

    def send(self):
        content_type = self.headers.get('Content-Type', '')
        
        if content_type == 'application/json':
            request_data = json.dumps(self.payload) if self.payload else None
        else:
            request_data = self.payload
        
        if self.method == 'POST':
            response = requests.post(
                self.url,
                params=self.params,
                headers=self.headers,
                data=request_data
            )
        elif self.method == 'PUT':
            response = requests.put(
                self.url,
                params=self.params,
                headers=self.headers,
                data=request_data
            )
        elif self.method == 'DELETE':
            response = requests.delete(
                self.url,
                params=self.params,
                headers=self.headers,
                data=request_data
            )
        elif self.method == 'PATCH':
            response = requests.patch(
                self.url,
                params=self.params,
                headers=self.headers,
                data=request_data
            )
        else:
            response = requests.get(
                self.url,
                params=self.params,
                headers=self.headers
            )
        return response

    def update(self, params=None, headers=None, payload=None):
        updated_params = self.params.copy()
        updated_headers = self.headers.copy()
        updated_payload = None
        if params:
            updated_params.update(params)
        if headers:
            updated_headers.update(headers)
        if payload:
            # 当payload为字典时,update self.payload
            if isinstance(payload, dict):
                if self.payload is None:
                    updated_payload = payload
                else:
                    self.payload.update(payload)
                    updated_payload = self.payload
            # 当payload为字符串时,replace self.payload
            elif isinstance(payload, str):
                updated_payload = payload
            else:
                raise ValueError("Invalid payload type. Expected dict or str.")

        content_type = updated_headers.get('Content-Type', '')
        if content_type == 'application/json':
            request_data = json.dumps(updated_payload) if updated_payload else None
        else:
            request_data = updated_payload

        if self.method == 'POST':
            response = requests.post(
                self.url,
                params=updated_params,
                headers=updated_headers,
                data=request_data
            )
        elif self.method == 'PUT':
            response = requests.put(
                self.url,
                params=updated_params,
                headers=updated_headers,
                data=request_data
            )
        elif self.method == 'DELETE':
            response = requests.delete(
                self.url,
                params=updated_params,
                headers=updated_headers,
                data=request_data
            )
        elif self.method == 'PATCH':
            response = requests.patch(
                self.url,
                params=updated_params,
                headers=updated_headers,
                data=request_data
            )
        else:
            response = requests.get(
                self.url,
                params=updated_params,
                headers=updated_headers
            )
        return response

    def replace(self, params=None, headers=None, payload=None):

        replaced_params = params if params else self.params
        replaced_headers = headers if headers else self.headers
        # 修正拼写错误
        replaced_payload = payload if payload else self.payload
        # 判断content-type
        content_type = replaced_headers.get('Content-Type', '')
        if content_type == 'application/json':
            request_data = json.dumps(replaced_payload) if replaced_payload else None
        else:
            request_data = replaced_payload
        if self.method == 'POST':
            response = requests.post(
                self.url,
                params=replaced_params,
                headers=replaced_headers,
                data=request_data
            )
        elif self.method == 'PUT':
            response = requests.put(
                self.url,
                params=replaced_params,
                headers=replaced_headers,
                data=request_data
            )
        elif self.method == 'DELETE':
            response = requests.delete(
                self.url,
                params=replaced_params,
                headers=replaced_headers,
                data=request_data
            )
        elif self.method == 'PATCH':
            response = requests.patch(
                self.url,
                params=replaced_params,
                headers=replaced_headers,
                data=request_data
            )
        else:
            response = requests.get(
                self.url,
                params=replaced_params,
                headers=replaced_headers
            )
        return response

def load_api_objects(api_dir) -> Dict[str, ReqScriptObject]:
    api_objects = {}
    for root, _, files in os.walk(api_dir):
        for file in files:
            if file.endswith(".py"):
                module_name = file[:-3]  # 移除 .py 后缀
                module_path = os.path.join(root, file)
                api_objects[module_name] = ReqScriptObject(module_path)
    return api_objects


if __name__ == "__main__":
    # if there is getcode.py under aom/
    api_objects = load_api_objects("aom/")
    getcode = api_objects["getcode"]  # 通过名称获取 APIObject
    response = getcode.modify(params={"code": "BB"})
    print(response.url)
