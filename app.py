from flask import Flask, render_template, request, flash, redirect, url_for
import os
from logics_1 import load_trained_model, classify_image, get_responsible_person

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the model once when the app starts
model = load_trained_model()

# Route for the homepage where the form is located
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get the form data
    pnr_number = request.form['pnr']
    image_file = request.files['file']

    if not image_file or not pnr_number:
        flash("Please provide both an image and a PNR number.")
        return render_template('index.html')

    # Save the uploaded image to a temporary location
    image_path = os.path.join('uploads', image_file.filename)
    image_file.save(image_path)

    # Classify the image using the loaded model
    try:
        classification_tag = classify_image(model, image_path)
    except Exception as e:
        flash(f"Error in image classification: {str(e)}")
        return render_template('index.html')

    # Identify the responsible personnel based on the PNR number and tag
    result = get_responsible_person(classification_tag, pnr_number)

    # Remove the temporary image file
    os.remove(image_path)

    # Extract the TT/CRPF ID and Route Incharge ID from the result
    responsible_person = result['responsible_person']
    route_incharge = result['route_incharge']

    # Redirect to either the TT or CRPF page with the relevant IDs
    if classification_tag == 'violence':
        # Redirect to CRPF page
        return redirect(url_for('crpf_info', crpf_id=responsible_person, incharge_id=route_incharge))
    else:
        # Redirect to TT page
        return redirect(url_for('tt_info', tt_id=responsible_person, incharge_id=route_incharge))

# Route for TT page
@app.route('/tt-info')
def tt_info():
    tt_id = request.args.get('tt_id')
    incharge_id = request.args.get('incharge_id')
    return render_template('tt.html', tt_id=tt_id, incharge_id=incharge_id)

# Route for CRPF page
@app.route('/crpf-info')
def crpf_info():
    crpf_id = request.args.get('crpf_id')
    incharge_id = request.args.get('incharge_id')
    return render_template('crpf.html', crpf_id=crpf_id, incharge_id=incharge_id)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
