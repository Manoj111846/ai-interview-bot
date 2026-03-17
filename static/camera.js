document.addEventListener("DOMContentLoaded", function () {

let video = document.getElementById("camera");
let statusText = document.getElementById("faceStatus");

if (!video) {
    console.log("❌ Video not found");
    return;
}

/* START CAMERA */
navigator.mediaDevices.getUserMedia({ video: true })
.then(function (stream) {

    video.srcObject = stream;
    video.muted = true;

    video.onloadedmetadata = function () {
        video.play();
        console.log("✅ Camera started");

        /* FACE DETECTION LOOP */
        setInterval(function(){

            if(video.videoWidth === 0) return;

            let canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            let ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0);

            let image = canvas.toDataURL("image/jpeg");

            fetch("/detect_face",{
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body: JSON.stringify({image:image})
            })
            .then(res => res.json())
            .then(data => {
                statusText.innerText = data.status;
            })
            .catch(err => {
                console.log("Face error:", err);
            });

        },3000);

    };

})
.catch(function (error) {

    console.log("❌ Camera error:", error);
    statusText.innerText = "Camera permission denied";

});

});