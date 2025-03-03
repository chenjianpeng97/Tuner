import sys
import os

#!/usr/bin/python
# -*- coding: UTF-8 -*-


class FidToPy:
    def __init__(self, str_name, sa_name):
        self.str_filename = str_name
        self.save_name = sa_name
        self.text = ""
        self.url_list = []
        self.headers = {}
        self.cookies = {}
        self.data = {}

    def get_url(self):
        infos = self.text.split("\n")[0]
        self.url_list = [infos.split(" ")[0], infos.split(" ")[1]]

    def get_headers(self):
        infos = self.text.split("\n")[1:]
        info = ""
        for i in infos:
            if "Cookie: " in i:
                break
            info += i + "\n"
        headers = info.split("\n")
        while "" in headers:
            headers.remove("")
        for i in headers:
            if ": " not in i:
                break
            self.headers[i.split(": ")[0]] = i.split(": ")[1]

    def get_cookies(self):
        infos = self.text.split("\n")[1:]
        cookies_flag = 0
        for i in infos:
            if "Cookie: " in i:
                self.cookies = i.replace("Cookie: ", "")
                # print(self.cookies)
                cookies_flag = 1
                break
        if cookies_flag == 1:
            self.cookies = {
                i.split("=")[0]: i.split("=")[1] for i in self.cookies.split("; ")
            }

    def get_data(self):
        try:
            infos = self.text.split("\n")
            for i in range(2, len(infos)):
                if infos[i - 1] == "" and "HTTP" in infos[i + 1]:
                    self.data = infos[i]
                    break
            # 处理self.data字符串，将其中的'null' - > None
            self.data = self.data.replace(":null", ":None")
            self.data = {
                i.split("=")[0]: (
                    i.split("=")[1] if i.split("=")[1] != "null" else None
                )
                for i in self.data.split("&")
            }

        except:
            pass

    def get_req(self):
        info_beg = "#!/usr/bin/python\n# -*- coding: UTF-8 -*-\nimport requests\nimport json\n\n"
        info_url = "url = '{}'\n".format(self.url_list[1])
        info_headers = "headers = {}\n".format(self.headers)
        # info_cookies = "cookies = {}\n".format(self.cookies)
        info_cookies = ""
        info_data = "payload = json.dumps({})\n\n".format(self.data)
        if "GET" in self.url_list[0]:
            info_req = "respones = requests.get(url, headers=headers)\n"
        else:
            info_req = "respones = requests.post(url, headers=headers, data=payload)\n"
        info_end = "print(len(respones.text))\nprint(respones.text)\n"
        text = (
            info_beg
            + info_url
            + info_headers
            + info_cookies
            + info_data
            + info_req
            + info_end
        )
        with open(self.save_name, "w+", encoding="utf8") as p:
            p.write(text)
        print("转化成功！！")
        print(self.save_name, "文件保存!")

    def read_infos(self):
        with open(self.str_filename, "r+", encoding="utf-8") as p:
            old_line = ""
            for line in p:
                if old_line == b"\n" and line.encode() == b"\n":
                    break
                old_line = line.encode()
                self.text += old_line.decode()
        # print("self.text:", self.text)

    def start(self):
        self.read_infos()
        self.get_url()
        self.get_headers()
        self.get_cookies()
        self.get_data()
        # print("self.url_list:", self.url_list)
        # print("self.headers:", self.headers)
        # print("self.cookies:", self.cookies)
        # print("self.data:", self.data)
        self.get_req()


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    elif len(sys.argv) == 1:
        txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
        print(txt_files)
        if not txt_files:
            print("Error: No .txt files found in the current directory.")
            sys.exit(1)
        for filename in txt_files:
            save_name = filename.replace("txt", "py")
            f = FidToPy(filename, save_name)
            f.start()
        sys.exit(0)
    else:
        print("Error: No input filename provided.")
        sys.exit(1)
    save_name = filename.replace("txt", "py")
    f = FidToPy(filename, save_name)
    f.start()


if __name__ == "__main__":
    main()
