// Working voice recorder with file upload fallback
class WorkingVoiceRecorder {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
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
        container.className = 'working-voice-recorder';
        container.innerHTML = `
            <div style="margin: 15px 0; padding: 15px; border: 2px dashed #007bff; border-radius: 8px; background: #f8f9fa;">
                <h4 style="margin: 0 0 10px 0; color: #007bff;">🎤 Voice Input</h4>
                <p style="margin: 0 0 10px 0; font-size: 0.9em; color: #666;">Speak clearly in Hindi or English. Good audio quality improves recognition.</p>
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <button type="button" id="record-voice-btn" class="btn btn-primary">
                        🎤 Start Recording
                    </button>
                    <input type="file" id="voice-file-input" accept="audio/*" style="display: none;">
                    <button type="button" id="upload-voice-btn" class="btn btn-secondary">
                        📁 Upload Audio File
                    </button>
                </div>
                <div id="voice-status" style="margin-top: 10px; font-size: 0.9em;"></div>
                <div id="voice-result" style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px; display: none;"></div>
            </div>
        `;
        
        textarea.parentNode.insertBefore(container, textarea.nextSibling);
        
        this.recordBtn = document.getElementById('record-voice-btn');
        this.uploadBtn = document.getElementById('upload-voice-btn');
        this.fileInput = document.getElementById('voice-file-input');
        this.statusDiv = document.getElementById('voice-status');
        this.resultDiv = document.getElementById('voice-result');
    }
    
    setupEventListeners() {
        // Record button
        this.recordBtn.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
        
        // Upload button
        this.uploadBtn.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // File input
        this.fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.processAudioFile(file);
            }
        });
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.processAudioFile(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            this.recordBtn.textContent = '⏹️ Stop Recording';
            this.recordBtn.className = 'btn btn-danger';
            this.statusDiv.innerHTML = '<span style="color: #dc3545;">🔴 Recording... Speak clearly</span>';
            
        } catch (error) {
            console.error('Recording failed:', error);
            this.statusDiv.innerHTML = '<span style="color: #dc3545;">❌ Microphone access denied. Use file upload instead.</span>';
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            this.recordBtn.textContent = '🎤 Start Recording';
            this.recordBtn.className = 'btn btn-primary';
            this.statusDiv.innerHTML = '<span style="color: #ffc107;">⏳ Processing audio...</span>';
        }
    }
    
    async processAudioFile(file) {
        try {
            this.statusDiv.innerHTML = '<span style="color: #ffc107;">⏳ Processing voice...</span>';
            
            const formData = new FormData();
            formData.append('audio', file, 'voice.wav');
            
            const response = await fetch('/api/voice_process_async', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success && result.text) {
                this.displayResult(result);
                this.updateTextarea(result.text);
            } else {
                this.statusDiv.innerHTML = '<span style="color: #dc3545;">❌ Speech not recognized. Please:<br>• Speak clearly and loudly<br>• Use Hindi or English<br>• Ensure good audio quality</span>';
            }
            
        } catch (error) {
            console.error('Voice processing error:', error);
            this.statusDiv.innerHTML = '<span style="color: #dc3545;">❌ Processing failed. Please:<br>• Check internet connection<br>• Try uploading audio file instead<br>• Ensure audio is clear</span>';
        }
    }
    
    displayResult(result) {
        const confidence = Math.round((result.confidence || 0.5) * 100);
        
        let analysisInfo = '';
        if (result.issue_type && result.issue_type !== 'unknown') {
            analysisInfo = `<br><strong>Issue:</strong> ${result.issue_type.charAt(0).toUpperCase() + result.issue_type.slice(1)}`;
        }
        if (result.location) {
            analysisInfo += `<br><strong>Location:</strong> ${result.location}`;
        }
        if (result.urgency) {
            analysisInfo += `<br><strong>Priority:</strong> ${result.urgency.charAt(0).toUpperCase() + result.urgency.slice(1)}`;
        }
        
        this.resultDiv.innerHTML = `
            <div style="border-left: 4px solid #28a745; padding-left: 10px;">
                <strong>✅ Voice Analyzed (${result.language || 'unknown'})</strong><br>
                <em>"${result.original_text || result.text}"</em>${analysisInfo}<br>
                <small style="color: #6c757d;">Confidence: ${confidence}% | Time: ${(result.processing_time || 0).toFixed(1)}s</small>
            </div>
        `;
        this.resultDiv.style.display = 'block';
        
        // Auto-fill form fields based on analysis
        this.autoFillForm(result);
        
        this.statusDiv.innerHTML = '<span style="color: #28a745;">✅ Voice analyzed and form updated!</span>';
    }
    
    updateTextarea(text) {
        const textarea = document.querySelector('textarea[name="description"]');
        if (textarea && text) {
            textarea.value = text;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    
    autoFillForm(result) {
        // Auto-fill issue type
        if (result.issue_type && result.issue_type !== 'unknown') {
            const issueSelect = document.querySelector('select[name="issue_type"]');
            if (issueSelect) {
                const option = Array.from(issueSelect.options).find(opt => 
                    opt.value.toLowerCase() === result.issue_type.toLowerCase()
                );
                if (option) {
                    issueSelect.value = option.value;
                    issueSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        }
        
        // Show analysis info
        if (result.location || result.urgency) {
            const analysisDiv = document.createElement('div');
            analysisDiv.style.cssText = 'margin-top: 10px; padding: 10px; background: #e7f3ff; border-radius: 5px; font-size: 0.9em;';
            
            let analysisText = '<strong>Extracted Information:</strong><br>';
            if (result.location) analysisText += `Location: ${result.location}<br>`;
            if (result.urgency) analysisText += `Priority: ${result.urgency}<br>`;
            if (result.keywords && result.keywords.length > 0) {
                analysisText += `Keywords: ${result.keywords.join(', ')}`;
            }
            
            analysisDiv.innerHTML = analysisText;
            this.resultDiv.appendChild(analysisDiv);
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('textarea[name="description"]')) {
        new WorkingVoiceRecorder();
    }
});