# AdminApp/views.py

from django.shortcuts import render
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import io, base64

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# ------------------ BASIC PAGES ------------------

def index(request):
    return render(request, 'index.html')

def AdminAction(request):
    name = request.POST.get('username')
    apass = request.POST.get('password')

    if name == 'Admin' and apass == 'Admin':
        return render(request, "AdminApp/AdminHome.html")
    else:
        return render(request, "index.html", {'data': "Login Failed"})
    
def Adminhome(request):
    return render(request, "AdminApp/AdminHome.html")   

# ------------------ USER MANAGEMENT ------------------

def ViewAllUsers(request):
    con = sqlite3.connect("db.sqlite3")
    cur=con.cursor()
    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            mobile TEXT,
            username TEXT,
            password TEXT
        )
    """)
    cur.execute("select * from user")
    data=cur.fetchall()
    con.close()
    strdata="<table border=1><tr><th>Name</th><th>Email</th><th>Mobile</th><th>Username</th><th>Action</th></tr>"
    for i in data:
        strdata+="<tr><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td><td>"+str(i[3])+"</td><td>"+str(i[4])+"</td><td><a href='/Delete?id="+str(i[0])+"'>Delete</a></td></tr>"
    context={'data':strdata}
    return render(request,'AdminApp/ViewAllUsers.html',context)


def Delete(request):
    uid=request.GET['id']
    con = sqlite3.connect("db.sqlite3")
    cur1=con.cursor()
    cur1.execute("delete from user where ID=?", (uid,))
    con.commit()
    cur=con.cursor()
    cur.execute("select * from user")
    data=cur.fetchall()
    con.close()
    strdata="<table border=1><tr><th>Name</th><th>Email</th><th>Mobile</th><th>Username</th><th>Action</th></tr>"
    for i in data:
        strdata+="<tr><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td><td>"+str(i[3])+"</td><td>"+str(i[4])+"</td><td><a href='/Delete?id="+str(i[0])+"'>Delete</a></td></tr>"
    context={'data':strdata}
    return render(request,'AdminApp/ViewAllUsers.html',context)



# ------------------ DATASET ------------------

global traindataset
traindataset = "Dataset"

def UploadDataset(request):
    return render(request, "AdminApp/UploadDataset.html",
                  {'data': "Dataset Ready"})


# ------------------ DATA GENERATION ------------------

def DataGenerate(request):
    global training_set, test_set

    datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2
    )

    training_set = datagen.flow_from_directory(
        traindataset,
        target_size=(48, 48),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )

    test_set = datagen.flow_from_directory(
        traindataset,
        target_size=(48, 48),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )

    return render(request, 'AdminApp/Generate.html')


# ------------------ CNN MODEL ------------------

def GenerateCNN(request):
    training_set = ImageDataGenerator(rescale=1./255).flow_from_directory(
        traindataset, target_size=(48, 48), batch_size=32)

    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=(48,48,3)),
        MaxPooling2D(2,2),
        Conv2D(32, (3,3), activation='relu'),
        MaxPooling2D(2,2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(training_set.num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(training_set, epochs=5)

    acc = history.history['accuracy'][-1]
    request.session['cnn_acc'] = float(acc)

    return render(request, 'AdminApp/LoadModel.html',
                  {'msg': f"CNN Accuracy: {acc:.2f}"})

# ------------------ ANN MODEL ------------------

def GenerateANN(request):
    training_set = ImageDataGenerator(rescale=1./255).flow_from_directory(
        traindataset, target_size=(48, 48), batch_size=32)

    model = Sequential([
        Flatten(input_shape=(48,48,3)),
        Dense(256, activation='relu'),
        Dense(128, activation='relu'),
        Dense(training_set.num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(training_set, epochs=5)

    acc = history.history['accuracy'][-1]
    request.session['ann_acc'] = float(acc)

    return render(request, 'AdminApp/LoadModel.html',
                  {'msg': f"ANN Accuracy: {acc:.2f}"})


# ------------------ COMPARISON ------------------

def comparison(request):
    cnn_acc = request.session.get('cnn_acc', 0) * 100
    ann_acc = request.session.get('ann_acc', 0) * 100

    models = ['CNN', 'ANN']
    values = [cnn_acc, ann_acc]

    plt.bar(models, values)
    plt.title("Accuracy Comparison")

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image_png = buffer.getvalue()
    chart = base64.b64encode(image_png).decode()

    return render(request, 'AdminApp/Graph.html',
                  {'chart': chart})


def logout(request):
    return render(request, 'index.html')

