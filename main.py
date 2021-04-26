from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from werkzeug.utils import secure_filename
import os
import pdfplumber
from gtts import gTTS
import datetime as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
Bootstrap(app)

#----Get Year (for copyright)----#
now = dt.datetime.now()
year = now.year

#----Create Forms----#
class UploadForm(FlaskForm):
    file = FileField(label='Upload File')
    submit = SubmitField("Submit")

#----Create Routes----#

@app.route("/")
def home():
    return render_template("index.html", year = year)

@app.route("/listen")
def listen():
    files = os.listdir('static/audiobooks')
    return render_template("listen.html", year = year, files = files)

@app.route("/create", methods=['GET', 'POST'])
def create():
    form = UploadForm()
    if form.validate_on_submit():
    #--Save PDF--#
        filename = secure_filename(form.file.data.filename)
        form.file.data.save('static/pdfs/' + filename)
    #--Convert PDF to Text--#
        with pdfplumber.open(f'static/pdfs/{filename}') as pdf:
            for i in range (0,len(pdf.pages)):
                page=pdf.pages[i]
                with open (f'static/text/text_{filename.strip(".pdf")}.txt', 'a') as file:
                    file.write(page.extract_text())
    #--Convert Text to Speech--#
        with open (f'static/text/text_{filename.strip(".pdf")}.txt', 'r') as file:
            audio_raw = gTTS(text=file.read(), lang='en', slow=False)
            audio = audio_raw.save(f'static/audiobooks/{filename.strip(".pdf")}.mp3')
    #--All Done!--#
        return redirect(url_for('listen'))
    return render_template("create.html", year = year, form = form)

@app.route("/delete/<file>", methods = ['GET'])
def delete(file):
    os.remove(f"static/audiobooks/{file}")
    return redirect(url_for('listen'))

if __name__ == '__main__':
    app.run(debug=True)
