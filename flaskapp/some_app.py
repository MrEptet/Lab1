'''
# модули работы с формами и полями в формах
from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
# модули валидации полей формы
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import Flask, Response, render_template
import base64
from PIL import Image
from io import BytesIO
import json
import lxml.etree as ET
import os
import sys
from . import net as neuronet
import gc

app = Flask(__name__)
#декоратор для вывода страницы по умолчанию
@app.route("/")
def hello():
 return " <html><head></head> <body> Hello World! </body></html>"
if __name__ == "__main__":
 app.run(host='127.0.0.1', port = 10000) 
# используем csrf токен, можете генерировать его сами
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdODV8sAAAAAAd3JTTL9Few1qPix-q0ijaRfVIC'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdODV8sAAAAAMHonXgrsII-IA20FuBY_8hGBZgw'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
# обязательно добавить для работы со стандартными шаблонами
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
# создаем форму для загрузки файла
class NetForm(FlaskForm):
 # поле для введения строки, валидируется наличием данных
 # валидатор проверяет введение данных после нажатия кнопки submit
 # и указывает пользователю ввести данные, если они не введены
 # или неверны
 openid = StringField('openid', validators = [DataRequired()])
 # поле загрузки файла
 # здесь валидатор укажет ввести правильные файлы
 upload = FileField('Load image', validators=[
 FileRequired(),
 FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
 # поле формы с capture
 recaptcha = RecaptchaField()
 #кнопка submit, для пользователя отображена как send
 submit = SubmitField('send')
# функция обработки запросов на адрес 127.0.0.1:5000/net
# модуль проверки и преобразование имени файла
# для устранения в имени символов типа / и т.д.
from werkzeug.utils import secure_filename
import os
# подключаем наш модуль и переименовываем
# для исключения конфликта имен
# метод обработки запроса GET и POST от клиента
@app.route("/net",methods=['GET', 'POST'])
def net():
 # создаем объект формы
 form = NetForm()
 # обнуляем переменные, передаваемые в форму
 filename=None
 neurodic = {}
 # проверяем нажатие сабмит и валидацию введенных данных
 if form.validate_on_submit():
 # файлы с изображениями читаются из каталога static
  base_dir = os.path.dirname(os.path.abspath(__file__))
  static_path = os.path.join(base_dir, 'static')
  fcount, fimage = neuronet.read_image_files(10, static_path)
  filename = os.path.join(static_path, secure_filename(form.upload.data.filename))
 # передаем все изображения в каталоге на классификацию
 # можете изменить немного код и передать только загруженный файл
  decode = neuronet.getResult(fimage)
 # записываем в словарь данные классификации
  for elem in decode:
   neurodic[elem[0][1]] = elem[0][2]
 # сохраняем загруженный файл
  form.upload.data.save(filename)
 # передаем форму в шаблон, так же передаем имя файла и результат работы нейронной
 # сети, если был нажат сабмит, либо передадим falsy значения
 gc.collect()
 return render_template('net.html',form=form,image_name=filename,neurodic=neurodic) 

from flask import request
# метод для обработки запроса от пользователя
@app.route("/apinet",methods=['GET', 'POST'])
def apinet():
 neurodic = {}
 # проверяем, что в запросе json данные
 if request.mimetype == 'application/json':
  # получаем json данные
  data = request.get_json()
  # берем содержимое по ключу, где хранится файл
  # закодированный строкой base64
  # декодируем строку в массив байт, используя кодировку utf-8
  # первые 128 байт ascii и utf-8 совпадают, потому можно
  filebytes = data['imagebin'].encode('utf-8')
  # декодируем массив байт base64 в исходный файл изображение
  cfile = base64.b64decode(filebytes)
  # чтобы считать изображение как файл из памяти, используем BytesIO
  img = Image.open(BytesIO(cfile))
  decode = neuronet.getResult([img])
  neurodic = {}
  for elem in decode:
   neurodic[elem[0][1]] = str(elem[0][2])
   print(elem)
 # преобразуем словарь в json-строку
 ret = json.dumps(neurodic)
 # готовим ответ пользователю
 resp = Response(response=ret,
          status=200,
          mimetype="application/json")
 # возвращаем ответ
 return resp 
 
@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
 #парсим xml файл в dom
 dom = ET.parse("./static/xml/file.xml")
 #парсим шаблон в dom
 xslt = ET.parse("./static/xml/file.xslt")
 #получаем трансформер
 transform = ET.XSLT(xslt)
 #преобразуем xml с помощью трансформера xslt
 newhtml = transform(dom)
 #преобразуем из памяти dom в строку, возможно, понадобится указать кодировку
 strfile = ET.tostring(newhtml)
 return strfile 
'''

import random
from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
# модули валидации полей формы
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import Flask, Response, render_template
import base64
from PIL import Image
from io import BytesIO
import json
import lxml.etree as ET
import os
import sys
# from . import net as neuronet # <-- Импорт модуля neuronet удален
import gc
# модуль проверки и преобразование имени файла для устранения в имени символов типа / и т.д.
from werkzeug.utils import secure_filename

app = Flask(__name__)
# декоратор для вывода страницы по умолчанию
@app.route("/")
def hello():
 return " <html><head></head> <body> Hello World! </body></html>"
if __name__ == "__main__":
 app.run(host='127.0.0.1', port = 10000) 
# используем csrf токен, можете генерировать его сами
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
# используем капчу и полученные секретные ключи с сайта Google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdODV8sAAAAAAd3JTTL9Few1qPix-q0ijaRfVIC'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdODV8sAAAAAMHonXgrsII-IA20FuBY_8hGBZgw'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
# обязательно добавить для работы со стандартными шаблонами
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
# создаем форму для загрузки файла
class NetForm(FlaskForm):
 openid = StringField('openid', validators = [DataRequired()])
 upload = FileField('Load image', validators=[
 FileRequired(),
 FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
 recaptcha = RecaptchaField()
 submit = SubmitField('send')

# метод обработки запроса GET и POST от клиента
@app.route("/net",methods=['GET', 'POST'])
def net():
 # создаем объект формы
 form = NetForm()
 # обнуляем переменные, передаваемые в форму
 filename=None
 neurodic = None # Инициализация как None, чтобы шаблон знал, что данных пока нет

 # проверяем нажатие сабмит и валидацию введенных данных
 if form.validate_on_submit():
  # файлы с изображениями читаются из каталога static
  base_dir = os.path.dirname(os.path.abspath(__file__))
  static_path = os.path.join(base_dir, 'static')
  
  filename = os.path.join(static_path, secure_filename(form.upload.data.filename))
 
  # Логика нейросети полностью удалена.
  # Вместо этого можно добавить другую логику обработки файла или просто сохранить его.
  
  # Сохраняем загруженный файл
  form.upload.data.save(filename)
  
  # В этом месте neurodic остается None, если вы не добавите другую логику

 # передаем форму в шаблон, так же передаем имя файла и результат работы 
 # (neurodic будет None при GET-запросе или после обработки без результатов)
 gc.collect()
 return render_template('net.html',form=form,image_name=filename,neurodic=neurodic) 

from flask import request
# метод для обработки запроса от пользователя
@app.route("/apinet",methods=['GET', 'POST'])
def apinet():
 neurodic = None
 # проверяем, что в запросе json данные
 if request.mimetype == 'application/json':
  data = request.get_json()
  filebytes = data['imagebin'].encode('utf-8')
  cfile = base64.b64decode(filebytes)
  img = Image.open(BytesIO(cfile))
  
  # Логика нейросети удалена. neurodic остается None.
  
  # Если вам нужен ответ в формате JSON, но без результатов НС, 
  # можно вернуть просто статус OK:
  neurodic = {"status": "image received and processed"}

 # преобразуем словарь в json-строку (если он был инициализирован)
 if neurodic is not None:
     ret = json.dumps(neurodic)
 else:
     ret = json.dumps({"status": "no data processed"})
     
 # готовим ответ пользователю
 resp = Response(response=ret,
          status=200,
          mimetype="application/json")
 # возвращаем ответ
 return resp 
 
@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
 #парсим xml файл в dom
 dom = ET.parse("./static/xml/file.xml")
 #парсим шаблон в dom
 xslt = ET.parse("./static/xml/file.xslt")
 #получаем трансформер
 transform = ET.XSLT(xslt)
 #преобразуем xml с помощью трансформера xslt
 newhtml = transform(dom)
 #преобразуем из памяти dom в строку, возможно, понадобится указать кодировку
 strfile = ET.tostring(newhtml)
 return strfile
