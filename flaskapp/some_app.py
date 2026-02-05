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
 relative_filename=None # <-- Добавлена новая переменная
 neurodic = None 

 # проверяем нажатие сабмит и валидацию введенных данных
 if form.validate_on_submit():
  base_dir = os.path.dirname(os.path.abspath(__file__))
  static_path = os.path.join(base_dir, 'static')
  
  # Генерируем безопасное имя файла
  simple_filename = secure_filename(form.upload.data.filename)
  
  # Формируем полный путь для сохранения
  filename = os.path.join(static_path, simple_filename)
 
  # Формируем относительный путь для веба (только имя файла)
  relative_filename = simple_filename # <-- Используем только имя файла

  # Сохраняем загруженный файл
  form.upload.data.save(filename)
  
 # Передаем в шаблон относительный путь вместо полного filename
 gc.collect()
 return render_template('net.html',form=form, image_name=filename, image_url=relative_filename, neurodic=neurodic) 

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
'''

import random
import os
import sys
import gc
import json
import base64
import lxml.etree as ET
import numpy as np
import matplotlib
# Используем бэкенд Agg для работы на сервере без графического интерфейса
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import Flask, Response, render_template, url_for, request
from flask_bootstrap import Bootstrap

# from . import net as neuronet # Импорт нейросети удален

app = Flask(__name__)

# --- Конфигурация приложения ---
SECRET_KEY = 'secret'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdODV8sAAAAAAd3JTTL9Few1qPix-q0ijaRfVIC'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdODV8sAAAAAMHonXgrsII-IA20FuBY_8hGBZgw'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
# Определяем папку static для сохранения графиков
app.config['STATIC_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

bootstrap = Bootstrap(app)

# --- Классы форм ---
class NetForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    upload = FileField('Load image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    percentage = IntegerField('Percentage (0-100%)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100, message='Value must be between 0 and 100')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('send')

# --- Вспомогательные функции обработки изображений и графиков ---

def create_histogram(image_data, filename, title):
    """Генерирует гистограмму цветов и сохраняет ее в файл."""
    plt.figure(figsize=(8, 4))
    plt.title(title)
    plt.hist(image_data[:, :, 0].ravel(), bins=256, color='red', alpha=0.5, label='Red')
    plt.hist(image_data[:, :, 1].ravel(), bins=256, color='green', alpha=0.5, label='Green')
    plt.hist(image_data[:, :, 2].ravel(), bins=256, color='blue', alpha=0.5, label='Blue')
    plt.legend()
    filepath = os.path.join(app.config['STATIC_FOLDER'], filename)
    plt.savefig(filepath)
    plt.close()

def apply_checkerboard(image_data: np.ndarray, percentage: int) -> np.ndarray:
    """
    Применяет маску в виде сетки 4x6 к изображению NumPy, закрашивая 
    процент ячеек случайным образом.

    :param image_data: Исходное изображение в виде массива NumPy (H, W, C).
    :param percentage: Процент ячеек, которые должны быть закрашены черным (0-100).
    :return: Изображение с примененной маской.
    """
    h, w, c = image_data.shape
    
    # Жестко задаем количество строк и столбцов по вашему примеру (4 ряда, 6 колонок)
    rows = 4
    cols = 6
    cell_h = h // rows
    cell_w = w // cols
    total_cells = rows * cols

    modified_image_data = image_data.copy()

    # Создаем список всех индексов ячеек и перемешиваем их
    all_cell_indices = [(i, j) for i in range(rows) for j in range(cols)]
    random.shuffle(all_cell_indices)

    # Определяем количество ячеек для закрашивания на основе процента
    cells_to_mask_count = int((percentage / 100.0) * total_cells)
    cells_to_mask = all_cell_indices[:cells_to_mask_count]

    # Закрашиваем выбранные ячейки черным
    for i, j in cells_to_mask:
        y1 = i * cell_h
        y2 = (i + 1) * cell_h
        x1 = j * cell_w
        x2 = (j + 1) * cell_w
        # Заполнение черным цветом для RGB
        modified_image_data[y1:y2, x1:x2] = [0, 0, 0]
            
    return modified_image_data

# --- Маршруты приложения Flask ---

@app.route("/")
def hello():
    return " <html><head></head> <body> Hello World! </body></html>"

@app.route("/net", methods=['GET', 'POST'])
def net():
    form = NetForm()
    filename = None
    relative_filename = None
    modified_url = None
    original_plot_url = None
    modified_plot_url = None
    neurodic = None 

    if form.validate_on_submit():
        static_path = app.config['STATIC_FOLDER']
        
        simple_filename = secure_filename(form.upload.data.filename)
        filename = os.path.join(static_path, simple_filename)
        relative_filename = simple_filename 
        form.upload.data.save(filename)
        
        percentage = form.percentage.data
        
        # 1. Загружаем изображение и преобразуем в NumPy
        original_image = Image.open(filename).convert('RGB')
        original_image_np = np.array(original_image)

        # 2. Создаем измененное изображение
        modified_image_np = apply_checkerboard(original_image_np, percentage)
        modified_image = Image.fromarray(modified_image_np, 'RGB')
        
        # Сохраняем измененное изображение
        modified_simple_filename = "modified_" + simple_filename
        modified_filename_path = os.path.join(static_path, modified_simple_filename)
        modified_image.save(modified_filename_path)
        modified_url = url_for('static', filename=modified_simple_filename)
        
        # 3. Генерируем графики
        create_histogram(original_image_np, 'original_hist.png', 'Original Image Color Distribution')
        create_histogram(modified_image_np, 'modified_hist.png', 'Modified Image Color Distribution')
        
        original_plot_url = url_for('static', filename='original_hist.png')
        modified_plot_url = url_for('static', filename='modified_hist.png')
        
    gc.collect()
    return render_template('net.html', form=form, image_name=filename, image_url=relative_filename, neurodic=neurodic, 
                           modified_url=modified_url, original_plot_url=original_plot_url, modified_plot_url=modified_plot_url) 

@app.route("/apinet", methods=['GET', 'POST'])
def apinet():
    neurodic = None
    if request.mimetype == 'application/json':
        data = request.get_json()
        filebytes = data['imagebin'].encode('utf-8')
        cfile = base64.b64decode(filebytes)
        img = Image.open(BytesIO(cfile))
        
        # Логика обработки API без нейросети
        neurodic = {"status": "image received and processed"}

    if neurodic is not None:
        ret = json.dumps(neurodic)
    else:
        ret = json.dumps({"status": "no data processed"})
        
    resp = Response(response=ret, status=200, mimetype="application/json")
    return resp 
 
@app.route("/apixml", methods=['GET', 'POST'])
def apixml():
    dom = ET.parse("./static/xml/file.xml")
    xslt = ET.parse("./static/xml/file.xslt")
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile 

if __name__ == "__main__":
    # Убедитесь, что папка static существует
    if not os.path.exists(app.config['STATIC_FOLDER']):
        os.makedirs(app.config['STATIC_FOLDER'])
        
    app.run(host='127.0.0.1', port=10000, debug=True)
