from flask import Flask, url_for, request, render_template, redirect
import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from helpers import createLabelTable, getImagePaths
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

        #create canvas for PDF (612.0px, 792.0px) or (8.5in, 11in)
        PAGE_WIDTH, PAGE_HEIGHT = LETTER
        canvas = Canvas("ProcessingTemplate.pdf", pagesize=LETTER)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(150, 10.2 * inch, "Library Processing Template:")

        #header border (x, y, width, height)
        canvas.rect(50, PAGE_HEIGHT - 75, PAGE_WIDTH - 100, 50)

        #book diagram image
        canvas.drawImage("static/booksDiagram.png", (PAGE_WIDTH - 512) / 2, PAGE_HEIGHT - 370, width = PAGE_WIDTH - 100, height=250)

        #create table
        table = createLabelTable(labelList, locationList, directionList)
        
        table_width, table_height = table.wrapOn(canvas, PAGE_WIDTH, PAGE_HEIGHT)

        #draw table on canvas (canvas, x, y)
        table.drawOn(canvas, (PAGE_WIDTH - 450) / 2, (PAGE_HEIGHT - 425) - table_height)

        #get image paths
        image_paths = getImagePaths(imageList)
        
        for image_path in image_paths:

            canvas.showPage()
            
            #get image original dimensions
            with Image.open(image_path) as img:
                img_width, img_height = img.size

            #scale image if it is too large
            scaling_factor = min(PAGE_WIDTH / img_width, PAGE_HEIGHT / img_height)
            new_img_width = img_width * scaling_factor
            new_img_height = img_height * scaling_factor
            
            #add image to PDF
            canvas.drawImage(image_path, (PAGE_WIDTH - new_img_width) / 2, (PAGE_HEIGHT - new_img_height) / 2, width=new_img_width, height=new_img_height)

            #save image to new page
            

        #remove images after inserting in PDF
        for image_path in image_paths:
            os.remove(image_path)

        #save and close PDF
        canvas.save()

        return {
            "label": labelList,
            "location": locationList,
            "direction": directionList,
            "notes": notes,
        }

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)