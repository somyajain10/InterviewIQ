(function () {
    const answer = document.getElementById("answer");
    const durationInput = document.getElementById("duration");
    const typedInput = document.getElementById("typed");
    const skippedInput = document.getElementById("skipped");
    const timerEl = document.getElementById("timer");
    const startBtn = document.getElementById("startRec");
    const stopBtn = document.getElementById("stopRec");
    const recStatus = document.getElementById("recStatus");
    const speechNote = document.getElementById("speechNote");
    const form = document.getElementById("answerForm");
    if (!form || !answer) return;

    let seconds = 0;
    let usedVoice = false;
    const tick = setInterval(function () {
        seconds += 1;
        const m = String(Math.floor(seconds / 60)).padStart(2, "0");
        const s = String(seconds % 60).padStart(2, "0");
        timerEl.textContent = m + ":" + s;
        durationInput.value = String(seconds);
    }, 1000);

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    if (!SpeechRecognition) {
        speechNote.textContent = "Speech recognition is not supported in this browser. Typing works fully — use the answer box below.";
        startBtn.disabled = true;
        stopBtn.disabled = true;
    } else {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";
        recognition.onresult = function (event) {
            let finalText = "";
            for (let i = 0; i < event.results.length; i += 1) {
                finalText += event.results[i][0].transcript + " ";
            }
            answer.value = finalText.trim();
            usedVoice = true;
            typedInput.value = "0";
        };
        recognition.onerror = function () {
            recStatus.textContent = "Microphone error. You can still type your answer.";
            startBtn.classList.remove("recording");
        };
        recognition.onend = function () {
            startBtn.classList.remove("recording");
            recStatus.textContent = "Microphone idle";
        };
    }

    startBtn.addEventListener("click", function () {
        if (!recognition) return;
        try {
            recognition.start();
            startBtn.classList.add("recording");
            recStatus.textContent = "Listening... speak clearly.";
        } catch (e) {
            recStatus.textContent = "Could not start the microphone. Type your answer instead.";
        }
    });

    stopBtn.addEventListener("click", function () {
        if (recognition) recognition.stop();
        startBtn.classList.remove("recording");
        recStatus.textContent = "Recording stopped";
    });

    document.getElementById("clearBtn").addEventListener("click", function () {
        answer.value = "";
        usedVoice = false;
        typedInput.value = "1";
    });

    document.getElementById("skipBtn").addEventListener("click", function () {
        skippedInput.value = "1";
        answer.value = answer.value || "skipped";
        form.submit();
    });

    answer.addEventListener("input", function () {
        if (!usedVoice) typedInput.value = "1";
    });

    form.addEventListener("submit", function () {
        if (recognition) {
            try { recognition.stop(); } catch (e) {}
        }
        clearInterval(tick);
        durationInput.value = String(seconds);
        if (!usedVoice) typedInput.value = "1";
        const overlay = document.createElement("div");
        overlay.style.cssText = "position:fixed;inset:0;background:rgba(8,17,31,0.55);display:grid;place-items:center;z-index:50;color:#fff;font-weight:700;font-size:1.2rem;";
        overlay.textContent = "Analyzing your response...";
        document.body.appendChild(overlay);
    });
})();
