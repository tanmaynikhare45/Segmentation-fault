// Real-time news and social media feed integration
class NewsSocialFeed {
    constructor() {
        this.feedContainer = null;
        this.refreshInterval = null;
        this.isLoading = false;
        this.lastUpdate = null;
        
        this.init();
    }
    
    init() {
        this.createFeedContainer();
        this.loadInitialFeed();
        this.setupAutoRefresh();
        this.setupEventListeners();
    }
    
    createFeedContainer() {
        // Find existing container or create new one
        this.feedContainer = document.getElementById('news-social-feed');
        
        if (!this.feedContainer) {
            this.feedContainer = document.createElement('div');
            this.feedContainer.id = 'news-social-feed';
            this.feedContainer.className = 'news-social-feed';
            
            // Insert in appropriate location (dashboard, home page, etc.)
            const targetContainer = document.querySelector('.dashboard-content') || 
                                  document.querySelector('.main-content') || 
                                  document.body;
            
            if (targetContainer) {
                targetContainer.appendChild(this.feedContainer);
            }
        }
        
        this.feedContainer.innerHTML = `
            <div class="feed-header">
                <h3>🔥 Live Civic Issues Feed</h3>
                <div class="feed-controls">
                    <button id="refresh-feed" class="btn btn-sm btn-outline-primary">
                        🔄 Refresh
                    </button>
                    <span id="last-updated" class="last-updated"></span>
                </div>
            </div>
            <div class="feed-filters">
                <button class="filter-btn active" data-source="all">All Sources</button>
                <button class="filter-btn" data-source="news">📰 News</button>
                <button class="filter-btn" data-source="twitter">🐦 Twitter</button>
                <button class="filter-btn" data-source="reddit">🔴 Reddit</button>
            </div>
            <div id="feed-content" class="feed-content">
                <div class="loading-spinner">⏳ Loading civic issues...</div>
            </div>
        `;
    }
    
    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-feed').addEventListener('click', () => {
            this.loadFeed();
        });
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterFeed(e.target.dataset.source);
            });
        });
    }
    
    setupAutoRefresh() {
        // Refresh every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadFeed(true); // Silent refresh
        }, 5 * 60 * 1000);
    }
    
    async loadInitialFeed() {
        await this.loadFeed();
    }
    
    async loadFeed(silent = false) {
        if (this.isLoading) return;
        
        this.isLoading = true;
        
        if (!silent) {
            document.getElementById('feed-content').innerHTML = '<div class="loading-spinner">⏳ Loading latest issues...</div>';
        }
        
        try {
            const response = await fetch('/api/news_issues', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    city: 'Gwalior' // Can be made dynamic
                })
            });
            
            const data = await response.json();
            
            if (data.issues && data.issues.length > 0) {
                this.displayFeed(data.issues);
                this.updateLastUpdated();
            } else {
                this.displayEmptyFeed();
            }
            
        } catch (error) {
            console.error('Error loading feed:', error);
            this.displayErrorFeed();
        } finally {
            this.isLoading = false;
        }
    }
    
    displayFeed(issues) {
        const feedContent = document.getElementById('feed-content');
        
        if (issues.length === 0) {
            this.displayEmptyFeed();
            return;
        }
        
        const feedHTML = issues.map(issue => this.createIssueCard(issue)).join('');
        feedContent.innerHTML = feedHTML;
        
        // Add click handlers for issue cards
        this.setupIssueCardHandlers();
    }
    
    createIssueCard(issue) {
        const sourceIcon = this.getSourceIcon(issue.source_type);
        const issueTypeIcon = this.getIssueTypeIcon(issue.issue_type);
        const timeAgo = this.getTimeAgo(issue.published_date);
        const relevanceScore = Math.round((issue.relevance_score || 0) * 10);
        
        return `
            <div class="issue-card" data-source="${issue.source_type}" data-issue-type="${issue.issue_type}">
                <div class="issue-header">
                    <div class="source-info">
                        <span class="source-icon">${sourceIcon}</span>
                        <span class="source-name">${issue.source_type.toUpperCase()}</span>
                        <span class="issue-type">${issueTypeIcon} ${issue.issue_type}</span>
                    </div>
                    <div class="issue-meta">
                        <span class="relevance-score" title="Relevance Score">⭐ ${relevanceScore}/10</span>
                        <span class="time-ago">${timeAgo}</span>
                    </div>
                </div>
                <div class="issue-content">
                    <h4 class="issue-title">${this.truncateText(issue.description.split(' - ')[0], 80)}</h4>
                    <p class="issue-description">${this.truncateText(issue.description, 150)}</p>
                    ${issue.keywords ? `<div class="issue-keywords">
                        ${issue.keywords.slice(0, 3).map(kw => `<span class="keyword-tag">#${kw}</span>`).join('')}
                    </div>` : ''}
                </div>
                <div class="issue-actions">
                    <button class="btn btn-sm btn-primary create-complaint" data-issue='${JSON.stringify(issue)}'>
                        📝 Create Complaint
                    </button>
                    <a href="${issue.source_url}" target="_blank" class="btn btn-sm btn-outline-secondary">
                        🔗 View Source
                    </a>
                </div>
            </div>
        `;
    }
    
    getSourceIcon(source) {
        const icons = {
            'news': '📰',
            'twitter': '🐦',
            'reddit': '🔴',
            'facebook': '📘'
        };
        return icons[source] || '📄';
    }
    
    getIssueTypeIcon(issueType) {
        const icons = {
            'pothole': '🕳️',
            'garbage': '🗑️',
            'streetlight': '💡',
            'waterlogging': '💧',
            'traffic': '🚦',
            'pollution': '🏭',
            'encroachment': '🚧'
        };
        return icons[issueType] || '⚠️';
    }
    
    getTimeAgo(dateString) {
        if (!dateString) return 'Unknown time';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }
    
    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    setupIssueCardHandlers() {
        // Handle "Create Complaint" buttons
        document.querySelectorAll('.create-complaint').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const issueData = JSON.parse(e.target.dataset.issue);
                this.createComplaintFromIssue(issueData);
            });
        });
    }
    
    createComplaintFromIssue(issue) {
        // Pre-fill complaint form with issue data
        const description = `Based on ${issue.source_type.toUpperCase()} report: ${issue.description}`;
        
        // If on report page, fill the form
        const descriptionField = document.querySelector('textarea[name="description"]');
        const issueTypeField = document.querySelector('select[name="issue_type"]');
        
        if (descriptionField) {
            descriptionField.value = description;
            descriptionField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        if (issueTypeField && issue.issue_type !== 'unknown') {
            issueTypeField.value = issue.issue_type;
            issueTypeField.dispatchEvent(new Event('change', { bubbles: true }));
        }
        
        // If not on report page, redirect there with data
        if (!descriptionField) {
            const params = new URLSearchParams({
                description: description,
                issue_type: issue.issue_type,
                source: 'news_feed'
            });
            window.location.href = `/report?${params.toString()}`;
        } else {
            // Scroll to form
            descriptionField.scrollIntoView({ behavior: 'smooth' });
            descriptionField.focus();
        }
    }
    
    filterFeed(source) {
        const cards = document.querySelectorAll('.issue-card');
        
        cards.forEach(card => {
            if (source === 'all' || card.dataset.source === source) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    updateLastUpdated() {
        const lastUpdatedEl = document.getElementById('last-updated');
        if (lastUpdatedEl) {
            const now = new Date();
            lastUpdatedEl.textContent = `Updated: ${now.toLocaleTimeString()}`;
        }
    }
    
    displayEmptyFeed() {
        document.getElementById('feed-content').innerHTML = `
            <div class="empty-feed">
                <div class="empty-icon">📭</div>
                <h4>No Recent Issues Found</h4>
                <p>No civic issues detected in recent news and social media.</p>
                <button onclick="window.location.href='/report'" class="btn btn-primary">
                    📝 Report an Issue
                </button>
            </div>
        `;
    }
    
    displayErrorFeed() {
        document.getElementById('feed-content').innerHTML = `
            <div class="error-feed">
                <div class="error-icon">❌</div>
                <h4>Failed to Load Feed</h4>
                <p>Unable to fetch latest civic issues. Please try again.</p>
                <button onclick="location.reload()" class="btn btn-outline-primary">
                    🔄 Retry
                </button>
            </div>
        `;
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// CSS Styles for news feed
const newsFeedStyles = `
<style>
.news-social-feed {
    margin: 20px 0;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    overflow: hidden;
}

.feed-header {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.feed-header h3 {
    margin: 0;
    font-size: 1.4em;
}

.feed-controls {
    display: flex;
    align-items: center;
    gap: 15px;
}

.last-updated {
    font-size: 0.85em;
    opacity: 0.9;
}

.feed-filters {
    padding: 15px 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.filter-btn {
    padding: 6px 12px;
    border: 1px solid #dee2e6;
    background: white;
    border-radius: 20px;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.2s;
}

.filter-btn:hover {
    background: #e9ecef;
}

.filter-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.feed-content {
    max-height: 600px;
    overflow-y: auto;
    padding: 20px;
}

.issue-card {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    margin-bottom: 15px;
    padding: 15px;
    transition: all 0.2s;
    background: white;
}

.issue-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.issue-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.source-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.source-name {
    font-weight: bold;
    font-size: 0.8em;
    color: #6c757d;
}

.issue-type {
    background: #e9ecef;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    color: #495057;
}

.issue-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.85em;
    color: #6c757d;
}

.relevance-score {
    background: #fff3cd;
    color: #856404;
    padding: 2px 6px;
    border-radius: 10px;
}

.issue-title {
    font-size: 1.1em;
    margin: 8px 0;
    color: #212529;
}

.issue-description {
    color: #6c757d;
    margin: 8px 0;
    line-height: 1.4;
}

.issue-keywords {
    margin: 10px 0;
}

.keyword-tag {
    background: #e7f3ff;
    color: #0066cc;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    margin-right: 5px;
}

.issue-actions {
    display: flex;
    gap: 10px;
    margin-top: 12px;
}

.loading-spinner, .empty-feed, .error-feed {
    text-align: center;
    padding: 40px 20px;
    color: #6c757d;
}

.empty-icon, .error-icon {
    font-size: 3em;
    margin-bottom: 15px;
}

.empty-feed h4, .error-feed h4 {
    margin: 15px 0 10px 0;
    color: #495057;
}

@media (max-width: 768px) {
    .feed-header {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
    
    .issue-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
    
    .issue-actions {
        flex-direction: column;
    }
    
    .feed-filters {
        justify-content: center;
    }
}
</style>
`;

// Initialize news feed when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add styles
    document.head.insertAdjacentHTML('beforeend', newsFeedStyles);
    
    // Initialize on appropriate pages
    const shouldInitialize = window.location.pathname.includes('/home') || 
                           window.location.pathname.includes('/dashboard') ||
                           window.location.pathname === '/' ||
                           document.querySelector('.dashboard-content');
    
    if (shouldInitialize) {
        window.newsSocialFeed = new NewsSocialFeed();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.newsSocialFeed) {
        window.newsSocialFeed.destroy();
    }
});