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

    def get_data(self, usr, typ):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json[typ]
        for u in users:
            if u['username'] == usr:
                if "data" in u.keys():
                    return u['data']
                else:
                    return []
        return None

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

    def open_chat(self, guia, guiado):
        js = json.load(open("data/messages.json"))
        for each in js:
            if each["guia"] == guia and each["guiado"] == guiado:
                return
        chat = {
            "guia": guia,
            "guiado": guiado,
            guia: self.get_data(guia,"guia")["name"],
            guiado: self.get_data(guiado,"guiado")["name"],
            "last_message":"Never",
            "messages": []
        }
        js.append(chat)
        json.dump(js, open("data/messages.json",'w'))

    def close_chat(self, guia, guiado):
        js = json.load(open("data/messages.json"))
        for each in js:
            if each["guia"] == guia and each["guiado"] == guiado:
                js.remove(each)
                return
        json.dump(js, open("data/messages.json"))

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
    def dashboardGuia(self, page=None, password=None, mobile=None, city=None, file=None):
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect("/")
        if self.get_data(self.get_user()['username'],'guia') == None:
            raise cherrypy.HTTPRedirect("/")
        tparams = {
            'username': self.get_user()['username'],
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
        if page == "dashG2":
            data = self.get_data(self.get_user()['username'],"guia")
            for each in data:
                tparams[each] = data[each]
            if "image" not in data:
                tparams["image"] = "assets/pfp/default.png"
        if password != None:
            if not self.do_authenticationJSON(self.get_user()['username'],password,"guia"):
                tparams['errors'] = True
            else:
                data = {}
                if mobile != None and mobile != "":
                    data["mobile"] = mobile
                if city != None and city != "-Escolha-":
                    data["city"] = city
                if file != None:
                    path = "assets/pfp/guia/"+tparams['username']
                    data['image'] = path
                self.change_data(self.get_user()['username'],"guia",data)
        self.set_user(tparams['username'])
        return self.render('dashguia.html',tparams)

    @cherrypy.expose
    def dashboardGuiado(self, page=None, password=None, mobile=None, file=None):
        if not self.get_user()['is_authenticated']:
            raise cherrypy.HTTPRedirect("/")
        if self.get_data(self.get_user()['username'],'guiado') == None:
            raise cherrypy.HTTPRedirect("/")
        tparams = {
            'username': self.get_user()['username'],
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
        if page == "dashg2":
            data = self.get_data(self.get_user()['username'],"guiado")
            for each in data:
                tparams[each] = data[each]
            if "image" not in data:
                tparams["image"] = "assets/pfp/default.png"
        if password != None:
            if not self.do_authenticationJSON(self.get_user()['username'],password,"guiado"):
                tparams['errors'] = True
            else:
                data = {}
                if mobile != None and mobile != "":
                    data["mobile"] = mobile
                if file != None:
                    path = "assets/pfp/guiado/"+tparams['username']
                    data['image'] = path
                self.change_data(self.get_user()['username'],"guiado",data)
        self.set_user(tparams['username'])
        return self.render('dashguiado.html',tparams)
    
    @cherrypy.expose
    def teaserGuia(self):
        return open('pages/teaserGuia.html').read()

    @cherrypy.expose
    def upload(self, file, type, password):
        if not self.do_authenticationJSON(self.get_user()['username'],password,type):
            return
        path = "assets/pfp/"+type+"//"+self.get_user()['username']
        if os.path.isfile(path):
            os.remove(path)
        open(path,"bw+").write(file.file.read())

    @cherrypy.expose
    def get_messages(self):
        if not self.get_user()['is_authenticated']:
            return
        user = self.get_user()['username']
        js = json.load(open("data/messages.json"))
        messages = []
        for each in js:
            if each["guia"] == user or each["guiado"] == user:
                messages.append(each)
        return json.dumps(messages)

    @cherrypy.expose
    def post_message(self, message, user):
        if not self.get_user()['is_authenticated']:
            return
        post = self.get_user()['username']
        print(post)
        print(user)
        js = json.load(open("data/messages.json"))
        m = {}
        talk = {}
        for each in js:
            if each["guia"] == post and each["guiado"] == user:
                talk = each
            if each["guiado"] == post and each["guia"] == user:
                talk = each
        if talk == {}:
            return
        m["destination"] = user
        m["content"] = message
        m["date"] = datetime.today().strftime('%Y/%m/%d')
        talk["messages"].append(m)
        talk["last_message"]= m["date"]
        print(js)
        print(talk)
        json.dump(js,open("data/messages.json",'w'))

    @cherrypy.expose
    def teaserGuiado(self):
        return open('pages/teaserGuiado.html').read()
    
    @cherrypy.expose
    def requisitar_guia(self, guia):
        if not self.get_user()['is_authenticated']:
            return
        if self.get_data(self.get_user()['username'],'guiado') == None:
            return
        self.open_chat(guia,self.get_user()['username'])

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
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './js'
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
