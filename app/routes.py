from flask import Flask, request,jsonify
from run import app
from app.models import Jobs
scheduled_jobs_manager = Jobs([])
@app.route('/add_job',methods=['POST'])
def add_job():
    try:
        data = request.get_json()
        if not data or 'job' not in data:
            return jsonify({'error':'Missing field: job'}),400
        scheduled_jobs_manager.submit_job(data['job'])
        return jsonify({'message':'Job submitted successfully'}),201
    except Exception as e:
        print(f"Unexpected error occurred in add_job:{e}")
        return jsonify({'error':'An internal server error occured. Please try again later'}),500