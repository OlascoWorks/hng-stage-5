from flask import Flask, request, jsonify, send_from_directory
import os, uuid, base64
import whisper

app = Flask(__name__)

@app.route('/')
def home():
    return "app is running..."

@app.route('/api/video/save', methods={'POST'})
def save_video():
    if request.is_json:
        try:
            video_id = request.json["video-id"]
            client_id = request.json["client-id"]
            unique_filename = f"video-{video_id}.webm"

            # write video data into video file and save the video to the local disk
            with open(f'/videos/{client_id}/unique_filename', 'wb') as video_file, open(f'{video_id}.bin', '+br') as binary_file:
                video_data = binary_file.read()
                video_file.write(video_data)

            # delete all associated files deleted for the recording
            os.remove(f'{video_id}-chunk.txt')
            os.remove(f'{video_id}-status.txt')
            os.remove(f'{video_id}.bin')

            # start transcription process
            model = whisper.load_model("base")
            audio = open(f'/videos/{client_id}/unique_filename', 'rb')
            result = model.transcribe(audio)

            return jsonify({
                "status": "success",
                "message": "successfully saved recording",
                "file": send_from_directory(f'/videos/{client_id}', unique_filename),
                "url": '/videos/{client_id}/{unique_filename}',
                "transcript": result.text,
                "timestamps": result["segments"]
            })
        except Exception as e:
            return jsonify({
                "message": "error saving video",
                "error": f"{e}",
                "hint": "you either provided no video data or data is invalid"
            }), 300
    else:
        return jsonify({
            "message": "Please provide your request in json format"
        }), 300


@app.route('/api/videos/<client_id>')
def get_videos(client_id):
    if request.is_json():
        try:
            video_files = os.listdir(f'/videos/{client_id}')

            return video_files
        except:
            return jsonify({
                "status": "fail",
                "message": f"could not get recordings. No user with id {client_id} found"
            })
    else:
        return jsonify({
            "status": "fail",
            "message": "please provide your request in a json format"
        })


@app.route('/api/start-recording')
def start_recording():
    if request.is_json():
        client_id = request.json["client-id"]
        video_id = str(uuid.uuid4())[:18]
        save_directory = f'videos/user-{client_id}'

        os.makedirs(save_directory, exist_ok=True)

        try:
            with open(f'{video_id}-status.txt', 'w') as file1, open(f'{video_id}.bin', 'w') as file2:
                file1.write("STARTED RECORDING")
        except Exception as e:
            return jsonify({
                "status": "fail",
                "message": "failed to start recording",
                "error_message": f"{e}"
            })


        return jsonify({
            "status": "success",
            "message": "successfully started recording...",
            "video-id": video_id
        })
    else:
        return jsonify({
            "status": "fail",
            "message": "please provide your request in a json format"
        })


@app.route('/api/stop-recording')
def stop_recording():
    if request.is_json():
        video_id = request.json["video-id"]
        try:
            with open(f'{video_id}-status.txt', 'w') as file:
                file.write("PROCESSING...")
        except FileNotFoundError:
            return jsonify({
                "status": "fail",
                "message": "failed to stop recording as no recording is in progress"
            })
        
        return jsonify({
            "status": "success",
            "message": "successfully stopped recording"
        })
    else:
        return jsonify({
            "status": "fail",
            "message": "please provide your request in a json format"
        })


@app.route('/api/upload-chunk')
def upload():
    if request.is_json():
        video_id = request.json["video-id"]
        chunk_id = request.json["chunk-id"]
        chunk_data = request.json["chunk-data"]
        try:
            with open(f'{video_id}-status.txt', 'w') as file:
                file.write("UPLOADING...")
        except Exception as e:
            return jsonify({
                "status": "fail",
                "message": "failed to upload chunk because there is no recording in progress",
                "error_message": f"{e}"
            })

        with open(f'{video_id}-chunk.txt', 'w+') as file:
            id = file.read()
            if chunk_id != id+1:
                return jsonify({
                    "status": "fail",
                    "message": "received chunk does not fit current order. Please upload chunks in sequence"
                })
            
            file.write(chunk_id)

        with open(f'{video_id}.bin', 'a') as file:
            file.write(chunk_data)
        
        return jsonify({
            "status": "success",
            "message": f"succesfully uploaded chunk number {chunk_id} to video with id {video_id}"
        })
    else:
        return jsonify({
            "status": "fail",
            "message": "please provide your request in a json format"
        })


@app.route('/api/destroy-recording')
def destroy_recording():
    if request.is_json():
        video_id = request.json["video-id"]
        try:
            os.remove(f'{video_id}-chunk.txt')
            os.remove(f'{video_id}-status.txt')
            os.remove(f'{video_id}.bin')

            return jsonify({
                "status": "success",
                "message": f"successfully destroyed recording with id {video_id} and all files associated have been deleted"
            })
        except Exception as e:
            return jsonify({
                "status": "fail",
                "message": f"failed to destroy recording. no recording with id {video_id} was found",
                "error_message": f"{e}"
            })
    else:
        return jsonify({
            "status": "fail",
            "message": "please provide your request in a json format"
        })


@app.route('/api/video/status')
def check_status():
    if request.is_json():
        video_id = request.json["video-id"]
        try:
            with open(f'{video_id}-status', 'r') as file:
                status = file.read()
        except FileNotFoundError:
            return jsonify({
                "status": "fail",
                "message": "failed to check status because there is no recrding in progress"
            })
        except Exception as e:
            return jsonify({
                "status": "fail",
                "message": "failed to check status",
                "error_message": f"{e}"
            })

        return jsonify({
            "status": "success",
            "recording-status": status
        })
    else:
        return jsonify({
            "status": "fail",
            "message": "please provide your request in a json format"
        })


if __name__ == '__main__':
    app.config.from_pyfile('config.py')
    app.run(debug=True)