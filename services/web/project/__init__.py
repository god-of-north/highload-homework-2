import os

from werkzeug.utils import secure_filename
from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    redirect,
    url_for
)
#from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("project.config.Config")
#db = SQLAlchemy(app)


#class User(db.Model):
#    __tablename__ = "users"
#
#    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(128), unique=True, nullable=False)
#    active = db.Column(db.Boolean(), default=True, nullable=False)
#
#    def __init__(self, email):
#        self.email = email


@app.route("/")
def hello_world():
    return jsonify(hello="world")


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """


from datetime import datetime
from elasticsearch import Elasticsearch

@app.route("/elastic")
def load_elastic():
    es = Elasticsearch(['http://elasticsearch:9200'])
    
    doc = {
        'author': 'kimchy',
        'text': 'Elasticsearch: cool. bonsai cool.',
        'timestamp': datetime.now(),
    }
    res = es.index(index="test-index", id=1, document=doc)
    
    ret = ""
    ret = ret + str(res['result']) + '\n'
    
    res = es.get(index="test-index", id=1)
    ret = ret + str(res['_source']) + '\n'
    
    es.indices.refresh(index="test-index")

    res = es.search(index="test-index", query={"match_all": {}})
    ret = ret + ("Got %d Hits:" % res['hits']['total']['value']) + '\n'
    for hit in res['hits']['hits']:
        ret = ret + ("%(timestamp)s %(author)s: %(text)s" % hit["_source"]) + '\n'
    return ret




import pymongo 

@app.route("/mongo")
def load_mongo():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/", username='root', password='example')

    mydb = myclient["testdb"]
    mycol = mydb["customers"]

    mydict = { "name": "John", "address": "Highway 37" }
    x = mycol.insert_one(mydict)

    ret = ''
    for x in mycol.find():
        ret = ret+str(x)+'\n' 
    return ret



def fibonacci_of(n):
    if n in {0, 1}:  
        return n
    return fibonacci_of(n - 1) + fibonacci_of(n - 2) 


@app.route("/cpu")
def load_cpu():
    return jsonify(fib=fibonacci_of(30))
