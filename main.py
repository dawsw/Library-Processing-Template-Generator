from flask import Flask, url_for, request, render_template, redirect
import os
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        labels = []

        labelList = request.form.getlist("label")
        locationList = request.form.getlist("location")
        directionList = request.form.getlist("direction")
        notes = request.form.get("notes")
        imageList = request.files.getlist("images")
        
        for label in range(len(labelList)):
            labels.append([labelList[label], locationList[label], directionList[label]])
        print(labels)
        
        #create canvas for PDF

        #612.0, 792.0  or 8.5, 11
        width, height = LETTER
        canvas = Canvas("ProcessingTemplate.pdf", pagesize=LETTER)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(150, 10.2 * inch, "Library Processing Template:")

        #x, y, width, height
        canvas.rect(50, height - 75, width - 100, 50)

        #
        canvas.drawImage("static/booksDiagram.png", (width - 512) / 2, height - 350, width= width - 100, height=250)

        #save and close PDF
        canvas.save()

        print(os.path.abspath("static/cover.png"))

        return {
            "label": labelList,
            "location": locationList,
            "direction": directionList,
            "notes": notes,
        }

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)