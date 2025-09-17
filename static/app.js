// Global state
let currentUser = null;
let currentApiKey = null;
let uploadedMediaId = null;

// API functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                'api-key': currentApiKey,
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function uploadFile(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/medias', {
            method: 'POST',
            headers: {
                'api-key': currentApiKey
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Upload Error:', error);
        throw error;
    }
}

// Auth functions
function quickLogin(apiKey) {
    document.getElementById('apiKeyInput').value = apiKey;
    login();
}

async function login() {
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    
    if (!apiKey) {
        showToast('Введите API ключ', 'error');
        return;
    }

    try {
        currentApiKey = apiKey;
        const response = await apiRequest('/api/users/me');
        
        if (response.result) {
            currentUser = response.user;
            document.getElementById('authModal').classList.add('hidden');
            document.getElementById('app').classList.remove('hidden');
            document.getElementById('currentUser').textContent = currentUser.name;
            
            showToast(`Добро пожаловать, ${currentUser.name}!`, 'success');
            loadFeed();
            loadProfile();
            loadUsers();
        } else {
            throw new Error('Invalid response');
        }
    } catch (error) {
        showToast('Неверный API ключ', 'error');
        currentApiKey = null;
        currentUser = null;
    }
}

function logout() {
    currentUser = null;
    currentApiKey = null;
    document.getElementById('authModal').classList.remove('hidden');
    document.getElementById('app').classList.add('hidden');
    document.getElementById('apiKeyInput').value = '';
    showToast('Вы вышли из системы', 'success');
}

// Navigation
function showSection(sectionName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Update sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}Section`).classList.add('active');

    // Load data for section
    if (sectionName === 'feed') {
        loadFeed();
    } else if (sectionName === 'profile') {
        loadProfile();
    } else if (sectionName === 'users') {
        loadUsers();
    }
}

// Tweet functions
async function postTweet() {
    const tweetText = document.getElementById('tweetText').value.trim();
    
    if (!tweetText) {
        showToast('Введите текст твита', 'error');
        return;
    }

    if (tweetText.length > 280) {
        showToast('Твит слишком длинный', 'error');
        return;
    }

    try {
        const tweetBtn = document.getElementById('tweetBtn');
        tweetBtn.disabled = true;
        tweetBtn.textContent = 'Отправляем...';

        const tweetData = {
            tweet_data: tweetText
        };

        if (uploadedMediaId) {
            tweetData.tweet_media_ids = [uploadedMediaId];
        }

        const response = await apiRequest('/api/tweets', {
            method: 'POST',
            body: JSON.stringify(tweetData)
        });

        if (response.result) {
            document.getElementById('tweetText').value = '';
            uploadedMediaId = null;
            document.getElementById('imagePreview').classList.add('hidden');
            updateCharCount();
            showToast('Твит опубликован!', 'success');
            loadFeed();
        } else {
            throw new Error('Failed to post tweet');
        }
    } catch (error) {
        showToast('Ошибка при публикации твита', 'error');
    } finally {
        const tweetBtn = document.getElementById('tweetBtn');
        tweetBtn.disabled = false;
        tweetBtn.textContent = 'Твитнуть';
    }
}

async function deleteTweet(tweetId) {
    if (!confirm('Удалить этот твит?')) {
        return;
    }

    try {
        const response = await apiRequest(`/api/tweets/${tweetId}`, {
            method: 'DELETE'
        });

        if (response.result) {
            showToast('Твит удален', 'success');
            loadFeed();
        } else {
            throw new Error('Failed to delete tweet');
        }
    } catch (error) {
        showToast('Ошибка при удалении твита', 'error');
    }
}

async function toggleLike(tweetId, isLiked) {
    try {
        const method = isLiked ? 'DELETE' : 'POST';
        const response = await apiRequest(`/api/tweets/${tweetId}/likes`, {
            method: method
        });

        if (response.result) {
            loadFeed();
        } else {
            throw new Error('Failed to toggle like');
        }
    } catch (error) {
        showToast('Ошибка при изменении лайка', 'error');
    }
}

async function loadFeed() {
    try {
        const response = await apiRequest('/api/tweets');
        
        if (response.result) {
            displayTweets(response.tweets);
        } else {
            throw new Error('Failed to load feed');
        }
    } catch (error) {
        document.getElementById('tweetsList').innerHTML = '<div class="loading">Ошибка загрузки ленты</div>';
    }
}

function displayTweets(tweets) {
    const container = document.getElementById('tweetsList');
    
    if (tweets.length === 0) {
        container.innerHTML = '<div class="loading">Нет твитов. Подпишитесь на пользователей или создайте первый твит!</div>';
        return;
    }

    container.innerHTML = tweets.map(tweet => {
        const isLiked = tweet.likes.some(like => like.user_id === currentUser.id);
        const isOwner = tweet.author.id === currentUser.id;
        
        return `
            <div class="tweet">
                <div class="tweet-header">
                    <div class="tweet-avatar">${tweet.author.name.charAt(0).toUpperCase()}</div>
                    <div class="tweet-author">${tweet.author.name}</div>
                </div>
                <div class="tweet-content">${escapeHtml(tweet.content)}</div>
                ${tweet.attachments.length > 0 ? `
                    <div class="tweet-images">
                        ${tweet.attachments.map(url => `<img src="${url}" alt="Tweet image">`).join('')}
                    </div>
                ` : ''}
                <div class="tweet-actions">
                    <button class="tweet-action ${isLiked ? 'liked' : ''}" onclick="toggleLike(${tweet.id}, ${isLiked})">
                        ${isLiked ? '❤️' : '🤍'} ${tweet.likes.length}
                    </button>
                    ${isOwner ? `
                        <button class="tweet-action delete" onclick="deleteTweet(${tweet.id})">
                            🗑️ Удалить
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Profile functions
async function loadProfile() {
    try {
        const response = await apiRequest('/api/users/me');
        
        if (response.result) {
            displayProfile(response.user);
        } else {
            throw new Error('Failed to load profile');
        }
    } catch (error) {
        document.getElementById('profileInfo').innerHTML = '<div class="loading">Ошибка загрузки профиля</div>';
    }
}

function displayProfile(user) {
    document.getElementById('profileInfo').innerHTML = `
        <div class="profile-header">
            <div class="profile-avatar">${user.name.charAt(0).toUpperCase()}</div>
            <div>
                <div class="profile-name">${user.name}</div>
                <div class="profile-id">ID: ${user.id}</div>
            </div>
        </div>
        <div class="profile-stats">
            <div class="stat">
                <div class="stat-number">${user.followers.length}</div>
                <div class="stat-label">Подписчики</div>
            </div>
            <div class="stat">
                <div class="stat-number">${user.following.length}</div>
                <div class="stat-label">Подписки</div>
            </div>
        </div>
        ${user.followers.length > 0 ? `
            <div class="followers-section">
                <h4>Подписчики:</h4>
                <div class="users-grid">
                    ${user.followers.map(follower => `
                        <div class="user-mini">
                            <span class="user-mini-avatar">${follower.name.charAt(0).toUpperCase()}</span>
                            ${follower.name}
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        ${user.following.length > 0 ? `
            <div class="following-section">
                <h4>Подписки:</h4>
                <div class="users-grid">
                    ${user.following.map(following => `
                        <div class="user-mini">
                            <span class="user-mini-avatar">${following.name.charAt(0).toUpperCase()}</span>
                            ${following.name}
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

// Users functions
async function loadUsers() {
    try {
        // Load all users (we'll use the known user IDs)
        const userIds = [1, 2, 3]; // alice, bob, charlie
        const users = [];
        
        for (const id of userIds) {
            try {
                const response = await apiRequest(`/api/users/${id}`);
                if (response.result) {
                    users.push(response.user);
                }
            } catch (error) {
                console.error(`Failed to load user ${id}:`, error);
            }
        }
        
        displayUsers(users);
    } catch (error) {
        document.getElementById('usersList').innerHTML = '<div class="loading">Ошибка загрузки пользователей</div>';
    }
}

function displayUsers(users) {
    const container = document.getElementById('usersList');
    
    container.innerHTML = users.map(user => {
        const isCurrentUser = user.id === currentUser.id;
        const isFollowing = user.followers.some(follower => follower.id === currentUser.id);
        
        return `
            <div class="user-card">
                <div class="user-info-card">
                    <div class="user-card-avatar">${user.name.charAt(0).toUpperCase()}</div>
                    <div>
                        <div class="user-card-name">${user.name}</div>
                        <div class="user-card-stats">
                            ${user.followers.length} подписчиков • ${user.following.length} подписок
                        </div>
                    </div>
                </div>
                ${!isCurrentUser ? `
                    <button class="btn ${isFollowing ? 'btn-ghost' : 'btn-primary'}" 
                            onclick="toggleFollow(${user.id}, ${isFollowing})">
                        ${isFollowing ? 'Отписаться' : 'Подписаться'}
                    </button>
                ` : '<span class="current-user-badge">Это вы</span>'}
            </div>
        `;
    }).join('');
}

async function toggleFollow(userId, isFollowing) {
    try {
        const method = isFollowing ? 'DELETE' : 'POST';
        const response = await apiRequest(`/api/users/${userId}/follow`, {
            method: method
        });

        if (response.result) {
            showToast(isFollowing ? 'Вы отписались' : 'Вы подписались', 'success');
            loadUsers();
            loadProfile();
        } else {
            throw new Error('Failed to toggle follow');
        }
    } catch (error) {
        showToast('Ошибка при изменении подписки', 'error');
    }
}

// Image upload
document.getElementById('imageInput').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showToast('Можно загружать только изображения', 'error');
        return;
    }

    if (file.size > 16 * 1024 * 1024) { // 16MB
        showToast('Файл слишком большой (максимум 16MB)', 'error');
        return;
    }

    try {
        const response = await uploadFile(file);
        if (response.result) {
            uploadedMediaId = response.media_id;
            
            // Show preview
            const preview = document.getElementById('imagePreview');
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <button class="remove-image" onclick="removeImage()">✕</button>
                `;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
            
            showToast('Изображение загружено', 'success');
        } else {
            throw new Error('Upload failed');
        }
    } catch (error) {
        showToast('Ошибка загрузки изображения', 'error');
        uploadedMediaId = null;
    }
});

function removeImage() {
    uploadedMediaId = null;
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('imageInput').value = '';
}

// Character count
document.getElementById('tweetText').addEventListener('input', updateCharCount);

function updateCharCount() {
    const text = document.getElementById('tweetText').value;
    const count = 280 - text.length;
    const counter = document.getElementById('charCount');
    
    counter.textContent = count;
    counter.style.color = count < 0 ? 'var(--error)' : count < 20 ? 'var(--accent)' : 'var(--text-muted)';
    
    document.getElementById('tweetBtn').disabled = count < 0 || text.trim().length === 0;
}

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateCharCount();
});
