from flask import Flask, url_for, request, render_template, redirect, send_file
from helpers import generatePDF, createLabelImages

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get("name")
        orderNumber = request.form.get("orderNumber")
        labelList = request.form.getlist("label")
        locationList = request.form.getlist("location")
        directionList = request.form.getlist("direction")
        notes = request.form.get("notes")
        imageList = request.files.getlist("imageInput")

        #if user didn't upload images
        if all(file.filename == ''for file in imageList):
            imageList = ''
        
        #add 'S' if not in orderNumber
        if orderNumber != '' and not orderNumber.startswith('S'):
            orderNumber = 'S' + orderNumber

        #create PDF
        pdf = generatePDF(name, orderNumber, labelList, locationList, directionList, notes, imageList)

        #if no orderNumber
        if orderNumber == '':
            #send the PDF file to the user with standard name
            return send_file(pdf, as_attachment=False, download_name="Library_Processing_Template", mimetype="application/pdf")
        
        #else return with order number in name
        return send_file(pdf, as_attachment=False, download_name=f"{orderNumber}_Processing_Template", mimetype="application/pdf")
        
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
