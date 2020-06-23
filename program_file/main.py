from pathlib import Path
from sys import argv
from urllib.parse import urlparse
import yaml

from bs4 import BeautifulSoup
import requests


class PageReader:
    def __init__(self, url):
        self.url = url
        self.parse_url = urlparse(url)

    def page_request(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                # response.encoding = 'utf-8'
                return self.edit_content(response.text), self.parse_url.path
            else:
                self.return_error(f'Was received wrong answer. Status code: {response.status_code}')
                return None, None
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.MissingSchema) as err:
            self.return_error(f'Some problem with connect - {err}')
            return None, None


    def edit_content(self, response) -> str:
        try:
            soup = BeautifulSoup(response, 'lxml').article
            result = soup.find_all(['h1', 'p', 'code', 'li', 'span'])
            return self.format_text(result)
        except AttributeError:
            print('Не удалось прочитать информацию с сайта')

    def format_text(self, data: list) -> str:
        result = ''
        for i in data:
            tag_name = i.name
            # Отфильтруем лишние ссылки т.к. это похоже а рекламу
            if (tag_name == 'li' and i.a or i.link) or (tag_name == 'span' and i.a or i.link):
                continue
            print(i)
            # Извлекаем контент из тегов
            content = i.contents
            if not content and tag_name == 'p' and i.p.span:
                content = i.p.span.contents

            if content:
                result += '\n'
                for c in range(len(content)):
                    # Проверяем, строка ли в контенте. Если нет придётся дообработать
                    if not isinstance(content[c], str):
                        new_string = self.handel_tag(content[c])
                        content[c] = new_string
                    result += content[c]
        return result


    def handel_tag(self, tag):
        """
        Метод принимает тег <a>  и обрабатывает его. Вытаскивает тест и делает ссылку абсолютной.
        """
        new_string = ''
        try:
            text, href = tag.text, tag.get('href')
            if text:
                new_string += f'{text}'
            if href:
                if 'http' in href:
                    new_string += f' [{href}]'
                else:
                    new_string += f" [{self.parse_url.scheme}://{self.parse_url.netloc}{href}]"
        except:
            new_string = ''
        finally:
            return new_string


    @staticmethod
    def return_error(message: str):
        print(message)


class FileCreator:
    def save_file(self, content: str, path: str) -> None:
        try:
            out_path = Path.cwd() / path[1:]
            Path(out_path).mkdir(parents=True, exist_ok=True)
            file_path = out_path / 'index.txt'
            with open(str(file_path), 'w', encoding='utf-8') as f:
                data = self.redact_content(content)
                f.write(str(data))
            print(f'\nФайл был успешно создан:\n{file_path} \n')
        except (FileNotFoundError, FileExistsError) as err:
            print(f'Возникла ошибка при записи файла - {err}')

    def redact_content(self, content: str) -> str:
        result = ''
        string = ''
        indents = content.splitlines()

        for i in indents:
            if i:
                words = i.split()
                for word in words:
                    if len(string) + len(word) <= 80:
                        string += f'{word} '
                    else:
                        result += f'{string}'
                        string = f'\n{word} '
                result += f'{string}\n\n'
                string = ''
        return result


def read_yaml():
    pass


if __name__ == '__main__':
    try:
        script, url = argv
    except ValueError:
        # url = input('Вы не передали в качестве параметра url, пожалуста введи его в строку ниже: \nПример: '
        #             'https://lenta.ru/articles/2020/06/20/babariko/ \n')
        # url = r'https://lenta.ru/articles/2020/06/20/babariko/'
        # url = r'https://www.fontanka.ru/2020/06/22/69328792/'
        # url = r'https://www.severcart.ru/blog/all/python_getattr/'
        # url = r'https://zen.yandex.ru/media/habr/chut-ne-uvolili-po-state-na-habre-5e1ed647b477bf00adcddabc'
        url = r'https://www.gazeta.ru/social/2020/06/23/13127743.shtml'
    if url:
        res = PageReader(url)
        content, path = res.page_request()
        if content:
            FileCreator().save_file(content, path)

