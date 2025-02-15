from flask import Flask, url_for, request, render_template, redirect
import os

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

        return {
            "label": labelList,
            "location": locationList,
            "direction": directionList,
            "notes": notes,
        }

    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)