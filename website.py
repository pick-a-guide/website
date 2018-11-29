import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import json


class WebApp(object):

    dbjson = 'data/db.json'

    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('website','pages'),
                autoescape=select_autoescape(['html', 'xml'])
                )


########################################################################################################################
#   Utilities

    def set_user(self, username=None):
        if username == None:
            cherrypy.session['user'] = {'is_authenticated': False, 'username': ''}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username}


    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']


    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)


    def do_authenticationJSON(self, usr, pwd, typ):
        user = self.get_user()
        db_json = json.load(open(WebApp.dbjson))
        users = db_json[typ]

        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                self.set_user(usr)
                break

    def register_userJSON(self, usr, pwd, typ):

        db_json = json.load(open(WebApp.dbjson))
        users = db_json[typ]
        aux = {'username' : usr, 'password' : pwd}

        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                print("Erro")
                return

        users.append(aux)
        json.dump(db_json, open(WebApp.dbjson, 'w'))


########################################################################################################################
#   Controllers

    @cherrypy.expose
    def index(self):
        return open("pages/index.html","r").read()

    @cherrypy.expose
    def escolhaInicioSessao(self):
        return open("pages/escolhaInicioSessao.html").read()

    @cherrypy.expose
    def escolhaRegisto(self):
        return open("pages/escolhaRegisto.html").read()

    @cherrypy.expose
    def iniciarSessaoGuia(self, username=None, password=None):
        if username == None:
            tparams = {
                'errors': False
                #'user': self.get_user(),
            }
            return self.render('iniciarSessaoGuia.html', tparams)
        else:

            self.do_authenticationJSON(username, password, 'guia')
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'errors': True,
                    'user': self.get_user(),
                }
                return self.render('iniciarSessaoGuia.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("dashboardGuia")

    @cherrypy.expose
    def loginGuiado(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('pages/iniciarSessaoGuiado.html', tparams)
        else:

            self.do_authenticationJSON(username, password, 'guia')
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Login',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('pages/login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("pages/index.html")

    @cherrypy.expose
    def dashboardGuia(self):
        return open('pages/dashguia.html').read()
    
    @cherrypy.expose
    def sair(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def signup(self):
        pass


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './css'
        },
        '/assets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './assets'
        },
        '/vendor': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './vendor'
        }
    }
    cherrypy.quickstart(WebApp(), '/', conf)
