# -*- coding: utf-8 -*-
"""[Final Submission] Image Classification Model Deployment - M Radya Fariez.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1titD3qZ_zjQKlrdefYO6Jgmg0KuEaeYd
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import tensorflow as tf
import zipfile, os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import shutil
# %matplotlib inline

#cane     - dog 
#elefante - elephant
#gallina  - chicken
#pecora   - sheep

!pip install -q kaggle

# upload kaggle.json
from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json
!ls ~/.kaggle

!kaggle datasets download -d alessiocorrado99/animals10

!mkdir animals
!unzip -qq animals10.zip -d animals
!ls animals

!ls animals/raw-img/

animals = os.path.join('/content/animals/raw-img/')
print(os.listdir(animals))

ignore_animals = ['farfalla','cavallo','gatto','ragno','scoiattolo','mucca']

for x in ignore_animals:
  path = os.path.join(animals, x)
  shutil.rmtree(path)

list_animals = os.listdir(animals)
print(list_animals)

from PIL import Image
total = 0

for x in list_animals:
  dir = os.path.join(animals, x)
  y = len(os.listdir(dir))

  print(x+':', y)
  total = total + y
  
  img_name = os.listdir(dir)
  for z in range(5):
    img_path = os.path.join(dir, img_name[z])
    img = Image.open(img_path)
    print('#',img.size)
  print('<<<<<<<>>>>>>>')

print('\nTotal Amount:', total)

import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 2, figsize=(15,15))
fig.suptitle("Random Images", fontsize=24)
animals_sorted = sorted(list_animals)
animals_id = 0
for i in range(2):
  for j in range(2):
    try:
      animals_selected = animals_sorted[animals_id] 
      animals_id += 1
    except:
      break
    if animals_selected == '.TEMP':
        continue
    animals_selected_images = os.listdir(os.path.join(animals, animals_selected))
    animals_selected_random = np.random.choice(animals_selected_images)
    img = plt.imread(os.path.join(animals, animals_selected, animals_selected_random))
    ax[i][j].imshow(img)
    ax[i][j].set_title(animals_selected, pad=10, fontsize=22)
    
plt.setp(ax, xticks=[],yticks=[])
plt.show

#Augmentation Data & Train Test Split
training_data = ImageDataGenerator(
      rescale = 1./255,
      rotation_range = 35,
      width_shift_range = 0.2,
      height_shift_range = 0.2,
      shear_range = 0.2,
      zoom_range = 0.2,
      horizontal_flip = True,
      fill_mode = 'nearest',
      validation_split = 0.2
    )

batch_size = 32 #processing data dalam 1 epoch (mempengaruhi runtime)
data_train = training_data.flow_from_directory(
    animals,
    target_size= (150, 150),
    batch_size= batch_size,
    class_mode= 'categorical',
    subset= 'training')

data_val = training_data.flow_from_directory(
    animals, 
    target_size= (150, 150),
    batch_size= batch_size,
    class_mode= 'categorical',
    subset= 'validation')

#Pembentukan model sequential

tf.device('/device:GPU:0')

model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(8, (3,3), activation = 'relu', input_shape = (150,150,3)),  #layer konvolusi ke-1
    tf.keras.layers.MaxPooling2D(2, 2),  

    tf.keras.layers.Conv2D(16, (3,3), activation = 'relu'), #layer konvolusi ke-2
    tf.keras.layers.MaxPooling2D(2, 2),

    tf.keras.layers.Conv2D(32, (3,3), activation = 'relu'), #layer konvolusi ke-3
    tf.keras.layers.MaxPooling2D(2, 2), 

    tf.keras.layers.Conv2D(64, (3,3), activation='relu'), #layer konvolusi ke-4
    tf.keras.layers.MaxPooling2D(2,2), 

    tf.keras.layers.Flatten(),  #layer input untuk deep learning NN
    tf.keras.layers.Dropout(0.5),

    #tf.keras.layers.Dense(128, activation = 'relu'),  #hidden layer ke-1
    tf.keras.layers.Dense(128, activation = 'relu'),  #hidden layer ke-2
    tf.keras.layers.Dense(4, activation = 'softmax')  #layer output
])

model.summary()

#Compile model
model.compile(optimizer = 'adam', metrics = ['accuracy'], loss = 'categorical_crossentropy')

#Callback opt
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    #if(logs.get('Accuracy')>=0.9 and logs.get('val_Accuracy')>=0.9):
    if logs.get('Accuracy') is not None and logs.get('Accuracy') > 0.90:
      self.model.stop_training = True
      print("\nAccuracy and val_Accuracy reached 90%")

callbacks = myCallback()

#train model NN
history = model.fit(
      data_train,
      steps_per_epoch = 35, #jumlah batch yang akan dieksekusi
      epochs = 150, 
      validation_data = data_val, #untuk tampilan akurasi
      validation_steps = 5, # jumlah batch yang akan dieksekusi pada setiap epoch
      verbose = 1,
      callbacks = [callbacks])

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Accuracy')
plt.ylabel('Accuracy Level')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss')
plt.ylabel('Loss Level')
plt.xlabel('Epoch')
plt.legend(['Train', 'Val'], loc='upper left')
plt.show()

# Melakukan konversi model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)

!ls -la | grep 'model'