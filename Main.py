import os
from sys import stderr

from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

