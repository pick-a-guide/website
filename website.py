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
                return True
        return False

    def register_userJSON(self, usr, pwd, typ, data):

        db_json = json.load(open(WebApp.dbjson))
        users = db_json[typ]
        aux = {'username' : usr, 'password' : pwd, 'data': data}

        for u in users:
            if u['username'] == usr:
                return

        self.set_user(usr)
        users.append(aux)
        json.dump(db_json, open(WebApp.dbjson, 'w'))

    def change_data(self, usr, typ, dt):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json[typ]
        aux = {}
        for u in users:
            if u['username'] == usr:
                aux = u
                users.remove(u)
                if 'data' not in aux.keys():
                    aux['data'] = {}
                for each in dt.keys():
                    aux['data'][each] = dt[each]
        
        if aux == {}:
            return False
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
                'errors': False,
                'user': self.get_user(),
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
                raise cherrypy.HTTPRedirect("dashboardGuia?page=dashG1")

    @cherrypy.expose
    def iniciarSessaoGuiado(self, username=None, password=None):
        if username == None:
            tparams = {
                'errors': False,
                'user': self.get_user(),
            }
            return self.render('iniciarSessaoGuiado.html', tparams)
        else:

            self.do_authenticationJSON(username, password, 'guiado')
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'errors': True,
                    'user': self.get_user(),
                }
                return self.render('iniciarSessaoGuiado.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("dashboardGuiado?page=dashg1")

    @cherrypy.expose
    def registoGuia(self, name=None, email=None, mobile=None, password=None, city=None):
        if name == None:
            tparams = {
                'errors': False,
                'user': self.get_user(),
            }
            return self.render('registoGuia.html',tparams)
        else:
            if name != None and email != None and mobile != None and password != None and city != None:
                self.register_userJSON(email,password,'guia',{'name':name,'mobile':mobile,'city':city})
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'errors': True,
                    'user': self.get_user(),
                }
                return self.render('registoGuia.html',tparams)
            else:
                raise cherrypy.HTTPRedirect("dashboardGuia?page=dashG1")
    
    @cherrypy.expose
    def registoGuiado(self, name=None, email=None, mobile=None, password=None):
        if name == None:
            tparams = {
                'errors': False,
                'user': self.get_user()
            }
            return self.render('registoGuiado.html',tparams)
        else:
            if name != None and email != None and mobile != None and password != None:
                self.register_userJSON(email,password,'guiado',{'name':name,'mobile':mobile})
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'errors': True,
                    'user': self.get_user(),
                }
                return self.render('registoGuiado.html',tparams)
            else:
                raise cherrypy.HTTPRedirect("dashboardGuiado?page=dashg1")
    
    @cherrypy.expose
    def dashboardGuia(self, page=None, password=None, mobile=None, city=None):
        tparams = {
            'user': self.get_user(),
            'dashG1': False,
            'dashG2': False,
            'dashG3': False,
            'dashG4': False,
            'dashG5': False,
            'dashG6': False,
            'errors': False
        }
        if page != None:
            tparams[page] = True
        if password != None:
            if not self.do_authenticationJSON(self.get_user()['username'],password,"guia"):
                tparams['errors'] = True
            else:
                data = {}
                if mobile != None:
                    data["mobile"] = mobile
                if city != None:
                    data["city"] = city
                self.change_data(self.get_user()['username'],"guia",data)
        return self.render('dashguia.html',tparams)

    @cherrypy.expose
    def dashboardGuiado(self, page=None, password=None, mobile=None):
        tparams = {
            'user': self.get_user(),
            'dashg1': False,
            'dashg2': False,
            'dashg3': False,
            'dashg4': False,
            'dashg5': False,
            'dashg6': False,
            'errors': False
        }
        if page != None:
            tparams[page] = True
        if password != None:
            if not self.do_authenticationJSON(self.get_user()['username'],password,"guiado"):
                tparams['errors'] = True
            else:
                data = {}
                if mobile != None:
                    data["mobile"] = mobile
                self.change_data(self.get_user()['username'],"guiado",data)
        return self.render('dashguiado.html',tparams)
    
    @cherrypy.expose
    def teaserGuia(self):
        return open('pages/teaserGuia.html').read()

    @cherrypy.expose
    def teaserGuiado(self):
        return open('pages/teaserGuiado.html').read()
    
    @cherrypy.expose
    def sair(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")

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
