const uploadForm = document.getElementById("uploadForm");
const statusDiv = document.getElementById("status");
const downloadButton = document.getElementById("downloadButton");

function showNotification(message, isLoading = false) {
    statusDiv.innerText = message;
    statusDiv.classList.add("show");

    if (isLoading) {
        statusDiv.innerHTML = `<span class="loading-spinner"></span> ${message}`;
    }

    statusDiv.style.right = "20px";
}

function hideNotification() {
    statusDiv.style.right = "-500px";
    setTimeout(() => {
        statusDiv.classList.remove("show");
    }, 5);
}

uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    showNotification("Uploading file...", true);

    const formData = new FormData(uploadForm);
    const response = await fetch("/ws/upload/", {
        method: "POST",
        body: formData,
    });

    const data = await response.json();
    const sessionId = data.session_id;
    connectWebSocket(sessionId);
});

function connectWebSocket(sessionId) {
    const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

    socket.onmessage = function (event) {
        const message = event.data;

        if (message.includes("complete")) {
            showNotification("Translation complete. Download available.", false);
            downloadButton.disabled = false;
            downloadButton.onclick = () => {
                window.location.href = `/ws/${sessionId}`;
            };
        } else {
            showNotification(message, true);
        }
    };

    socket.onclose = function () {
        hideNotification();
    };
}



document.querySelector(".btn-history").addEventListener("click", () => {
    const overlay = document.getElementById("overlay");
    const modal = document.getElementById("modal");

    // Fetch and display history data
    fetchTranslationHistory((historyHTML) => {
        document.getElementById("history-modal-content").innerHTML = historyHTML;
        overlay.style.display = "block";
        modal.classList.add("show");
    });
});

document.getElementById("close-modal").addEventListener("click", () => {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("modal").classList.remove("show");
});

function fetchTranslationHistory(callback) {
    fetch('/history/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const historyHTML = data.history.map(item => `
                <div class="history-item">
                    <div class="history-item-header">
                        <strong>Session ID:</strong> ${item.sessionId}
                    </div>
                    <div class="history-item-content">
                        <div><strong>Translated Language:</strong> ${item.translated_language}</div>
                        <div><strong>Created At:</strong> ${new Date(item.createdAt).toLocaleString()}</div>
                        <div><strong>Files Processed:</strong> ${item.filesProcessed.length}</div>
                    </div>
                    <ul class="history-files">
                    ${item.filesProcessed.map(file => `
                        <li class="history-file">
                            <strong>File Name:</strong> ${file.fileName || file}<br>                
                            <strong>File Path:</strong> ${file.filePath || file}<br>
                            <strong>Processed At:</strong> ${file.processedAt || file}<br>
                            <strong>Result:</strong> ${file.result || file}
                        </li>
                    `).join('')}
                    </ul>
                </div>
                `).join('');

                callback(historyHTML);
            } else {
                console.error("Failed to load history:", data.message);
            }
        })
        .catch(error => {
            console.error("Error fetching history:", error);
        });
}
