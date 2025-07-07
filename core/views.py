from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ScanResult
from .forms import ScanUploadForm
from django.contrib import messages
import pytz
from django.utils import timezone
from django.conf import settings
import os
import logging
import numpy as np
import cv2
from tensorflow import keras
from django.core.files.storage import FileSystemStorage

load_model = keras.models.load_model

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'core/home.html')

# Load models at server startup
vgg19_model = load_model('models/model_vgg19.keras')
densenet_model = load_model('models/model_DenseNet121.keras')
inceptionresnet_model = load_model('models/model_incepresnet.keras')
inceptionv3_model = load_model('models/model_Inceptionv3.keras')
xception_model = load_model('models/model_xception.keras')
models = [vgg19_model, densenet_model, inceptionresnet_model, inceptionv3_model, xception_model]

def get_className(classNo):
    return "No Brain Tumor" if classNo == 0 else "Yes Brain Tumor"

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (120, 120))  # Fixed resizing method
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def getResult(img):
    predictions = []
    for model in models:
        image = preprocess_image(img)
        result = model.predict(image)
        predictions.append(np.argmax(result, axis=1))
    final_prediction = np.round(np.mean(predictions))
    return final_prediction

@login_required
def dashboard(request):
    # Get the user's scan history regardless of the request method
    scans = ScanResult.objects.filter(user=request.user).order_by('-created_at')
    for scan in scans:
        scan.filename = os.path.basename(scan.image.name)
        scan.formatted_time = timezone.localtime(scan.created_at, pytz.timezone('Asia/Kolkata')).strftime("%B %d, %Y, %I:%M %p")

    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')  # Changed from 'file' to 'image'
        if uploaded_file:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            value = getResult(file_path)
            result = get_className(value)

            # Save the scan result to the database
            scan_result = ScanResult.objects.create(
                user=request.user,
                image=uploaded_file,
                result=result
            )

            return JsonResponse({
                'success': True,
                'filename': uploaded_file.name,
                'result': value,
                'image_url': fs.url(filename),
                'upload_time': timezone.now().astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
            })

        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

    # If it's a GET request, render the dashboard with the user's scan history
    return render(request, 'core/dashboard.html', {'scans': scans})