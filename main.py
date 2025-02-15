from flask import Flask, url_for, request, render_template, redirect, send_file
import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from helpers import generatePDF
from PIL import Image

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        labelList = request.form.getlist("label")
        locationList = request.form.getlist("location")
        directionList = request.form.getlist("direction")
        notes = request.form.get("notes")
        imageList = request.files.getlist("images")

        pdf = generatePDF(labelList, locationList, directionList, notes, imageList)

        return send_file(pdf, as_attachment=False, download_name="Library_Processing_Template.pdf", mimetype="application/pdf")

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)