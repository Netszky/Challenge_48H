import os
from sys import stderr

from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
import pprint


app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/passionfroid'

mongo = PyMongo(app)
db = mongo.db.passionfroid
db2 = mongo.db.fs.files


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        recherche = request.form.get("recherche")
        if recherche:
            recherche = str.capitalize(recherche)
            images = db.find({"tag": {"$regex": recherche}})
            return render_template('index.html', images=images)
    else:
        images = db.find()
        return render_template('index.html', images=images)

@app.route('/AjouterPhoto')
def ajouter():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image_passionfroid' in request.files:
        image_passionfroid = request.files['image_passionfroid']
        categorie = request.form['categorie']
        tag = request.form['tag']
        contract = request.form.getlist('radio_contract')
        hasHuman = request.form.getlist('radio')
        for i in image_passionfroid:
            mongo.save_file(i.filename, i)
            mongo.db.passionfroid.insert_one({'image_passionfroid_name': i.filename, 'categorie': categorie, 'tag': tag, 'hasHuman': hasHuman, 'Contractuelle': contract})
    return redirect(url_for('index'))

@app.route('/image/<filename>')
def image(filename):
    return mongo.send_file(filename)

@app.route('/Catégorie/<categorie>', methods=['GET'])
def Ambiance(categorie):
    images = db.find({'categorie': categorie})
    return render_template('index.html', images=images)

@app.route('/Catégorie/<categorie>', methods=['GET'])
def Produit(categorie):
    images = db.find({'categorie': categorie})
    return render_template('index.html', images=images)

@app.route('/detail/<id>', methods=['GET'])
def detail(id):
    detail = db.find_one({'_id': ObjectId(id)})
    return render_template('detail.html', detail=detail)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
