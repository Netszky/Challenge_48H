import os
from sys import stderr

from bson import ObjectId
from dns import *
from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
import gunicorn
import pprint


app = Flask(__name__)
#Lien MongoAtlas
app.config['MONGO_URI'] = 'mongodb+srv://root:root@cluster0.wqlut.mongodb.net/passionfroid?retryWrites=true&w=majority'

mongo = PyMongo(app)
db = mongo.db.passionfroid

@app.route('/', methods=['GET', 'POST'])
def index():
#Index
    if request.method == "POST":
        recherche = request.form.get("recherche")
        filtre = request.form.get("filtre")
        #Barre de recherche
        if recherche:
            if filtre == 'Tag':
                a = recherche.split()
                print("tag")

                images = db.find({"$or": [{"tag": {"$regex": recherche[0]}}, {"tag": {"$regex": recherche[1]}}]})
                return render_template('index.html', images=images)
            elif filtre == 'Categorie':
                print("Cat")
                images = db.find({"categorie": {"$regex": recherche}})
                return render_template('index.html', images=images)
            elif filtre == 'Nom':
                print("nom")
                images = db.find({"image_passionfroid_name": {"$regex": recherche}})
                countimages = images.count()
                return render_template('index.html', images=images, countimages=countimages)
        else:
            images = db.find()
            countimages = images.count()
            return render_template('index.html', images=images, countimages=countimages)
    else:
        #Requete non filtrée index
        images = db.find()
        countimages = images.count()
        return render_template('index.html', images=images, countimages=countimages)

@app.route('/AjouterPhoto')
#Formulaire Ajout
def ajouter():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
#Ajout photo dans base
def upload():

    if 'image_passionfroid[]' in request.files:
        image_passionfroid = request.files.getlist('image_passionfroid[]')

        categorie = request.form['categorie']
        tag = request.form['tag']
        tag = tag.split()
        contract = request.form.getlist('radio_contract')
        hasHuman = request.form.getlist('radio')
        format = request.form.getlist('radio_format')
        for i in image_passionfroid:
            mongo.save_file(i.filename, i)
            mongo.db.passionfroid.insert({'image_passionfroid_name': i.filename, 'categorie': categorie, 'tag': tag, 'hasHuman': hasHuman, 'Contractuelle': contract, 'format': format})
    return redirect(url_for('index'))


@app.route('/image/<filename>')
#Envoyer image
def image(filename):
    return mongo.send_file(filename)

@app.route('/Catégorie/<categorie>', methods=['GET'])
#Filtre Catégorie = Ambiance
def Ambiance(categorie):
    images = db.find({'categorie': categorie})
    countimages = images.count()
    return render_template('index.html', images=images, countimages=countimages)

@app.route('/Catégorie/<categorie>', methods=['GET'])
#Filtre Catégorie = Produit
def Produit(categorie):
    images = db.find({'categorie': categorie})
    countimages = images.count()
    return render_template('index.html', images=images, countimages=countimages)

@app.route('/detail/<id>', methods=['GET'])
#Detail image quand cliquée
def detail(id):
    detail = db.find_one({'_id': ObjectId(id)})
    return render_template('detail.html', detail=detail)

@app.route('/update/<id>', methods=['POST'])
#Mise a jour Image
def update(id):
    #image_passionfroid = request.files['image_passionfroid']
    categorie = request.form.get('categorie')
    tag = request.form.get('tag')
    hasHuman = request.form.getlist('radio')
    contract = request.form.getlist('radio_contract')
    format_image = request.form.getlist('radio_format')


    updated_image = db.find_one({'_id': ObjectId(id)})
    #updated_image["image_passionfroid_name"] = image_passionfroid
    updated_image["categorie"] = categorie
    updated_image["tag"] = tag
    updated_image["hasHuman"] = hasHuman
    updated_image["Contractuelle"] = contract
    updated_image["format"] = format_image

    db.replace_one({'_id': ObjectId(id)}, updated_image)
    return redirect(url_for('detail', id=id))


@app.route('/delete/<id>', methods=['POST'])
#Suppression Image
def delete(id):
    db.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

@app.route('/Human/<choix>', methods=['GET'])
#Filtre onglet droit à l'image
def Human(choix):
    images = db.find({'hasHuman': choix})
    print(choix)
    countimages = images.count()
    return render_template('index.html', images=images, countimages=countimages)

@app.route('/Contract/<choix>', methods=['GET'])
#filtre onglet Contractuelle
def Contract(choix):
    images = db.find({'Contractuelle': choix})
    print(choix)
    countimages = images.count()
    return render_template('index.html', images=images, countimages=countimages)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5000, debug=True)
