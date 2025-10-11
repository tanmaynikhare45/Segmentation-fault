// Real-time voice recorder with multilingual support
class VoiceRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.stream = null;
        this.recordButton = null;
        this.statusDiv = null;
        this.resultDiv = null;
        
        this.init();
    }
    
    init() {
        // Create UI elements
        this.createUI();
        this.setupEventListeners();
    }
    
    createUI() {
        // Find or create voice recorder container
        let container = document.getElementById('voice-recorder');
        if (!container) {
            container = document.createElement('div');
            container.id = 'voice-recorder';
            container.className = 'voice-recorder-container';
            
            // Insert after description textarea if it exists
            const textarea = document.querySelector('textarea[name="description"]');
            if (textarea) {
                textarea.parentNode.insertBefore(container, textarea.nextSibling);
            }
        }
        
        container.innerHTML = `
            <div class="voice-controls">
                <button type="button" id="record-btn" class="btn btn-primary">
                    🎤 Start Recording
                </button>
                <div id="recording-status" class="recording-status"></div>
            </div>
            <div id="voice-result" class="voice-result"></div>
            <div class="supported-languages">
                <small>Supports: Hindi, English, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Urdu</small>
            </div>
        `;
        
        this.recordButton = document.getElementById('record-btn');
        this.statusDiv = document.getElementById('recording-status');
        this.resultDiv = document.getElementById('voice-result');
    }
    
    setupEventListeners() {
        this.recordButton.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
    }
    
    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            this.recordButton.textContent = '⏹️ Stop Recording';
            this.recordButton.className = 'btn btn-danger';
            this.statusDiv.innerHTML = '<span class="recording-indicator">🔴 Recording...</span>';
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.statusDiv.innerHTML = '<span class="error">❌ Microphone access denied</span>';
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            
            this.recordButton.textContent = '🎤 Start Recording';
            this.recordButton.className = 'btn btn-primary';
            this.statusDiv.innerHTML = '<span class="processing">⏳ Processing audio...</span>';
        }
    }
    
    async processAudio() {
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
            
            // Convert to WAV for better compatibility
            const wavBlob = await this.convertToWav(audioBlob);
            
            const formData = new FormData();
            formData.append('audio', wavBlob, 'recording.wav');
            
            const response = await fetch('/api/voice_process_async', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayResult(result);
                this.updateTextarea(result.text);
            } else {
                this.statusDiv.innerHTML = `<span class="error">❌ ${result.error}</span>`;
            }
            
        } catch (error) {
            console.error('Error processing audio:', error);
            this.statusDiv.innerHTML = '<span class="error">❌ Processing failed</span>';
        }
    }
    
    async convertToWav(webmBlob) {
        // Simple conversion - in production, use a proper audio conversion library
        return webmBlob; // For now, return as-is since our backend handles webm
    }
    
    displayResult(result) {
        const confidence = Math.round(result.confidence * 100);
        const processingTime = result.processing_time.toFixed(2);
        
        this.resultDiv.innerHTML = `
            <div class="voice-result-content">
                <div class="result-header">
                    <strong>✅ Voice Recognized</strong>
                    <span class="confidence">Confidence: ${confidence}%</span>
                </div>
                <div class="result-text">"${result.text}"</div>
                <div class="result-meta">
                    <span class="language">Language: ${result.language}</span>
                    <span class="timing">Processed in ${processingTime}s</span>
                </div>
            </div>
        `;
        
        this.statusDiv.innerHTML = '<span class="success">✅ Voice processed successfully</span>';
        
        // Auto-hide status after 3 seconds
        setTimeout(() => {
            this.statusDiv.innerHTML = '';
        }, 3000);
    }
    
    updateTextarea(text) {
        const textarea = document.querySelector('textarea[name="description"]');
        if (textarea && text) {
            const currentText = textarea.value.trim();
            if (currentText) {
                textarea.value = `${currentText}\n\n[Voice Input]: ${text}`;
            } else {
                textarea.value = text;
            }
            
            // Trigger input event to update any listeners
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
}

// CSS styles for voice recorder
const voiceRecorderStyles = `
<style>
.voice-recorder-container {
    margin: 15px 0;
    padding: 15px;
    border: 2px dashed #007bff;
    border-radius: 8px;
    background-color: #f8f9fa;
}

.voice-controls {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 10px;
}

.recording-status {
    font-weight: bold;
}

.recording-indicator {
    color: #dc3545;
    animation: pulse 1s infinite;
}

.processing {
    color: #ffc107;
}

.success {
    color: #28a745;
}

.error {
    color: #dc3545;
}

.voice-result {
    margin-top: 10px;
}

.voice-result-content {
    background: white;
    padding: 12px;
    border-radius: 6px;
    border-left: 4px solid #28a745;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.confidence {
    font-size: 0.9em;
    color: #6c757d;
}

.result-text {
    font-style: italic;
    margin: 8px 0;
    padding: 8px;
    background: #f8f9fa;
    border-radius: 4px;
}

.result-meta {
    display: flex;
    gap: 15px;
    font-size: 0.85em;
    color: #6c757d;
}

.supported-languages {
    margin-top: 8px;
    color: #6c757d;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

@media (max-width: 768px) {
    .voice-controls {
        flex-direction: column;
        align-items: stretch;
    }
    
    .result-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
    
    .result-meta {
        flex-direction: column;
        gap: 5px;
    }
}
</style>
`;

// Initialize voice recorder when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add styles
    document.head.insertAdjacentHTML('beforeend', voiceRecorderStyles);
    
    // Initialize voice recorder on report page
    if (window.location.pathname.includes('/report') || document.querySelector('textarea[name="description"]')) {
        new VoiceRecorder();
    }
});