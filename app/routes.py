
from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/chat-info")
def chat_info():
    return "<span>Servidor de chat disponível</span>"
