from os import path, getcwd
import re
import yaml

from bs4 import BeautifulSoup
import requests


class PageReader:
    # def __init__(self, url):
    #     self.url = url
    #     self.base_url = None

    def page_request(self, url: str):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                new_content = self.edit_content(response.text)

                FileCreator().save_file(new_content, url)
            else:
                self.return_error(f'Was received wrong answer. Status code: {response.status_code}')
        except (requests.ConnectionError, requests.Timeout) as err:
            self.return_error(f'Some problem with connect - {err}')


    def edit_content(self, response) -> str:
        soup = BeautifulSoup(response, 'lxml').article
        res = soup.find_all(['h1', 'p'])

        return self.format_text(res)


    def format_text(self, data: list) -> str:
        result = ''
        for i in data:
            content = i.contents
            if content:
                result += ' \\n\\n '
                for c in range(len(content)):
                    if not isinstance(content[c], str):
                        text, href = content[c].text, content[c].get('href')
                        new_string = ''
                        if text:
                            new_string += f'{text}'
                        if href:
                            new_string += f' [{href}]'
                        content[c] = new_string
                    result += content[c]
        return result


    @staticmethod
    def return_error(message: str):
        print(message)


class FileCreator:
    def save_file(self, content: str, file_name: str) -> None:
        cur_dir = getcwd()
        with open(r'simple_name.txt', 'w', encoding='utf-8') as f:
            data = self.redact_content(content)
            f.write(str(data))


    def redact_content(self, content: str) -> str:
        result = ''
        string = ''
        spl = content.split()
        for i in range(len(spl)):
            if spl[i] == '\\n\\n':
                if i > 1:
                    result += f'{string}\n\n'
                    string = ''
                else:
                    continue
            elif len(string) + len(spl[i]) <= 80:
                string += f'{spl[i]} '
            else:
                result += f'{string}'
                string = f'\n{spl[i]} '
        result += string
        return result


def read_yaml():
    pass


if __name__ == '__main__':
    url = r'https://lenta.ru/articles/2020/06/20/babariko/'
    # url = r'https://www.fontanka.ru/2020/06/22/69328792/'
    # url = r'https://www.severcart.ru/blog/all/python_getattr/'
    res = PageReader()
    res.page_request(url)

