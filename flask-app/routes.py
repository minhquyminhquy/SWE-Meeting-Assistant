import os
import uuid
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, abort
import threading
from werkzeug.utils import secure_filename
from app import db
from models import Meeting
from meeting_assistant import transcribe_audio, generate_meeting_summary

logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def process_meeting_recording(meeting_id, file_path):
    """
    Process the meeting recording in a background thread.
    
    Args:
        meeting_id (str): The ID of the meeting
        file_path (str): Path to the audio file
    """
    try:
        # Retrieve the meeting from the database
        
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            logger.error(f"Meeting with ID {meeting_id} not found")
            return
            
        # Transcribe the audio
        logger.debug(f"Starting transcription for meeting {meeting_id}")
        transcript = transcribe_audio(file_path)
        
        meeting.transcript = transcript
        db.session.commit()
        
        # Generate meeting summary
        logger.debug(f"Generating summary for meeting {meeting_id}")
        summary_data = generate_meeting_summary(transcript)
        
        # Update the meeting object with the summary data
        meeting.summary = summary_data.get('summary', '')
        meeting.decisions = '\n'.join(summary_data.get('decisions', []))
        

        #meeting.action_items = '\n'.join(summary_data.get('action_items', []))
        #meeting.action_items = '\n'.join(str(item) for item in summary_data.get('action_items', []))
        # Assuming summary_data.get('action_items', []) returns a list of dictionaries:
        meeting.action_items = '\n'.join(
            f"{item['task']} (Assigned to: {item['assignee']}, Deadline: {item['deadline']})"
            for item in summary_data.get('action_items', [])
        )

        logger.info(meeting.decisions)
        logger.info(meeting.action_items)

        # Convert Each Dictionary to a String:
        #meeting.action_items = '\n'.join(str(item) for item in summary_data.get('action_items', []))
        meeting.processed = True
        db.session.commit()
        
        logger.debug(f"Processing completed for meeting {meeting_id}")
    except Exception as e:
        #logger.error(f"Error processing meeting {meeting_id}: {str(e)}")
        logger.error(f"Error processing meeting {meeting_id}: {str(e)}", exc_info=True)
        # Update the meeting with the error
        meeting = Meeting.query.get(meeting_id)
        if meeting:
            meeting.error = str(e)
            meeting.processed = True
            db.session.commit()

def register_routes(app):
    """
    Register all routes for the application.
    
    Args:
        app: The Flask application
    """
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file upload and start processing. Works"""
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        title = request.form.get('title', 'Untitled Meeting')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            # Generate a unique filename
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Create a new Meeting record
            meeting = Meeting(
                title=title,
                recording_filename=unique_filename,
                original_filename=filename
            )
            db.session.add(meeting)
            db.session.commit()
            
            process_meeting_recording(meeting_id=meeting.id, file_path=file_path)
            
            # Redirect to the summary page
            flash('Your meeting recording has been uploaded and is being processed.', 'success')
            return redirect(url_for('view_summary', meeting_id=meeting.id))
        else:
            flash(f'Invalid file format. Allowed formats: {", ".join(app.config["ALLOWED_EXTENSIONS"])}', 'danger')
            return redirect(request.url)
    
    @app.route('/summary/<meeting_id>')
    def view_summary(meeting_id):
        """Display the meeting summary."""
        meeting = Meeting.query.get_or_404(meeting_id)
        return render_template('summary.html', meeting=meeting)
    
    @app.route('/history')
    def view_history():
        """Display the meeting history."""
        meetings = Meeting.query.order_by(Meeting.created_at.desc()).all()
        return render_template('history.html', meetings=meetings)
    
    @app.route('/api/meeting/<meeting_id>')
    def get_meeting_status(meeting_id):
        """API endpoint to get meeting processing status."""
        meeting = Meeting.query.get_or_404(meeting_id)
        return jsonify(meeting.to_dict())
    
    @app.route('/export/<meeting_id>', methods=['GET'])
    def export_summary(meeting_id):
        """Export the meeting summary as a text file."""
        meeting = Meeting.query.get_or_404(meeting_id)
        if not meeting.processed or meeting.error:
            flash('Meeting processing is not complete', 'warning')
            return redirect(url_for('view_summary', meeting_id=meeting_id))
            
        export_content = f"""
        MEETING SUMMARY: {meeting.title}
        Date: {meeting.created_at.strftime('%Y-%m-%d %H:%M:%S')}

        SUMMARY:
        {meeting.summary}

        DECISIONS:
        {meeting.decisions}

        ACTION ITEMS:
        {meeting.action_items}

        --------------------------------------------------
        Full Transcript:
        {meeting.transcript}
        """
        
        # Create a temporary file for download
        import tempfile
        fd, path = tempfile.mkstemp(suffix='.txt')
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(export_content)
        
        return_data = open(path, 'rb').read()
        os.unlink(path)  # Delete the temp file
        
        # Generate a clean filename
        safe_title = "".join([c for c in meeting.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_title = safe_title.replace(' ', '_')
        download_name = f"{safe_title}_{meeting.created_at.strftime('%Y%m%d')}.txt"
        
        response = app.response_class(
            return_data,
            mimetype='text/plain',
            headers={"Content-Disposition": f"attachment;filename={download_name}"}
        )
        return response
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
