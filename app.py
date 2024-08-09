from flask import Flask, render_template, request

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for processing form data
@app.route('/process', methods=['POST'])
def process():
    input_data = request.form.get('input_data')
    # Process the input_data with your Python app
    result = f'Processed data: {input_data}'
    return render_template('index.py', result=result)

if __name__ == '__main__':
    app.run(debug=True)
