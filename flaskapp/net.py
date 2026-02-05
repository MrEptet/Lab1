import random
import os
# модуль работы с изображениями
from PIL import Image
import numpy as np
# Конфигурация GPU удалена, так как не нужна без TensorFlow/Keras

height = 255
width = 255

# чтение изображений из каталога
# учтите, если там есть файлы, не соответствующие изображениям, или каталоги
# возникнет ошибка
def read_image_files(files_max_count,dir_name):
  files = os.listdir(dir_name)
  files_count = files_max_count
  if(files_max_count>len(files)): # определяем количество файлов не больше max
   files_count = len(files)
  image_box = [[]]*files_count
  for file_i in range(files_count): # читаем изображения в список
    full_path = os.path.join(dir_name, files[file_i])
    img = Image.open(full_path)
    img.load()
    image_box[file_i] = img
  return files_count, image_box
  
def getResult(image_box):
  files_count = len(image_box)
  images_resized = [[]]*files_count
  # нормализуем изображения и преобразуем в numpy
  for i in range(files_count):
   # Преобразование в numpy массив и нормализация до диапазона [0.0, 1.0]
   images_resized[i] = np.array(image_box[i].resize((height,width)))/255.0
  images_resized = np.array(images_resized)
  
  # Код, связанный с resnet.predict и decode_predictions, удален.
  # Функция теперь возвращает numpy-массив изображений
  return images_resized
