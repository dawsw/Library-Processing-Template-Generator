from flask import Flask, url_for, request, render_template, redirect, send_file
from helpers import generatePDF, createLabelImages

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        labelList = request.form.getlist("label")
        locationList = request.form.getlist("location")
        directionList = request.form.getlist("direction")
        notes = request.form.get("notes")
        imageList = request.files.getlist("imageInput")

        #if user didn't upload images
        if all(file.filename == ''for file in imageList):
            imageList = ''

        #create PDF
        pdf = generatePDF(labelList, locationList, directionList, notes, imageList)

        # Send the PDF file to the user
        return send_file(pdf, as_attachment=False, download_name="Library_Processing_Template", mimetype="application/pdf")

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
