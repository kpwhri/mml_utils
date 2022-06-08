from livereload import Server, shell
import sys

if __name__ == '__main__':
    print('Ensure that requirements are installed: `pip install -r requirements-docs.txt`')
    make = 'make.bat' if sys.platform == 'win32' else 'make'
    server = Server()
    server.watch('*.rst', shell(f'{make} html'), delay=1)
    server.watch('*.md', shell(f'{make} html'), delay=1)
    server.watch('*.py', shell(f'{make} html'), delay=1)
    server.watch('_static/*', shell(f'{make} html'), delay=1)
    server.watch('_templates/*', shell(f'{make} html'), delay=1)
    server.serve(root='_build/html')
