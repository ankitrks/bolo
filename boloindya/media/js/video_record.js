navigator.mediaDevices.getUserMedia({
    audio: isEdge ? true : {
        echoCancellation: false
    }
}).catch(function(error) {
    $('#upload').hide();
    var res = confirm("Device / browser doesn't support this feature. Press OK to Answer in Text & Cancel to go back");
    if (res == true) {window.location = window.location.href.replace('/video', '/text');}
    else { window.location = '/topic/' + window.location.href.split('/')[4] + '/';}
});

var mediaSource = new MediaSource();
mediaSource.addEventListener('sourceopen', handleSourceOpen, false);
var mediaRecorder;
var recordedBlobs;
var sourceBuffer;
var gumVideo = document.querySelector('video#gum');
var recordedVideo = document.querySelector('video#recorded');
var recordButton = document.querySelector('button#recordVid');
var playButton = document.querySelector('button#play');
var downloadButton = document.querySelector('button#download');
recordButton.onclick = toggleRecording;
playButton.onclick = play;
downloadButton.onclick = download;
var constraints = {
  audio: true,
  video: true
};

// navigator.mediaDevices.getUserMedia(constraints).then(
//   successCallback
// ).catch(function(error) {
//     alert("Device / browser doesn't support this feature.");
//     // console.error(error);
// });

function successCallback(stream) {
  // console.log('getUserMedia() got stream: ', stream);
  window.stream = stream;
  gumVideo.srcObject = stream;
}
function errorCallback(error) {
  // console.log('navigator.getUserMedia error: ', error);
}
function handleSourceOpen(event) {
  // console.log('MediaSource opened');
  sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"');
  // console.log('Source buffer: ', sourceBuffer);
}
function handleDataAvailable(event) {
  if (event.data && event.data.size > 0) {
    recordedBlobs.push(event.data);
  }
}
function handleStop(event) {
  // console.log('Recorder stopped: ', event);
}
function toggleRecording() {
  if (recordButton.textContent === 'Start Recording') {
    $('#btnPublish').hide()
    $('.record_info').html('Recording in progress...')
    startRecordingVideo();
  } else {
    stopRecordingVideo();
    recordButton.textContent = 'Start Recording';
    recordButton.disabled = true;
    $('.record_info').html('Please wait... <br>uploading file! ')
    playButton.disabled = false;
    downloadButton.disabled = false;
  }
}
// The nested try blocks will be simplified when Chrome 47 moves to Stable
function startRecordingVideo() {
  var options = {mimeType: 'video/webm', bitsPerSecond: 1000000};
  recordedBlobs = [];
  try {
    mediaRecorder = new MediaRecorder(window.stream, options);
  } catch (e0) {
    // console.log('Unable to create MediaRecorder with options Object: ', e0);
    try {
      options = {mimeType: 'video/webm,codecs=vp9', bitsPerSecond: 1000000};
      mediaRecorder = new MediaRecorder(window.stream, options);
    } catch (e1) {
      // console.log('Unable to create MediaRecorder with options Object: ', e1);
      try {
        options = 'video/vp8'; // Chrome 47
        mediaRecorder = new MediaRecorder(window.stream, options);
      } catch (e2) {
        alert('MediaRecorder is not supported by this browser.\n\n' +
            'Try Firefox 29 or later, or Chrome 47 or later, with Enable experimental Web Platform features enabled from chrome://flags.');
        console.error('Exception while creating MediaRecorder:', e2);
        return;
      }
    }
  }
  // console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
  recordButton.textContent = 'Stop Recording';
  playButton.disabled = true;
  downloadButton.disabled = true;
  mediaRecorder.onstop = handleStop;
  mediaRecorder.ondataavailable = handleDataAvailable;
  mediaRecorder.start(10); // collect 10ms of data
  // console.log('MediaRecorder started', mediaRecorder);
}
function stopRecordingVideo() {
  mediaRecorder.stop();
  // console.log('Recorded Blobs: ', recordedBlobs);
var blob = new Blob(recordedBlobs, {type: 'video/webm'});
  //postVideoToServer(recordedBlobs);
  recordedVideo.controls = true;
  sendVideoData(blob);
}
function sendVideoData(File) {
    // console.log(File);
    formData = new FormData();
    formData.append('files_varname', 'file');
    formData.append('file', File);
    formData.append('file_dest', "video.webm");
    var xhr = new XMLHttpRequest();
    //xhr.setRequestHeader("Content-Type","multipart/form-data");
    xhr.open('POST', "https://www.careeranna.com/demo/getAudioData", true);
    xhr.onload = function (e) {
    if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          // console.log("success");
          // console.log(xhr.responseText);
          $("#id_comment").html(xhr.responseText);
          $('[name="question_audio"]').val('');
          $('[name="question_video"]').val(xhr.responseText);
          $('#btnPublish').show()
          $('.record_info').html('')
          $('.modal-backdrop, #myModalVideo').hide();
          recordButton.disabled = false;
        } else {
          console.error(xhr.statusText);
        }
      }
    };
    xhr.onerror = function (e) {
      console.error(xhr.statusText);
    };
    xhr.send(formData); 
}
function play() {
  var superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
  recordedVideo.src = window.URL.createObjectURL(superBuffer);
}