# Installation Guide

### 1. Download the repository

To get started, download this repository to your local machine. You can either clone it using Git or download it as a ZIP file.

#### Clone using Git

```bash
git clone https://github.com/justogm/user-gaze-track.git
cd user-gaze-track
```

#### Download as ZIP

1. Navigate to the [repository page](https://github.com/justogm/user-gaze-track).
2. Click on the green "Code" button and select "Download ZIP".
3. Extract the ZIP file and navigate to the extracted folder.

### 2. Install the requirements

#### Using Conda

```bash
conda env create --file environment.yml
conda activate gaze-track-env
```

#### Using venv

```bash
python -m venv gaze-track-env
source gaze-track-env/bin/activate  # On Windows: gaze-track-env\Scripts\activate
pip install -r requirements.txt
```

### 3. Generate certificates

To enable HTTPS support for the gaze tracking module, you need to generate SSL certificates.

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

This command will prompt you with a series of questions and generate the *cert.pem* and *key.pem* files required by Flask.

### 4. Configure the tool

Edit the `config/config.json` file to set the desired port and specify the URL of an image or prototype to be used.

### 5. Run the tool

```bash
python app.py
```
