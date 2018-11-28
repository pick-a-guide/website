import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import json


class WebSite(object):

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
        return self.render(tps)


    def do_authenticationJSON(self, usr, pwd, typ):
        user = self.get_user()
        db_json = json.load(open(WebSite.dbjson))
        users = db_json[typ]

        for u in users:
            if u['username'] == usr and u['password'] == pwd:
                self.set_user(usr)
                break


########################################################################################################################
#   Controllers

    @cherrypy.expose
    def index(self):

        return self.render('index.html')


    @cherrypy.expose
    def about(self):
        tparams = {
            'title': 'About',
            'message': 'Your application description page.',
            'user': self.get_user(),
        }
        return self.render('about.html', tparams)


    @cherrypy.expose
    def contact(self):
        tparams = {
            'title': 'Contact',
            'message': 'Your contact page.',
            'user': self.get_user(),
        }
        return self.render('contact.html', tparams)


    @cherrypy.expose
    def loginGuia(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('iniciarSessaoGuia.html', tparams)
        else:

            self.do_authenticationJSON(username, password, 'guia')
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Login',
                    'errors': True,
                    'user': self.get_user(),
                }
                return self.render('iniciarSessaoGuia.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("dashguia.html")

    @cherrypy.expose
    def loginGuiado(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('iniciarSessaoGuiado.html', tparams)
        else:

            self.do_authenticationJSON(username, password, 'guia')
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Login',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def logout(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def signup(self):
        pass


    @cherrypy.expose
    def shut(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.quickstart(WebApp(), '/', conf)
