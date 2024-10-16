import os
import pandas as pd
import pdfplumber
import io
import re
import datetime

def text_extraction(file_content):
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            id = re.search("(?<=ID:)\s?[0-9]*", text)
            name = re.search("(?<=Name:)\s?.* .*, \w+|(?<=Nombre:)\s?.* .*, .*?(?=OD|OS)", text)
            birthdate = re.search("(?<=DOB:)\s?..-...-..|(?<=Fecha de nacimiento:)\s?[0-9]{1,2}/[0-9]{2}/[0-9]{4}", text)
            exam_date = re.search("(?<=Exam Date:)\s?..-...-..|(?<=Fecha de examen:)\s?[0-9]{1,2}/[0-9]{2}/[0-9]{4}", text)
            gender = re.search("(?<=Gender:)\s?\w+|(?<=Sexo:)\s?\w+", text)
            name = name.group().strip() if name else ''
            id = id.group().strip() if id else ''
            birthdate = birthdate.group().strip() if birthdate else ''
            exam_date = exam_date.group().strip() if exam_date else ''
            gender = gender.group().strip() if gender else ''

            try:
                birthdate = datetime.datetime.strptime(birthdate, '%d-%b-%y').date() if birthdate else None
                exam_date = datetime.datetime.strptime(exam_date, '%d-%b-%y').date() if exam_date else None
            except:
                try:
                    birthdate = datetime.datetime.strptime(birthdate, '%d/%m/%Y').date() if birthdate else None
                    exam_date = datetime.datetime.strptime(exam_date, '%d/%m/%Y').date() if exam_date else None
                except:
                    birthdate = None
                    exam_date = None

            last_name = name.split(", ")[0] if name else ''
            name = name.split(", ")[1] if name else ''

            return {
                "id": id,
                "name": name,
                "last_name": last_name,
                "birthdate": birthdate,
                "exam_date": exam_date,
                "gender": gender
            }
