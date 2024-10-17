# MediFlow  

MediFlow is a web-based application designed to streamline the analysis of Optical Coherence Tomography (OCT) exams for ophthalmologists. This guide will walk you through the steps to **download, install, and run the project** on your local machine.

---

## **Prerequisites**  

Before setting up MediFlow, ensure that the following are installed:  
- **Python 3.8+**  
- **pip (Python package manager)**  
- **Git**  
- **Virtualenv** (optional, but recommended)  

Additionally, the project requires **Tesseract OCR** to be installed. Follow the instructions below to install it from the [UB Mannheim Tesseract Repository](https://github.com/UB-Mannheim/tesseract/wiki).

---

## **Installation Instructions**

### 1. Clone the Repository  
First, clone the MediFlow project repository to your local machine. Open a terminal and run:  

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

### 2. Set up a Virtual Environment (Optional)  
It’s recommended to use a virtual environment to avoid conflicts between dependencies. Create and activate the virtual environment:  

**On Linux/macOS:**  
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**  
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies  
Install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Install Tesseract OCR  
You need to install **Tesseract OCR** to enable the OCR functionality. Follow the steps below:  

1. Visit the [UB Mannheim Tesseract Repository](https://github.com/UB-Mannheim/tesseract/wiki).  
2. Download and install the **Tesseract executable** for your operating system.  
3. Add Tesseract to your system’s PATH (check the installation guide for instructions).  
4. Verify the installation by running:

```bash
tesseract --version
```

---

### 5. Set up the Django Project  
1. **Run migrations** to set up the database schema:

```bash
python manage.py migrate
```

2. **Create a superuser** to access the admin panel:

```bash
python manage.py createsuperuser
```

---

### 6. Run the Development Server  
Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### 7. Accessing the Admin Panel  
You can log in to the **admin panel** using the superuser credentials you created earlier:  
[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## **Usage**  
- Upload OCT exam files from the web interface.  
- Use the OCR functionality to extract data automatically.  
- Manage patients, exams, and results through the admin panel.

---

## **Troubleshooting**  
- If you encounter issues with **Tesseract**, ensure it is properly installed and available in your system's PATH.
- For dependency-related errors, try reinstalling the packages using:  
  ```bash
  pip install --force-reinstall -r requirements.txt
  ```

---
