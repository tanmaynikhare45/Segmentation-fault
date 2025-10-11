// Simple voice recorder without HTTPS requirement
class SimpleVoiceRecorder {
    constructor() {
        this.isRecording = false;
        this.init();
    }
    
    init() {
        this.createUI();
        this.setupEventListeners();
    }
    
    createUI() {
        const textarea = document.querySelector('textarea[name="description"]');
        if (!textarea) return;
        
        const container = document.createElement('div');
        container.className = 'simple-voice-recorder';
        container.innerHTML = `
            <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <button type="button" id="simple-record-btn" class="btn btn-primary">
                    🎤 Record Voice
                </button>
                <input type="file" id="voice-upload" accept="audio/*" style="margin-left: 10px;">
                <div id="voice-status" style="margin-top: 5px; font-size: 0.9em; color: #666;"></div>
            </div>
        `;
        
        textarea.parentNode.insertBefore(container, textarea.nextSibling);
        
        this.recordButton = document.getElementById('simple-record-btn');
        this.voiceUpload = document.getElementById('voice-upload');
        this.statusDiv = document.getElementById('voice-status');
    }
    
    setupEventListeners() {
        // File upload handler
        this.voiceUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.processVoiceFile(file);
            }
        });
        
        // Record button - try microphone or fallback to file upload
        this.recordButton.addEventListener('click', () => {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                this.tryMicrophoneAccess();
            } else {
                this.voiceUpload.click();
            }
        });
    }
    
    async tryMicrophoneAccess() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.startRecording(stream);
        } catch (error) {
            console.log('Microphone access denied, using file upload');
            this.statusDiv.innerHTML = '⚠️ Microphone access denied. Please upload an audio file instead.';
            this.voiceUpload.click();
        }
    }
    
    startRecording(stream) {
        this.statusDiv.innerHTML = '🔴 Recording... Click stop when done.';
        this.recordButton.textContent = '⏹️ Stop Recording';
        this.recordButton.onclick = () => this.stopRecording(stream);
        
        // Simple recording implementation
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        
        this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
        };
        
        this.mediaRecorder.onstop = () => {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            this.processVoiceFile(audioBlob);
        };
        
        this.mediaRecorder.start();
    }
    
    stopRecording(stream) {
        this.mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
        
        this.recordButton.textContent = '🎤 Record Voice';
        this.recordButton.onclick = () => this.tryMicrophoneAccess();
        this.statusDiv.innerHTML = '⏳ Processing audio...';
    }
    
    async processVoiceFile(file) {
        try {
            const formData = new FormData();
            formData.append('audio', file, 'recording.wav');
            
            const response = await fetch('/api/voice_process_async', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success && result.text) {
                this.updateTextarea(result.text);
                this.statusDiv.innerHTML = `✅ Voice recognized: "${result.text}" (${result.language})`;
            } else {
                this.statusDiv.innerHTML = '❌ Voice processing failed. Try speaking clearly.';
            }
            
        } catch (error) {
            console.error('Voice processing error:', error);
            this.statusDiv.innerHTML = '❌ Processing failed. Check your connection.';
        }
    }
    
    updateTextarea(text) {
        const textarea = document.querySelector('textarea[name="description"]');
        if (textarea && text) {
            const currentText = textarea.value.trim();
            if (currentText) {
                textarea.value = `${currentText}\n\n[Voice]: ${text}`;
            } else {
                textarea.value = text;
            }
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('textarea[name="description"]')) {
        new SimpleVoiceRecorder();
    }
});