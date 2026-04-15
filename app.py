import cv2
import base64
import numpy as np
from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# =====================
# LOAD MODEL KLASIFIKASI (HASIL TRAININGMU)
# =====================
model = YOLO("best.pt")  
# ⬆️ GANTI sesuai path model hasil trainingmu

# =====================
# LABEL & INFO SAMPAH
# =====================
WASTE_MAP = {
    "organic": {
        "title": "Sampah Organik",
        "color": "#10B981",
        "desc": "Sampah yang berasal dari bahan alami dan mudah terurai, seperti sisa makanan dan tumbuhan.",
        "action": "Buang ke tong sampah HIJAU untuk proses pengomposan.",
        "bin_text": "Buang ke Tong Sampah Hijau",
        "bin_color": "Hijau",
        "bin_img": "/static/img/1.png"
    },
    "inorganic": {
        "title": "Sampah Anorganik",
        "color": "#3B82F6",
        "desc": "Sampah yang berasal dari bahan non-alami dan sulit terurai, seperti plastik, kertas, dan logam.",
        "action": "Buang ke tong sampah BIRU untuk didaur ulang.",
        "bin_text": "Buang ke Tong Sampah Biru",
        "bin_color": "Biru",
        "bin_img": "/static/img/3.png"
    },
    "B3": {
        "title": "Sampah Berbahaya (B3)",
        "color": "#EF4444",
        "desc": "Sampah yang dapat mengandung zat berbahaya, seperti baterai, popok, pembalut, dan obat-obatan.",
        "action": "Buang ke tong sampah MERAH khusus sampah B3.",
        "bin_text": "Buang ke Tong Sampah Merah (B3)",
        "bin_color": "Merah",
        "bin_img": "/static/img/2.png"
    }
}

# =====================
# ROUTE HALAMAN UTAMA
# =====================
@app.route("/")
def index():
    return render_template("index.html")

# =====================
# ROUTE PREDIKSI KLASIFIKASI
# =====================
@app.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return jsonify({"success": False, "msg": "File tidak ditemukan."})

    # =====================
    # BACA GAMBAR
    # =====================
    img_bytes = request.files["file"].read()
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"success": False, "msg": "Gagal membaca gambar."})

    # =====================
    # PREDIKSI KLASIFIKASI
    # =====================
    results = model.predict(source=img, imgsz=224, verbose=False)
    r = results[0]

    if r.probs is None:
        return jsonify({"success": False, "msg": "Prediksi gagal."})

    # Ambil probabilitas
    probs = r.probs.data.cpu().numpy()
    cls_id = int(np.argmax(probs))
    conf = float(probs[cls_id])
    label = r.names[cls_id]

    if label not in WASTE_MAP:
        return jsonify({"success": False, "msg": f"Label '{label}' tidak dikenali."})

    # =====================
    # Encode gambar asli (tanpa bounding box)
    # =====================
    _, buffer = cv2.imencode(".jpg", img)
    img_base64 = base64.b64encode(buffer).decode()

    return jsonify({
        "success": True,
        "info": WASTE_MAP[label],
        "conf": f"{conf*100:.1f}%",
        "img": f"data:image/jpeg;base64,{img_base64}"
    })

# =====================
# RUN FLASK
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
