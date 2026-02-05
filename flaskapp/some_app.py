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

app = Flask(__name__)
@app.route("/")
def hello():
    return " <html><head></head> <body> Hello World! </body></html>"

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
    
    modified_image_data = image_data.copy()

    height = 255
    width = 255
    
    if percentage == 0:
        return modified_image_data # Избегаем деления на ноль, если процент 0

    total = int(height * (percentage / 100.0))
    
    if total == 0:
        return image_data # Гарантируем, что размер блока хотя бы 1 пиксель
    
    # Закрашиваем ячейки черным
    for i in range(height // total + 1): # Добавляем +1 на случай неполного покрытия
     for j in range(width // total + 1):
      if (i + j) % 2 == 0:
       # Безопасно определяем конечные индексы с помощью min()
       y_start = i * total
       y_end = min(y_start + total, height) # Ограничиваем высоту
       x_start = j * total
       x_end = min(x_start + total, width) # Ограничиваем ширину

       # Проверяем, что срез не пустой перед присваиванием
       if y_start < y_end and x_start < x_end:
        # Присваиваем черный цвет [0, 0, 0]
        # Убедитесь, что массив цвета соответствует типу данных изображения (float или int)
        modified_image_data[y_start:y_end, x_start:x_end, :] = [0.0, 0.0, 0.0]
                
    return modified_image_data

# --- Маршруты приложения Flask ---

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
        original_image_np = np.array(original_image.resize((255, 255))) / 255.0
        print(f"Image dtype: {original_image_np.dtype}")

        # 2. Создаем измененное изображение
        modified_image_np = apply_checkerboard(original_image_np, percentage)
        modified_image_unit8 = (modified_image_np * 255).astype(np.uint8)
        modified_image = Image.fromarray(modified_image_unit8, 'RGB')
        
        # Сохраняем измененное изображение
        modified_simple_filename = "modified_" + simple_filename
        modified_filename_path = os.path.join(static_path, modified_simple_filename)
        modified_image.save(modified_filename_path)
        modified_url = url_for('static', filename=modified_simple_filename)
        
        # 3. Генерируем графики
        create_histogram(original_image_np, 'original_hist.png', 'Original Image Color Distribution')
        create_histogram(modified_image_np, 'modified_hist.png', 'Modified Image Color Distribution')

        print(f"DEBUG INFO: modified_image_np shape: {modified_image_np.shape}", flush=True)
        print(f"DEBUG INFO: modified_image_np dtype: {modified_image_np.dtype}", flush=True)
        
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
