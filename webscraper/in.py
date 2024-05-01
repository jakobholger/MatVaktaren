from bs4 import BeautifulSoup
import sys


def main(args):
    print(args[0])
    file = args[0]
    with open(file, 'r') as f:
        html_content = f.read()
    parse_html(html_content)

def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup.prettify())

if __name__ == '__main__':
    main(sys.argv[1:])
