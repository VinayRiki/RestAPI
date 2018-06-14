from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Simple API',
    description='A simple API',
)

ns = api.namespace('books', description='Books in Library')

book = api.model('Book', {
    'id': fields.Integer(readOnly=True, description='Book id number'),
    'BookName': fields.String(required=True, description='Name of the Book')
})


class BookDAO(object):
    def __init__(self):
        self.counter = 0
        self.books = []

    def get(self, id):
        for book in self.books:
            if book['id'] == id:
                return book
        api.abort(404, "book {} doesn't exist".format(id))

    def create(self, data):
        book = data
        book['id'] = self.counter = self.counter + 1
        self.books.append(book)
        return book

    def delete(self, id):
        book = self.get(id)
        self.books.remove(book)


DAO = BookDAO()
DAO.create({'task': 'Build an API'})
DAO.create({'task': '?????'})
DAO.create({'task': 'profit!'})


@ns.route('/')
class BookList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(book)
    def get(self):
        '''Shows All Books in Library'''
        return DAO.books

    @ns.doc('create_todo')
    @ns.expect(book)
    @ns.marshal_with(book, code=201)
    def post(self):
        '''Add Book To Library'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Book(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(book)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_book')
    @ns.response(204, 'Book deleted')
    def delete(self, id):
        '''Delete a book using its id'''
        DAO.delete(id)
        return '', 204



if __name__ == '__main__':
    app.run(debug=True,port=8080)