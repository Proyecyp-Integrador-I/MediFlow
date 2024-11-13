from exam.models import Exam, Patient
from exam.utils.calculate_age import calculate_age
from datetime import datetime
import os

from django.conf import settings

MEDIA_ROOT = settings.MEDIA_ROOT


# Takes a list of dictionaries that correspond to a filename and relative filepath and the InMemoryUploadedFile file objects
# Creates a folder structure with the InMemoryUploadedFile file objects organized by patient folder
def process_folder_structure(folder_structure, files):
    patient_folders = {}
    print(folder_structure)
    for element in folder_structure:
        print(len(folder_structure))
        print(element)
        folder = '/'.join(element['path'].split('/')[0:-1])
        file = element['name']
        print(folder, file)
        uploaded_file = next((f for f in files if f.name == file), None)
        print(folder, file, uploaded_file)

        if folder not in patient_folders:
            patient_folders[folder] = [uploaded_file]
        else:
            patient_folders[folder].append(uploaded_file)

    return patient_folders

def save_extracted_patient(patient_info):
    if not patient_info.get('id'):
        print("Patient info not found")
        return False, patient_info
    else:
        patient = Patient.objects.filter(identification=patient_info['id']).first()
        print("searching patient")
        if not patient:
            print("Patient not found")
            patient = Patient(
                    name=patient_info.get('name', None),
                    last_name=patient_info.get('last_name', None),
                    identification=patient_info.get('id', None), 
                    age=calculate_age(patient_info.get('birthdate')) if patient_info.get('birthdate') else None,
                    date_of_birth=patient_info.get('birthdate', None),
                    gender=patient_info.get('gender', None)
                )
            patient.save()
        else:
            print("Patient found, editing")
            patient.name = patient_info.get('name', patient.name)
            patient.last_name = patient_info.get('last_name', patient.last_name)
            patient.age = calculate_age(patient_info.get('birthdate')) if patient_info.get('birthdate') else patient.age
            patient.date_of_birth = patient_info.get('birthdate', patient.date_of_birth)
            patient.save()

        return True, patient

def save_extracted_exam(patient, patient_info, exam_path):
    exam = Exam.objects.filter(patient=patient, file=exam_path).first()
    if not exam:
        exam = Exam(patient=patient, exam_date=patient_info['exam_date'], file=exam_path)
        exam.save()
    elif exam.exam_date != patient_info['exam_date']:
        exam.exam_date = patient_info['exam_date']
        exam.save()
    return exam

def get_new_exam_path(patient_info, folder):
    
    patient_folder_name = folder.split("/")[-1]
    try:
        exam_file_name = f"{patient_info['name']} {patient_info['last_name']} {patient_info['exam_date'].strftime('%Y-%m-%d')}.pdf"
        exam_path = os.path.join(MEDIA_ROOT,"uploads", exam_file_name)
    except:
        # Case where no information was extracted
        exam_file_name = f"{patient_folder_name}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        exam_path = os.path.join(MEDIA_ROOT,"uploads", exam_file_name)
    return exam_path
