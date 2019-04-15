//============== New Updated Code ================
navigator.mediaDevices.getUserMedia({
    audio: isEdge ? true : {
        echoCancellation: false
    }
}).catch(function(error) {
    var res = confirm("Device / browser doesn't support this feature. Press OK to Answer in Text & Cancel to go back");
    if (res == true) {window.location = window.location.href.replace('/audio', '/text');}
    else { window.location = '/topic/' + window.location.href.split('/')[4] + '/';}
});

var audio = document.querySelector('audio');
function captureMicrophone(callback) {
    btnReleaseMicrophone.disabled = false;
    if(microphone) {
        callback(microphone);
        return;
    }
    if(typeof navigator.mediaDevices === 'undefined' || !navigator.mediaDevices.getUserMedia) {
        alert('This browser does not supports WebRTC getUserMedia API.');
        if(!!navigator.getUserMedia) {
            alert('This browser seems supporting deprecated getUserMedia API.');
        }
    }
}

function replaceAudio(src) {
    // var newAudio = document.createElement('audio');
    // newAudio.controls = true;
    // newAudio.autoplay = true;

    // if(src) {
    //     newAudio.src = src;
    // }
    
    // var parentNode = audio.parentNode;
    // parentNode.innerHTML = '';
    // parentNode.appendChild(newAudio);

    // audio = newAudio;
}

function stopRecordingCallback() {
    replaceAudio(URL.createObjectURL(recorder.getBlob()));

    // btnStartRecording.disabled = false;

    setTimeout(function() {
        if(!audio.paused) return;

        setTimeout(function() {
            if(!audio.paused) return;
            audio.play();
        }, 1024);
        
        audio.play();
    }, 300);

    audio.play();

    btnDownloadRecording.disabled = false;

    if(isSafari) {
        click(btnReleaseMicrophone);
    }

    if(!recorder || !recorder.getBlob()) return;

    var blob = recorder.getBlob();
    var file = new File([blob], getFileName('mp3'), {
        type: 'audio/mp3'
    });
    SaveToDisk(file, getFileName('mp3'));

}

var isEdge = navigator.userAgent.indexOf('Edge') !== -1 && (!!navigator.msSaveOrOpenBlob || !!navigator.msSaveBlob);
var isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

var recorder; // globally accessible
var microphone;

var btnStartRecording = document.getElementById('btn-start-recording');
var btnStopRecording = document.getElementById('btn-stop-recording');
var btnReleaseMicrophone = document.querySelector('#btn-release-microphone');
var btnDownloadRecording = document.getElementById('btn-download-recording');

btnStartRecording.onclick = function() {
  $('.record_info').html('Recording in progress...');
    this.disabled = true;
    this.style.border = '';
    this.style.fontSize = '';

    if (!microphone) {
        captureMicrophone(function(mic) {
            microphone = mic;

            if(isSafari) {
                replaceAudio();

                audio.muted = true;
                audio.srcObject = microphone;

                btnStartRecording.disabled = false;
                btnStartRecording.style.border = '1px solid red';
                btnStartRecording.style.fontSize = '150%';
                click(btnStartRecording);
                return;
            }

            click(btnStartRecording);
        });
        return;
    }

    replaceAudio();

    audio.muted = true;
    audio.srcObject = microphone;

    var options = {
        type: 'audio',
        numberOfAudioChannels: isEdge ? 1 : 2,
        checkForInactiveTracks: true,
        bufferSize: 44100
    };

    if(isSafari || isEdge) {
        options.recorderType = StereoAudioRecorder;
    }

    if(navigator.platform && navigator.platform.toString().toLowerCase().indexOf('win') === -1) {
        options.sampleRate = 48000; // or 44100 or remove this line for default
    }

    if(isSafari) {
        options.sampleRate = 44100;
        options.bufferSize = 4096;
        options.numberOfAudioChannels = 2;
    }

    if(recorder) {
        recorder.destroy();
        recorder = null;
    }

    recorder = RecordRTC(microphone, options);

    recorder.startRecording();

    btnStopRecording.disabled = false;
    btnDownloadRecording.disabled = true;
};


btnStopRecording.onclick = function() {
    this.disabled = true;
    // $('#btn-start-recording').attr('disabled', true);
    $('.record_info').html('Please wait... <br>uploading file!');
    recorder.stopRecording(stopRecordingCallback);
};

btnReleaseMicrophone.onclick = function() {
    this.disabled = true;
    btnStartRecording.disabled = false;
    if(microphone) {
        microphone.stop();
        microphone = null;
    }
    if(recorder) {
        // click(btnStopRecording);
    }
};

btnDownloadRecording.onclick = function() {
    this.disabled = true;
    if(!recorder || !recorder.getBlob()) return;

    var blob = recorder.getBlob();
    var file = new File([blob], getFileName('mp3'), {
        type: 'audio/mp3'
    });
    SaveToDisk(file, getFileName('mp3'));
};

function click(el) {
    el.disabled = false; // make sure that element is not disabled
    var evt = document.createEvent('Event');
    evt.initEvent('click', true, true);
    el.dispatchEvent(evt);
}

function getRandomString() {
    if (window.crypto && window.crypto.getRandomValues && navigator.userAgent.indexOf('Safari') === -1) {
        var a = window.crypto.getRandomValues(new Uint32Array(3)),
            token = '';
        for (var i = 0, l = a.length; i < l; i++) {
            token += a[i].toString(36);
        }
        return token;
    } else {
        return (Math.random() * new Date().getTime()).toString(36).replace(/\./g, '');
    }
}

function getFileName(fileExtension) {
    var d = new Date();
    var year = d.getFullYear();
    var month = d.getMonth();
    var date = d.getDate();
    return 'RecordRTC-' + year + month + date + '-' + getRandomString() + '.' + fileExtension;
}

function SaveToDisk(File, fileName) {debugger;
  // for non-IE
  if (!window.ActiveXObject) {
    formData = new FormData();
    formData.append('files_varname', 'file');
    formData.append('file', File);
    formData.append('file_dest', "video.webm");
    var xhr = new XMLHttpRequest();
    xhr.open('POST', "https://www.careeranna.com/demo/getAudioData", true);
    xhr.onload = function (e) {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          $("#id_comment").html(xhr.responseText);
          $('[name="question_video"]').val('');
          $('[name="question_audio"]').val(xhr.responseText);
          $('#btnPublish').show();
          $('.record_info').html('');
          $('.modal-backdrop').hide();
          $('.btnCloseAudio').click();
          btnStartRecording.disabled = false;
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

  // for IE
  else if (!!window.ActiveXObject && document.execCommand) {
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
          $("#id_comment").html(xhr.responseText);
          $('[name="question_video"]').val('');
          $('[name="question_audio"]').val(xhr.responseText);
          $('#btnPublish').show();
          $('.record_info').html('');
          $('.modal-backdrop').hide();
          $('.btnCloseAudio').click();
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
}
//====================End=========================  
