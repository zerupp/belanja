import streamlit as st
import streamlit.components.v1 as components

# Set up page config
st.set_page_config(page_title="For Anis ❤️", layout="centered")

# Sembunyikan header/footer asal Streamlit supaya nampak kemas
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Kod HTML, CSS & JavaScript
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>For Anis</title>
    <!-- Library untuk efek bunga api -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh;
            margin: 0;
            background-color: #ffe6e6;
            font-family: 'Arial', sans-serif;
            overflow: hidden; /* Supaya tak ada scrollbar bila butang lari */
        }
        .container {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            position: relative;
            width: 90%;
            max-width: 500px;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        h1 {
            color: #ff4d4d;
            font-size: 28px;
            margin-bottom: 30px;
        }
        .btn {
            background-color: #ff4d4d;
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            margin: 10px;
            transition: 0.2s;
            box-shadow: 0 4px 10px rgba(255, 77, 77, 0.4);
        }
        .btn:hover {
            background-color: #ff1a1a;
            transform: scale(1.05);
        }
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            width: 100%;
        }
        /* Sembunyikan step 2 & 3 pada mulanya */
        #step2, #step3 {
            display: none;
        }
    </style>
</head>
<body>

<div class="container" id="main-container">
    <!-- Soalan Pertama -->
    <div id="step1">
        <h1>Do you love me Anis? ❤️</h1>
        <div class="btn-group">
            <button class="btn" onclick="showStep2()">Yes</button>
            <button class="btn runaway" id="btn-no">No</button>
        </div>
    </div>

    <!-- Soalan Kedua -->
    <div id="step2">
        <h1>Level of love? 😍</h1>
        <div class="btn-group">
            <button class="btn runaway">0%</button>
            <button class="btn runaway">50%</button>
            <button class="btn runaway">100%</button>
            <button class="btn" onclick="showStep3()">Infinity</button>
        </div>
    </div>

    <!-- Keputusan Akhir -->
    <div id="step3">
        <h1 style="font-size: 36px; margin-bottom: 0;">I LOVE YOU TOO ANIS! 🎆❤️</h1>
    </div>
</div>

<script>
    // Fungsi untuk buat butang lari bertukar tempat
    function moveButton(btn) {
        // Kira saiz skrin supaya butang tak terkeluar dari pandangan
        const maxX = window.innerWidth - btn.clientWidth - 20;
        const maxY = window.innerHeight - btn.clientHeight - 20;
        
        const randomX = Math.random() * maxX;
        const randomY = Math.random() * maxY;
        
        btn.style.position = 'fixed';
        btn.style.left = `${randomX}px`;
        btn.style.top = `${randomY}px`;
    }

    // Assign fungsi lari kepada semua butang yang ada class 'runaway'
    const runaways = document.querySelectorAll('.runaway');
    runaways.forEach(btn => {
        // Lari bila mouse lalu (untuk PC)
        btn.addEventListener('mouseover', () => moveButton(btn));
        
        // Lari bila jari sentuh (untuk Phone)
        btn.addEventListener('touchstart', (e) => {
            e.preventDefault(); // Elak butang tertekan di phone
            moveButton(btn);
        });
        
        // Lari bila tertekan (sekadar langkah berjaga-jaga)
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            moveButton(btn);
        });
    });

    // Pergi ke soalan Level of Love
    function showStep2() {
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
    }

    // Pergi ke mesej I LOVE YOU & tembak bunga api
    function showStep3() {
        document.getElementById('step2').style.display = 'none';
        document.getElementById('step3').style.display = 'block';
        
        // Buat background container transparent sikit biar bunga api nampak jelas
        document.getElementById('main-container').style.background = 'rgba(255, 255, 255, 0.9)';
        
        fireworks();
    }

    // Logic Bunga Api (Confetti)
    function fireworks() {
        var duration = 8 * 1000; // Bunga api meletup selama 8 saat
        var animationEnd = Date.now() + duration;
        var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        var interval = setInterval(function() {
            var timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            var particleCount = 50 * (timeLeft / duration);
            // Tembak dari dua bucu berbeza
            confetti(Object.assign({}, defaults, { particleCount,
                origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
            }));
            confetti(Object.assign({}, defaults, { particleCount,
                origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
            }));
        }, 250);
    }
</script>
</body>
</html>
"""

# Paparkan HTML di dalam Streamlit (ketinggian disetkan kepada 700px supaya ngam)
components.html(html_code, height=700)
