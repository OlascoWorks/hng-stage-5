## API DOCUMEMTATION 📝

### Detailed guide on how to use API

This is a backend project for a screen recording chrome extension built on the python framework - [Flask](https://palletsprojects.com/p/flask/) and hosted on [render](https://render.com). that is also hosted remotely on render to allow for manipulation of a Person table by performing CRUD operations on it

## The process

> ### Starting a recording
  - **Info** This initialises the recording process and allows for chunks of data to be received in the chunk uploading endpoint
  - **Method** -  GET
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/start-recording
  - **Body** -
    ```
    {
      "client-id": <string> // unique id designated to a user in the frontend. This should be stored in a secure lace like the user's local storage as it would be used for user-related tasks like starting and viewing recordings
    }
    ```
  - **Response** -  If no errors are encountered, a fresh recording session is created and a unique video id is sent back
    ```
    {
      "status": "success"
      "message": "successfully started recording",
      "video-id": <string>
    }
    ```


> ### Uploading chunks
  - **Info** This receives data of a recording in chunks and appends them until the recording process is complete
  - **Method** -  GET
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/upload-chunk
  - **Body** -
    ```
    {
      "video-id": <string>, // a unique id that is received upon starting a new recording
      "chunk-id": <string>, // a sequential id assigned from the frontend to chunks to ensure they are in order
      "chunk-data": <string> // the data contained in the chunk i.e the chunk itself
    }
    ```
  - **Response** -  If a recording with the provided id has started and the chunk fits the order, a success response like this is received
    ```
    {
      "status": "success",
      "message": f"succesfully uploaded chunk number {chunk_id} to video with id {video_id}"
    }
    ```


> ### Stopping a recording
  - **Info** This stops the chunk receiving process and starts the process of joining the chunks together to store the recorded video and create a transcript. NOTE‼️ This endpoint does not automatically begin the final process; a seperate request needs to be send to the '/api/video/save' endpoint after stopping recording.
  - **Method** -  GET
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/stop-recording
  - **Body** -
    ```
    {
      "video-id": <string>
    }
    ```
  - **Response** -  If a video with the provided id is in a recording state, the recording process is stopped and a response like this is received
    ```
    {
      "status": "success",
      "message": "successfully stopped recording"
    }
    ```


> ### Saving a recording
  - **Info** This compiles all the received chunks into a video and also transcribes said video with timestamps
  - **Method** -  POST
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/video/save
  - **Body** -
    ```
    {
      "video-id": <string>,
      "client-id": <string>
    }
    ```
  - **Response** -  If a client with the provided id exists and a recording with provided id is valid(has uncompiled chunks), a success response like this is received
    ```
    {
      "status": "success",
      "message": "successfully saved recording",
      "file": send_from_directory(f'/videos/{client_id}', unique_filename), // the actual video file
      "url": '/videos/{client_id}/{unique_filename}', // url to video. NB:should be appended to root directory
      "transcript": <json>, // transcript texts
      "timestamps": <json> // timestamps
    }
    ```



> ### Getting recordings
  - **Info** This returns a list of recorded videos by user with provided id
  - **Method** -  GET
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/videos/<client_id:string>
  - **Response** -  If a client with the provided id exists, a list of all their recordings are returned


> ### Destroying a recording
  - **Info** This endpoint should be used in a situation when a user stops recording and discards the recording
  - **Method** -  GET
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/destroy-recording
  - **Body** -
    ```
    {
      "video-id": <string>
    }
    ```
  - **Response** -  If a recording with the provided id exists and valid(has uncompiled chunks), the chunks are discarded and a success response like this is received
    ```
    {
      "status": "success",
      "message": "successfully destroyed recording with id {video_id} and all files associated have been deleted"
    }
    ```


> ### Checking recording status
  - **Info** This is used to check the status of an ongoing recording
  - **Method** -  GET
  - **Endpoint** -  https://hng-stage5-sam.onrender.com/api/video/save
  - **Body** -
    ```
    {
      "video-id": <string>
    }
    ```
  - **Response** -  If a recording with the provided id exists and a recording with provided id is valid(has at least begun), a success response like this is received
    ```
    {
      "status": "success",
      "recording-status": status
    }
    ```
  - **The following are all the posiible statuses**
    ```
    "STARTED RECORDING":  A recording with that id has been started but no chunks have been received,
    "UPLOADING":  A recording with that id has been started at least 1 chunk has been received,
    "PROCESSING":  A recording with that id has been stopped and is being processed and transcribed
    ``` 

    

> ## Request/Response Formats

- **Request Format**: All requests should be in JSON format. The content type of the request should be set to `application/json`.

- **Response Format**: Responses are returned in JSON format and include relevant information or error messages in a case of failure. They also include a status response which could be eithr 'fail' or 'success'. Most successful responses include a `"message"` field for context.
