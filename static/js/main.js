const webcam = document.getElementById('webcam');
const preview = document.getElementById('preview');
const captureBtn = document.getElementById('captureBtn');
const placeholder = document.getElementById('placeholder');
const canvas = document.createElement('canvas');
let currentStream = null;

async function startCamera() {
    try {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }
        
        currentStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: "environment",
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        });
        
        webcam.srcObject = currentStream;
        webcam.onloadedmetadata = () => {
            webcam.play();
            webcam.classList.remove('hidden');
            preview.classList.add('hidden');
            placeholder.classList.add('hidden');
            captureBtn.classList.remove('hidden');
        };
    } catch (e) {
        console.error(e);
        alert("Gagal mengakses kamera. Pastikan izin diberikan.");
    }
}

async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Tampilkan loading preview
    const reader = new FileReader();
    reader.onload = (event) => {
        preview.src = event.target.result;
        preview.classList.remove('hidden');
        webcam.classList.add('hidden');
        placeholder.classList.add('hidden');
        captureBtn.classList.add('hidden');
    };
    reader.readAsDataURL(file);
    
    // Langsung kirim ke server
    sendToServer(file);
}

async function captureImage() {
    if (!currentStream) return;

    // Set ukuran canvas sesuai resolusi video asli agar kotak tidak meleset
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
    
    // Ubah ke Blob lalu kirim
    canvas.toBlob((blob) => {
        const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
        sendToServer(file);
    }, 'image/jpeg', 0.95);
}

async function sendToServer(file) {
    // UI Feedback
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('result-section')?.classList.remove('hidden');
    document.getElementById('result-content').classList.add('hidden');

    const body = new FormData();
    body.append('file', file);
    
    try {
        const res = await fetch('/predict', { method: 'POST', body });
        const data = await res.json();
        
        document.getElementById('loading').classList.add('hidden');
        
        // Tampilkan gambar hasil deteksi (yang ada bounding boxnya)
        if (data.img) {
            preview.src = data.img;
            preview.classList.remove('hidden');
            webcam.classList.add('hidden');
        }

        if(data.success) {
            document.getElementById('result-content').classList.remove('hidden');
            document.getElementById('resLabel').innerText = data.info.title;
            document.getElementById('resLabel').style.color = data.info.color;
            document.getElementById('resConf').innerText = data.conf;
            document.getElementById('resDesc').innerText = data.info.desc;
            document.getElementById('resAction').innerText = data.info.action;
            document.getElementById('binText').innerText = data.info.bin_text;
            document.getElementById('binImg').src = data.info.bin_img;

        } else {
            alert("Tidak ada objek terdeteksi.");
        }
    } catch (err) {
        console.error(err);
        document.getElementById('loading').classList.add('hidden');
    }
}