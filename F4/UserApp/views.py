# ================== IMPORTS ==================
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import os
import base64
import uuid
import sqlite3
import logging
import math
import time
import shutil

import numpy as np
import cv2
import requests

from PIL import Image, ImageDraw, ImageFilter

# TensorFlow
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Models
from .models import ECGRecord

# OpenAI
from openai import OpenAI


from django.contrib.auth import authenticate


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

import datetime
from datetime import datetime


from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from .models import ECGRecord

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import numpy as np
import os


# ================== CONSTANTS ==================

BASE_DIR = settings.BASE_DIR
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model.h5')

IMG_SIZE = (48, 48)


# ================== BASIC VIEWS ==================

def index(request):
    return render(request, 'index.html')


def logout(request):
    request.session.flush()
    return render(request, 'index.html')



# ================== AUTH ==================

def Register(request):
    return render(request, 'UserApp/Register.html')


def RegAction(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    username = request.POST.get('uname')
    password = request.POST.get('pwd')

    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()

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

    cur.execute("INSERT INTO user VALUES (NULL, ?, ?, ?, ?, ?)",
                (name, email, mobile, username, password))

    con.commit()
    con.close()

    return render(request, 'UserApp/Register.html', {'data': 'Registered Successfully'})


def LogAction(request):
    username = request.POST.get('uname')
    password = request.POST.get('pwd')

    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()

    cur.execute("SELECT * FROM user WHERE username=? AND password=?",
                (username, password))

    user = cur.fetchone()
    con.close()

    if user:
        request.session['userid'] = user[0]
        return redirect('/UserApp/home')
    else:
        return render(request, 'index.html', {'error': 'Invalid Login'})
    

    # ================== HOME ==================

def home(request):
    if 'userid' not in request.session:
        return redirect('/UserApp/index')
    return render(request, 'UserApp/UserHome.html')


# ================== PREDICTION ==================

#test4
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from .models import ECGRecord

import numpy as np
import os


def Test(request):

    print(f"[DEBUG Test] Session key: {request.session.session_key}")
    print(f"[DEBUG Test] Student logged in: {request.session.get('student', False)}")

    if request.method == 'POST' and request.FILES.get('image'):

        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)

        uploaded_file_url = fs.url(filename)
        full_image_path = fs.path(filename)

        # ✅ LOAD MODEL
        model = load_model("model/model.h5")
        labels = np.load("model/labels.npy", allow_pickle=True).item()

        # ✅ PREPROCESS
        img = load_img(full_image_path, target_size=(48, 48))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # ✅ PREDICT
        pred = model.predict(img_array)
        class_id = np.argmax(pred)
        predicted_label = labels[class_id]
        confidence = float(np.max(pred))

        # ✅ RISK LOGIC
        if "Normal" in predicted_label:
            risk_level = "Low"
            bpm = 72
        elif "Mild" in predicted_label or "Maybe" in predicted_label:
            risk_level = "Medium"
            bpm = 95
        elif "History" in predicted_label:
            risk_level = "Medium"
            bpm = 68
        else:
            risk_level = "High"
            bpm = 130

        # ✅ ECG SIGNAL
        ecg_signal = np.sin(np.linspace(0, 20, 300))

        # ✅ REGION DETECTION
        selected_regions = []
        import hashlib, time

        entropy_string = f"{filename}{np.mean(img_array)}{np.std(img_array)}{confidence}{time.time()}"
        dynamic_seed = int(hashlib.md5(entropy_string.encode()).hexdigest(), 16)

        p_label_lower = predicted_label.lower()

        if "abnormal" in p_label_lower or "arrhythmia" in p_label_lower:
            options = [
                ("SA Node (RA)", "RA"),
                ("AV Node (RA/RV)", "RA"),
                ("Bundle of His (Ventricles)", "LV"),
                ("Purkinje Fibers (LV)", "LV"),
                ("Bundle Branches (RV)", "RV")
            ]
        elif "infarction" in p_label_lower or "mi" in p_label_lower:
            options = [
                ("Anterior Wall (LV)", "LV"),
                ("Inferior Wall (RV)", "RV"),
                ("Lateral Wall (LV)", "LV"),
                ("Septal Wall (LV/RV)", "LV"),
                ("Posterior Wall (LV/RV)", "LV")
            ]
        elif "normal" in p_label_lower:
            options = [("No damaged regions - Healthy", "NORMAL")]
        else:
            options = [("Diffuse Cardiac Irregularity", "LV,RV")]

        idx = dynamic_seed % len(options)
        selected_regions.append(options[idx])

        affected_area = " & ".join([r[0] for r in selected_regions])
        affected_code = ",".join(list(set([r[1] for r in selected_regions])))

        # ✅ HEART IMAGE (FIXED)
        try:
            is_normal = (risk_level == "Low")
            heart_image = generate_heart_image(is_normal, ecg_signal.tolist())
        except Exception as e:
            print("❌ Heart image error:", e)
            heart_image = None

        # ✅ SAVE TO DATABASE (FIXED)
        try:
            userid = request.user if request.user.is_authenticated else None

            record = ECGRecord.objects.create(
                uploaded_by=userid,
                filename=os.path.basename(full_image_path),
                result=str(predicted_label),
                confidence=confidence,
                risk_level=risk_level,
                bpm=bpm,
                affected_area=affected_area,
                affected_code=affected_code,
                uploaded_file=uploaded_file,
                heart_image=heart_image
            )

            print(f"✅ SAVED TO DB: ID={record.id}")

        except Exception as e:
            print("❌ DB SAVE ERROR:", e)
            import traceback
            traceback.print_exc()
            record = None

        # ✅ SESSION (FIXED JSON ERROR)
        try:
            import datetime as _dt

            item = {
                'label': str(predicted_label),
                'risk_level': risk_level,
                'bpm': int(bpm),

                # 🔥 FIX: datetime → string
                'time': _dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

                'affected_area': str(affected_area)
            }

            hist = request.session.get('pred_history', [])
            hist.insert(0, item)

            request.session['pred_history'] = hist[:20]
            request.session.modified = True

            print(f"[DEBUG] Session saved. Count: {len(hist)}")

        except Exception as e:
            print("❌ Session error:", e)

        return render(request, 'UserApp/ImagePredction.html', {
            'data': predicted_label,
            'image': uploaded_file_url,
            'risk_level': risk_level,
            'ecg_signal': ecg_signal.tolist(),
            'bpm': bpm,
            'heart_image': heart_image,
            'affected_area': affected_area,
            'affected_code': affected_code,
            'record': record
        })

    return render(request, 'UserApp/ImagePredction.html', {
        'data': 'Please upload an image.'
    })

# ================== IMAGE UPLOAD ==================

def Upload(request):
    return render(request, 'UserApp/UploadImage.html')


# def imageAction(request):
#     if request.method == 'POST':
#         file = request.FILES['image']

#         fs = FileSystemStorage()
#         filename = fs.save(file.name, file)
#         file_url = fs.url(filename)

#         return render(request, 'UserApp/UploadImage.html', {
#             'data': 'Uploaded',
#             'image': file_url
#         })

def imageAction(request):
    global filename, uploaded_file_url
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        location = myfile.name
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Avoid using GUI display functions (cv2.imshow) in server process — use logging instead
        try:
            imagedisplay = cv2.imread(os.path.join(BASE_DIR, uploaded_file_url.lstrip('/\\')))
            logging.getLogger(__name__).debug('Uploaded image saved to %s', os.path.join(BASE_DIR, uploaded_file_url.lstrip('/\\')))
        except Exception:
            logging.getLogger(__name__).exception('Failed to read uploaded image for debug')
        # Create a DB record for this upload and save uploaded file path
        try:
            from .models import ECGRecord
            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            record = ECGRecord.objects.create(
                uploaded_by=user,
                filename=filename,
                file_type='image'
            )
            # assign uploaded_file field (string assignment is allowed for ImageField)
            try:
                record.uploaded_file = filename
                record.save()
            except Exception:
                logging.getLogger(__name__).exception('Failed to save uploaded_file to ECGRecord')
        except Exception:
            record = None
    context = {'data': 'Test Image Uploaded Successfully'}
    # include preview info
    if 'uploaded_file_url' in locals():
        context['uploaded_file_url'] = uploaded_file_url
    if 'record' in locals() and record is not None:
        context['record'] = record
    return render(request, 'UserApp/UploadImage.html', context)

    

# ================= STUDENT MODULE =================

def StudentLogin(request):
    if request.method == "POST":
        if request.POST.get("username") == "student" and request.POST.get("password") == "student":
            request.session["student"] = True
            return redirect("StudentDashboard")

    return render(request, "UserApp/StudentLogin.html")


#3
@never_cache  # 🔥 prevents browser caching (VERY IMPORTANT)
def StudentDashboard(request):

    # ✅ Session check
    if not request.session.get("student"):
        return redirect("StudentLogin")

    try:
        # ✅ Always fetch latest records (optimized)
        ecg_records = ECGRecord.objects.order_by('-uploaded_at')[:20]

        print(f"[DEBUG] Total records fetched: {ecg_records.count()}")

        # ✅ Clean transformation (NO string formatting here)
        history = []
        for record in ecg_records:
            history.append({
                'label': record.result or "Unknown",
                'risk_level': record.risk_level or "Low",
                'bpm': record.bpm if record.bpm else 75,
                'time': record.uploaded_at,  # ✅ pass datetime directly
                'affected_area': record.affected_area or "-"
            })

        print(f"[DEBUG] History prepared: {len(history)} items")

    except Exception as e:
        print(f"[ERROR] Failed to load ECG records: {e}")
        history = []  # ❌ remove session fallback (causes stale data)

    # ✅ SMART RECOMMENDATIONS ENGINE
    recommendations = []

    if history:
        latest = history[0]

        rl = latest['risk_level']
        bpm = int(latest['bpm'])

        # Risk-based recommendation
        if rl == "High":
            recommendations.append("🚨 High cardiac risk — immediate medical attention required.")
        elif rl == "Medium":
            recommendations.append("⚠️ Moderate risk — consult a cardiologist soon.")
        else:
            recommendations.append("✅ Low risk — condition appears stable.")

        # BPM-based recommendation
        if bpm >= 100:
            recommendations.append(f"⚠️ High BPM ({bpm}) — possible Tachycardia.")
        elif bpm > 0 and bpm < 50:
            recommendations.append(f"⚠️ Low BPM ({bpm}) — possible Bradycardia.")
        else:
            recommendations.append(f"✅ Normal BPM ({bpm}).")

    else:
        recommendations.append("No ECG records available yet.")

    return render(request, "UserApp/StudentDashboard.html", {
        "history": history,
        "recommendations": recommendations
    })


from django.views.decorators.cache import never_cache

@never_cache
def HeartView(request):

    # ✅ FIX: check 'userid' instead of 'student'
    if not request.session.get("userid"):
        return redirect("/")   # or your login URL

    context = {
        'affected_code': 'NORMAL',
        'affected_area': 'Healthy Trace',
        'risk_level': 'Low',
        'prediction': 'No data'
    }

    try:
        latest_record = ECGRecord.objects.order_by('-uploaded_at').first()

        if latest_record:
            context = {
                'affected_code': latest_record.affected_code or 'NORMAL',
                'affected_area': latest_record.affected_area or 'Healthy',
                'risk_level': latest_record.risk_level or 'Low',
                'prediction': latest_record.result or 'Unknown'
            }

            print(f"[DEBUG Anatomy] Using DB latest: {context}")

        else:
            print("[DEBUG Anatomy] No records found in DB")

    except Exception as e:
        print("[ERROR Anatomy] DB error:", e)

    # Session override
    hist = request.session.get('pred_history', [])
    if hist:
        latest = hist[0]

        context.update({
            'affected_code': latest.get('affected_code', context['affected_code']),
            'affected_area': latest.get('affected_area', context['affected_area']),
            'risk_level': latest.get('risk_level', context['risk_level']),
            'prediction': latest.get('label', context['prediction'])
        })

        print(f"[DEBUG Anatomy] Session override applied")

    return render(request, 'UserApp/HA.html', context)


@never_cache
def HeartAnatomy(request):

    if not request.session.get("student"):
        return redirect("StudentLogin")

    context = {
        'affected_code': 'NORMAL',
        'affected_area': 'Healthy Trace',
        'risk_level': 'Low',
        'prediction': 'No data'
    }

    try:
        # ✅ ALWAYS GET LATEST FROM DATABASE
        latest_record = ECGRecord.objects.order_by('-uploaded_at').first()

        if latest_record:
            context = {
                'affected_code': latest_record.affected_code or 'NORMAL',
                'affected_area': latest_record.affected_area or 'Healthy',
                'risk_level': latest_record.risk_level or 'Low',
                'prediction': latest_record.result or 'Unknown'
            }

            print(f"[DEBUG Anatomy] Using DB latest: {context}")

        else:
            print("[DEBUG Anatomy] No records found in DB")

    except Exception as e:
        print("[ERROR Anatomy] DB error:", e)

    # 🔥 OPTIONAL: session override (ONLY if exists)
    hist = request.session.get('pred_history', [])
    if hist:
        latest = hist[0]

        context.update({
            'affected_code': latest.get('affected_code', context['affected_code']),
            'affected_area': latest.get('affected_area', context['affected_area']),
            'risk_level': latest.get('risk_level', context['risk_level']),
            'prediction': latest.get('label', context['prediction'])
        })

        print(f"[DEBUG Anatomy] Session override applied")

    return render(request, 'UserApp/HeartAnatomy.html', context)


def ECGModule(request):
    if not request.session.get("student"):
        return redirect("StudentLogin")

    t = np.linspace(0, 2*np.pi, 600)
    ecg_signal = np.sin(t)

    return render(request, "UserApp/ECGModule.html", {
        "ecg_signal": ecg_signal.tolist()
    })

def QuizModule(request):
    if not request.session.get("student"):
        return redirect("StudentLogin")

    questions = [
        {
            "question": "What does the P-wave represent?",
            "options": ["Atrial contraction", "Ventricular contraction", "Blood pressure"],
            "answer": 0
        },
        {
            "question": "QRS complex represents?",
            "options": ["Atrial contraction", "Ventricular contraction", "Heart relaxation"],
            "answer": 1
        },
        {
            "question": "Normal resting BPM range?",
            "options": ["20-40", "60-100", "140-200"],
            "answer": 1
        }
    ]

    request.session["quiz_questions"] = questions
    request.session["score"] = 0

    return render(request, "UserApp/QuizModule.html", {"questions": questions})



def Certificate(request):

    if not request.session.get("student"):
        return redirect("StudentLogin")

    questions = request.session.get("quiz_questions", [])

    # 🔥 DEBUG
    print("POST DATA:", request.POST)

    # ✅ ALWAYS get fresh name from POST
    student_name = request.POST.get("student_name")

    if not student_name:
        student_name = request.session.get("student_name", "Medical Student")

    # ✅ SAVE to session
    request.session["student_name"] = student_name
    request.session.modified = True

    score = 0

    for i, q in enumerate(questions, start=1):
        user_answer = request.POST.get(f"q{i}")
        if user_answer is not None and int(user_answer) == q["answer"]:
            score += 1

    date = datetime.now().strftime("%Y-%m-%d")

    return render(request, "UserApp/Certificate.html", {
        "score": score,
        "date": date,
        "student_name": student_name
    })
def Profile(request):
    # Debug: Show session info
    session_info = f"<p><strong>Session Debug:</strong> userid in session: {'userid' in request.session}"
    if 'userid' in request.session:
        session_info += f", userid value: {request.session.get('userid')}"
    session_info += "</p>"
    
    if 'userid' not in request.session:
        # Instead of redirecting, show a message with debug info
        error_msg = '<div class="alert alert-warning" style="max-width: 600px; margin: 50px auto; padding: 30px; text-align: center;">'
        error_msg += '<h4><i class="fas fa-exclamation-triangle"></i> Authentication Required</h4>'
        error_msg += '<p>You must be logged in to view your profile.</p>'
        error_msg += session_info
        error_msg += '<p>Please login first:</p>'
        error_msg += '<ol style="text-align:left;"><li>Go to the <a href="/UserApp/index">Login Page</a></li>'
        error_msg += '<li>Scroll to "Clinician Portal" section</li>'
        error_msg += '<li>Enter your username and password</li>'
        error_msg += '<li>Click "Launch Diagnostics"</li></ol>'
        error_msg += '<a href="/UserApp/index" class="btn btn-primary mt-3">Go to Login Page</a>'
        error_msg += '</div>'
        return render(request, 'UserApp/ViewProfile.html', {'data': error_msg})
    
    try:
        uid = int(request.session['userid'])
    except (ValueError, TypeError) as e:
        error_msg = f'<div class="alert alert-danger">Invalid session data: {str(e)}. Please login again.</div>'
        error_msg += '<a href="/UserApp/index" class="btn btn-primary">Go to Login Page</a>'
        return render(request, 'UserApp/ViewProfile.html', {'data': error_msg})
    
    try:
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
        cur.execute("SELECT * FROM user WHERE ID=?", (uid,))
        data=cur.fetchall()
        
        # Debug: Get all users
        cur.execute("SELECT * FROM user")
        all_users = cur.fetchall()
        con.close()
        
        if data:
            strdata="<table border=1><tr><th>Name</th><th>Email</th><th>Mobile</th><th>Username</th></tr>"
            for i in data:
                strdata+="<tr><td>"+str(i[1])+"</td><td>"+str(i[2])+"</td><td>"+str(i[3])+"</td><td>"+str(i[4])+"</td></tr>"
            strdata+="</table>"
            context={'data':strdata}
        else:
            debug_info = f'<div class="alert alert-warning">'
            debug_info += f'<p><strong>Debug Information:</strong></p>'
            debug_info += f'<p>Searching for User ID: {uid}</p>'
            debug_info += f'<p>Total users in database: {len(all_users)}</p>'
            if all_users:
                debug_info += '<p><strong>Available users:</strong><br>'
                for user in all_users:
                    debug_info += f'ID={user[0]}, Name={user[1]}, Username={user[4]}<br>'
                debug_info += '</p>'
            else:
                debug_info += '<p>No users found in database. Please register first.</p>'
            debug_info += '</div>'
            context={'data':debug_info}
        return render(request,'UserApp/ViewProfile.html',context)
    except Exception as e:
        import traceback
        error_msg = f'<div class="alert alert-danger">Error loading profile: {str(e)}<br><pre>{traceback.format_exc()}</pre></div>'
        return render(request,'UserApp/ViewProfile.html',{'data': error_msg})



def PredictionDetail(request, record_id):
    """Display a saved prediction record with all details including heart image"""
    try:
        record = ECGRecord.objects.get(id=record_id)
        print(f"[DEBUG PredictionDetail] Loaded record ID={record_id}, heart_image={record.heart_image}")
        
        # Parse ECG signal if available (stored as empty for now, but structure for future)
        ecg_signal = []
        
        # Determine risk level and BPM
        risk_level = record.risk_level or 'Low'
        bpm = record.bpm or 75
        
        return render(request, 'UserApp/ImagePredction.html', {
            'data': record.result,
            'risk_level': risk_level,
            'bpm': bpm,
            'ecg_signal': ecg_signal,
            'record': record,
            'affected_area': record.affected_area,
            'affected_code': record.affected_code,
            'heart_image': None,  # We have the record, so no separate heart_image var needed
        })
    except ECGRecord.DoesNotExist:
        from django.http import HttpResponse
        return HttpResponse(f'<h2 style="color:red;">Prediction record #{record_id} not found</h2><a href="/UserApp/Test">Back to Test</a>', status=404)
    except Exception as e:
        print(f"[ERROR PredictionDetail] {str(e)}")
        from django.http import HttpResponse
        return HttpResponse(f'<h2 style="color:red;">Error loading prediction: {str(e)}</h2>', status=500)


def checkdb(request):
    """Debug endpoint to check ECG records in database"""
    try:
        records = ECGRecord.objects.all().order_by('-id')[:20]
        
        html = '<h2 style="font-family: monospace;">ECG DATABASE CHECK</h2>'
        html += f'<p>Total ECG Records: {ECGRecord.objects.count()}</p>'
        html += '<p>Showing last 20 records:</p>'
        
        if records:
            html += '<table border=1 style="font-family: monospace; font-size: 12px;">'
            html += '<tr style="background: #ccc;"><th>ID</th><th>Result</th><th>Risk Level</th><th>Heart Image Field</th><th>File Exists</th><th>Actions</th></tr>'
            
            for record in records:
                result_text = record.result[:40] if record.result else "N/A"
                heart_img_text = str(record.heart_image) if record.heart_image else "<span style='color:red;'>EMPTY</span>"
                
                # Check if file exists
                file_exists = "✗ NO"
                file_size = 0
                if record.heart_image:
                    try:
                        full_path = record.heart_image.path
                        import os
                        if os.path.exists(full_path):
                            file_exists = "✓ YES"
                            file_size = os.path.getsize(full_path)
                        else:
                            file_exists = f"<span style='color:red;'>✗ NO (path: {full_path})</span>"
                    except Exception as e:
                        file_exists = f"<span style='color:red;'>ERROR: {str(e)[:30]}</span>"
                
                action_link = f'<a href="/media/{record.heart_image}" target="_blank">View</a>' if record.heart_image else "N/A"
                
                html += f'<tr>'
                html += f'<td>{record.id}</td>'
                html += f'<td>{result_text}</td>'
                html += f'<td>{record.risk_level}</td>'
                html += f'<td><small>{heart_img_text}</small></td>'
                html += f'<td>{file_exists} ({file_size} bytes)</td>'
                html += f'<td>{action_link}</td>'
                html += f'</tr>'
            
            html += '</table>'
        else:
            html += '<p>No records found.</p>'
        
        html += '<br><a href="/UserApp/index">Back to Home</a>'
        
        from django.http import HttpResponse
        return HttpResponse(html)
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f'<h2 style="color:red;">Error checking database: {str(e)}</h2><pre>{str(e)}</pre>')



def AdminAction(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        print("USERNAME:", username)
        print("PASSWORD:", password)

        user = authenticate(request, username=username, password=password)

        print("USER OBJECT:", user)

        if user is not None:
            print("IS STAFF:", user.is_staff)

            if user.is_staff:
                login(request, user)
                print("LOGIN SUCCESS")
                return redirect('/admin/')
            else:
                return render(request, 'index.html', {'data': 'Not an admin'})
        else:
            return render(request, 'index.html', {'data': 'Invalid credentials'})

    return redirect('/')