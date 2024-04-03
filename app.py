from flask_cors import CORS
import os
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, abort, session, get_flashed_messages, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import base64
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from moviepy.editor import AudioFileClip, ImageSequenceClip, VideoFileClip, ImageClip, concatenate_videoclips
from moviepy.video.fx.fadein import fadein
from datetime import datetime
from moviepy.video.fx.rotate import rotate
import time
import psycopg2
from psycopg2.extensions import AsIs


app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_COOKIE_SECURE'] = False  # Only for development, set to True for production
app.secret_key = 'your_secret_key_here'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/user'

jwt = JWTManager(app)
connection = psycopg2.connect("postgresql://ananya:VxDI3HTYlVom1wq9KqeAZw@revengers-4079.7s5.aws-ap-south-1.cockroachlabs.cloud:26257/iss_proj?sslmode=require")


# cur=connection.cursor()
# cur.execute("SELECT now()")
# res = cur.fetchall()
# connection.commit()
# print(res)


# Function to execute MySQL queries
def execute_query(query, values=None):
    cursor = connection.cursor()
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    connection.commit()
    cursor.close()
    # connection.close()

# Secret key for session management
app.secret_key = os.urandom(24)

def convertphotoToBinaryData(file_val):
    return file_val.read()

# Function to check if user is logged in
def is_logged_in():
    return 'logged_in' in session
print("hi")
@app.route('/')
def final():
    print("hi")
    return render_template('final.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

# Route for user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user into database
        execute_query("INSERT INTO users (first_name, email, username, user_password) VALUES (%s, %s, %s, %s)", (name, email, username, hashed_password))

        # Redirect to login page
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Fetch form data
        username = request.form['username']
        session['username'] = username
        print("session data: ",session)
        password = request.form['password']

        # Get user by email
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        print(user)
        cursor.close()
        
        if not user:
            # Redirect to a custom template if user account doesn't exist
            return render_template('user_not_found.html')
        
        if(user[3]=="admin"):
                response = make_response(redirect(url_for('admin_page')))

        if user and check_password_hash(user[4], password):
            # Generate JWT token
    
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[3]
            print(session)
            
            if(user[3]=="admin"):
                response = make_response(redirect(url_for('admin_page')))
            else: 
                access_token = create_access_token(identity=username, expires_delta=timedelta(days=7))   
                response = make_response(redirect(url_for('photos', username=username)))
                response.set_cookie('access_token_cookie', value=access_token, max_age=3600, httponly=True)
            return response
        flash("Invalid","error")    
            
            
    return render_template('login.html')

@app.route('/admin')
def admin_page():
    if 'logged_in' in session and session['logged_in'] and session['username'] == "admin":
        cursor = connection.cursor()
        cursor.execute("SELECT username, first_name, email FROM users")
        users = cursor.fetchall()
        cursor.close()
        return render_template('admin.html', users=users)
    else:
        return redirect(url_for('login'))

@app.route('/photos/<username>',  methods=['GET', 'POST'])
@jwt_required()
def photos(username):
    current_user = get_jwt_identity()
    print("Current user:", current_user)
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)  # Return a forbidden error (HTTP status code 403)
    return render_template('photos.html',username=username)
    
@app.route('/recieve', methods=['POST'])
def receive_array():
    print("Receiving files...")
    print(session)
    username = session["username"]
    if 'uploaded_files[]' in request.files:
        files = request.files.getlist('uploaded_files[]')
        print(files)
        for file in files:
            print("File received:", file.filename)
            file_data=convertphotoToBinaryData(file)
            execute_query("INSERT INTO photos (username, filename, photo) VALUES (%s, %s, %s)", (username, file.filename, file_data))
            print("inserted")
        return 'Files received successfully!'
    else:
        print("Gandu kya kiya")
        return 'No files received in the request.'


# @app.route('/photos/<username>')
# def display_photos(username):
#     try:
#         # Fetch photos from the database
#         cursor = db_connection.cursor()
#         cursor.execute("SELECT filename, photo FROM photos WHERE username = %s", (username,))
#         photos = cursor.fetchall()
#         cursor.close()
        
#         # Check if any photos were found
#         if not photos:
#             return 'No photos found for this user.'

#         # Pass the photos to the template
#         return render_template('video.html', username=username, photos=photos)

#     except Exception as e:
#         return f"An error occurred: {str(e)}"
   
    
@app.route('/videos/<username>/<path>', methods=['GET', 'POST'])
@jwt_required()
def re_direct(username , path):
    current_user = get_jwt_identity()
    print("Current user:", current_user)
    print("Username: ",username)
    if current_user != username:
        print("Error: Current user does not match requested user.")
        abort(403)  # Return a forbidden error (HTTP status code 403)
        
    try:
        # Fetch photos from the database for the given username
        cursor = connection.cursor()
        # user_id = session["user_id"]
        # print("Username inside try: ",user_id)
        cursor.execute("SELECT filename, photo FROM photos WHERE username = %s", (username,))
        photos = cursor.fetchall()
        if(photos):
            print("YES mc")
        cursor.close()
        
        modified_photos = []
        print(photos)
        for photo in photos:
            filename = photo[0]
            photo_data = photo[1]
            
            
            photo_base64 = base64.b64encode(photo_data).decode('utf-8')
            modified_photo = {
                    'filename': filename,
                    'photo': photo_base64
                }
            modified_photos.append(modified_photo)
                
        print(modified_photos)
                
        
        timestamp = int(time.time())
# Assign the modified photos list to the template
        return render_template('videos.html', username=username, photos=modified_photos ,path = path, timestamp = timestamp+1)

    except Exception as e:
        return f"An error occurred: {str(e)}"

        

@app.route('/videos')
@jwt_required()
def video():
    access_token_cookie = request.cookies.get('access_token_cookie')
    if access_token_cookie:
        try:
            decoded = decode_token(access_token_cookie)
            username = decoded.get('sub')
            timestamp = int(time.time())
            return redirect(url_for('re_direct', username=username , path='final'))
        except Exception as e:
            print("Error decoding token:", e)

    else:
        # Handle the case when the access token is missing
        return jsonify({'error': 'Access token missing'}), 401

@app.route('/search')
def search_images():
    query = request.args.get('query')
    username = session.get('username')

    if query:
        # Query the database for filenames matching the search query
        cursor = connection.cursor()
        cursor.execute("SELECT filename FROM photos WHERE username = %s AND filename LIKE %s", (username, query + '%'))
        matched_images = [image[0] for image in cursor.fetchall()]
        cursor.close()

        # Return the matched images to the frontend
        return jsonify(success=True, images=matched_images)
    else:
        # Handle empty search query
        return jsonify(success=True, images=[])
  
    
    
@app.route('/save_selected_photos', methods=['POST' , 'GET'])
def save_selected_photos():
    print('**')
    data = request.json
    selected_filenames = data.get('filenames', [])
    print("Selected filenames:", selected_filenames)
    # print(session)
    username=session["username"]
    # Now you can process the selected filenames as needed
    # 'Selected filenames received successfully!'

    def create_video(list ):

    # Connect to MySQL database
        # connection = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     password="password",
        #     database="iss_proj"
        # )
        cursor = connection.cursor()

        # Initialize video writer
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # video_out = cv2.VideoWriter('output_video.mp4', fourcc, 1, (640, 480))  # Adjust frame size as needed //
        images = []
        
        # Query to select images from the database
        for i in list:
            query = "SELECT photo FROM photos WHERE filename=%s"

            # Execute the query
            cursor.execute(query,(i,))

        # Iterate over the results and create video
            for photo in cursor.fetchall():
                # Read image from bytes
                image = Image.open(BytesIO(photo[0]))

                # Convert image to OpenCV format
                # image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # # Resize image if needed
                # image = cv2.resize(image, (640, 480)) 
                # # Adjust dimensions as needed
                image = image.resize((640, 480))

                # Convert image to numpy array and add to list
                images.append(np.array(image))
                # Write frame to video
                # video_out.write(image)

        # Release video writer and close MySQL connection
        # video_out.release()
        clip = ImageSequenceClip(images, fps=1)  # Adjust fps as needed

        # Write video to file
        clip.write_videofile('static/final.mp4')

        with open('output_video.mp4', 'rb') as f:
            video_blob = f.read()

        # Insert the video into the database
        session['video_timestamp']= int(time.time())
        timestamp=session['video_timestamp']
        insert_query = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, f'output_video_{timestamp}.mp4', video_blob))

        video_name = f"output_video_{timestamp}.mp4"
        print(video_name)
        session['video_name']=video_name
        # Commit the transaction
        connection.commit()
        # video_id = cursor.lastrowid
        # print("Video ID:", video_id)
        # connecti/on.close()

        print("Video created successfully.")
        return "Video created successfully."
    create_video(selected_filenames)
    # return "video created"
    # return redirect(url_for('display_video', video_id=username))
    return redirect(url_for('re_direct', username=username , path='final'))
    

# @app.route('/display_video/<string:video_id>')
# def display_video(video_id):
#     # Connect to the database
#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Navishaa@05",
#         database="login"
#     )
#     cursor = connection.cursor()

#     # Fetch the video from the database
#     cursor.execute("SELECT video FROM videos WHERE username = %s", (video_id,))
#     video = cursor.fetchone()[0]
#     # print(video)

#     # Close the database connection
#     connection.close()

#     # Convert the video data to a base64 string
#     video_base64 = base64.b64encode(video).decode('utf-8')
#     print(type(video_base64))
#     # print("Base64-encoded video:", video_base64)
#     # Render the template with the video data
#     print("done ")
#     # response = Response(video, mimetype='video/mp4')

#     # Return the response
#     # return response

#     return render_template('videos.html', video_data=video_base64.encode('utf-8'))

@app.route('/display/<video_id>' ,  methods=['POST' , 'GET'])
def display_video(video_id):
    
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="password",
    #     database="iss_proj"
    # )
    
    cursor = connection.cursor()
    # cursor.execute("SELECT video FROM videos WHERE username = %s", (video_id,))
    # video = (cursor.fetchone()[0])
    # connection.close()
    
    if request.method == 'POST':
        
        # with open("retrieved_video.mp4", "wb") as f:
        #     f.write(video)
        nav = request.form['song']
        if nav != "No":
            video_clip = VideoFileClip("static/final.mp4")
            audio_clip = AudioFileClip(f"static/{nav}.mp3")

            audio_clip = audio_clip.subclip(0, video_clip.duration)

            final_clip = video_clip.set_audio(audio_clip)

            final_clip.write_videofile("static/final.mp4")
        # return render_template('display.html', video_id=video_id )
        return redirect(url_for('re_direct', username=video_id , path='final'))

    # with open("static/final.mp4", "wb") as f:
    #     f.write(video)
    # return render_template('display.html', video_id=video_id )
    return redirect(url_for('re_direct', username=video_id , path='final'))

@app.route('/add_transition', methods=['GET'])
def add_transition():
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="Nidhi&Kriti1911",
    #     database="iss_proj"
    # )
    cursor = connection.cursor()
    username=session["username"]
    video_in_database=session['video_name']
    video_timestamp = session['video_timestamp']

    print("video in database",video_in_database)
    print("video timestamp",video_timestamp)

    # Query to select video from the database
    query = "SELECT video FROM videos WHERE filename = %s"

    # Execute the query
    cursor.execute(query, (video_in_database,))

    # Fetch the video as a single blob
    # print(mycursor.fetchone())
    video_blob = (cursor.fetchone()[0])

    # Write the video blob to a temporary file
    with open("temp_video.mp4", "wb") as file:
        file.write(video_blob)

    # Close MySQL connection
    # connection.close()

    # Read the temporary video file as a VideoFileClip
    video_clip = VideoFileClip(f"static/{video_in_database}")

    # Break down the video into frames
    frames = [frame for frame in video_clip.iter_frames()]

    # Convert frames to ImageClips with transitions
    clips_with_transitions = []
    for frame in frames:
        # Convert frame to ImageClip with transition and add to list
        clip = ImageClip(np.array(frame), duration=1).fx(fadein, duration=1)  # Adjust duration as needed

        clips_with_transitions.append(clip)

    # Concatenate the clips with transitions
    final_clip = concatenate_videoclips(clips_with_transitions, method="compose")

    # Set fps for the final_clip (assuming 24 fps for example)
    final_clip.fps = 24  # You can adjust the fps as needed

    # Write video with transitions to file
    final_clip.write_videofile(f"static/output_video_with_fade_{video_timestamp}.mp4")  # Adjust codec as needed

    with open(f"static/output_video_with_fade_{video_timestamp}.mp4","rb") as ofile:
        video_blob = ofile.read()
        query2 = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
        cursor.execute(query2, (username, f"static/output_video_with_fade_{video_timestamp}.mp4", video_blob))

    video_in_database = f"output_video_with_fade_{video_timestamp}.mp4"

    print("Video with transitions created successfully.")
    return jsonify({'video_url': url_for('static', filename=f"output_video_with_fade_{video_timestamp}.mp4")})


@app.route('/add_transition_rotate', methods=['GET'])
def add_transition_rotate():
    # Connect to MySQL database
    # connection = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="Nidhi&Kriti1911",
    #     database="iss_proj"
    # )
    # cursor = connection.cursor()

    username=session["username"]
    video_in_database=session['video_name']
    video_timestamp = session['video_timestamp']

    # Query to select video from the database
    query = "SELECT video FROM videos WHERE filename = %s"

    cursor = connection.cursor()
    # Execute the query
    cursor.execute(query, (video_in_database,))

    # Fetch the video as a single blob
    video_blob = cursor.fetchone()[0]

    # Write the video blob to a temporary file
    with open("temp_video.mp4", "wb") as file:
        file.write(video_blob)

    # Close MySQL connection
    # connection.close()

    # Read the temporary video file as a VideoFileClip
    video_clip = VideoFileClip("temp_video.mp4")

    # Break down the video into frames
    frames = [frame for frame in video_clip.iter_frames()]

    # Calculate duration for each frame
    frame_duration = video_clip.duration / len(frames)

    # Convert frames to ImageClips with transitions
    clips_with_transitions = []
    for i, frame in enumerate(frames):
        # Convert frame to ImageClip
        frame_clip = ImageClip(frame, duration=frame_duration)
        # Rotate frame into view over the duration of the clip
        clip = rotate(frame_clip, lambda t: 360 * t / frame_duration, unit='deg')  # Rotate frame from 0 to 360 degrees over the duration of the frame
        clips_with_transitions.append(clip)

    # Concatenate the clips with transitions
    final_clip = concatenate_videoclips(clips_with_transitions, method="compose")

    # Set fps for the final_clip (assuming 24 fps for example)
    final_clip.fps = 24  # You can adjust the fps as needed

    # Write video with transitions to file
    final_clip.write_videofile(f"static/output_video_with_rotation_transition{video_timestamp}.mp4")  # Adjust codec as needed
    
    with open(f"static/output_video_with_rotation_transition{video_timestamp}.mp4","rb") as ofile:
        video_blob = ofile.read()
        query2 = "INSERT INTO videos (username, filename, video) VALUES (%s, %s, %s)"
        cursor.execute(query2, (username, f"static/output_video_with_rotation_transition{video_timestamp}.mp4", video_blob))

    video_in_database = f"output_video_with_rotation_transition{video_timestamp}.mp4"

    print("Video with rotation transition created successfully.")
    return jsonify({'video_url': url_for('static', filename=f"output_video_with_rotation_transition{video_timestamp}.mp4")})

    
# @app.route('/videos/<path:filename>')
# def serve_video(filename):
#     return send_from_directory('.', filename)



if __name__ == '__main__':
    app.run(debug=True)
