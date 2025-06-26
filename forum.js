// Forum functionality

let currentPage = 1;
let currentCategory = 'all';
let posts = [];

// Sample forum posts data
const samplePosts = [
  {
    id: 1,
    title: "Help with Quadratic Equations",
    content: "I'm struggling with solving quadratic equations using the quadratic formula. Can someone explain the steps?",
    author: "Rahul Kumar",
    category: "math-10",
    categoryLabel: "Class 10",
    timestamp: "2024-01-15T10:30:00Z",
    replies: 5,
    likes: 12
  },
  {
    id: 2,
    title: "Trigonometry Tips for Board Exams",
    content: "What are the most important trigonometry formulas to remember for Class 12 board exams?",
    author: "Priya Sharma",
    category: "math-12",
    categoryLabel: "Class 12",
    timestamp: "2024-01-14T15:45:00Z",
    replies: 8,
    likes: 20
  },
  {
    id: 3,
    title: "Coordinate Geometry Practice Problems",
    content: "Looking for more practice problems on coordinate geometry. Any good resources?",
    author: "Amit Singh",
    category: "math-11",
    categoryLabel: "Class 11",
    timestamp: "2024-01-14T09:20:00Z",
    replies: 3,
    likes: 7
  },
  {
    id: 4,
    title: "Algebra Basics - Need Clarification",
    content: "Can someone help me understand the basics of algebraic expressions and their simplification?",
    author: "Sneha Patel",
    category: "math-9",
    categoryLabel: "Class 9",
    timestamp: "2024-01-13T14:15:00Z",
    replies: 6,
    likes: 15
  },
  {
    id: 5,
    title: "Study Group for Mathematics",
    content: "Anyone interested in forming an online study group for mathematics? We can meet weekly to discuss problems.",
    author: "Vikash Gupta",
    category: "general",
    categoryLabel: "General",
    timestamp: "2024-01-13T11:00:00Z",
    replies: 12,
    likes: 25
  },
  {
    id: 6,
    title: "Integration Techniques",
    content: "What are the different methods of integration? I'm finding substitution method particularly challenging.",
    author: "Anita Rao",
    category: "math-12",
    categoryLabel: "Class 12",
    timestamp: "2024-01-12T16:30:00Z",
    replies: 4,
    likes: 10
  }
];

// Initialize forum
document.addEventListener('DOMContentLoaded', function() {
  posts = [...samplePosts];
  displayPosts();
  updateStats();
});

function showNewTopicForm() {
  document.getElementById('new-topic-form').style.display = 'block';
  document.getElementById('topic-title').focus();
}

function hideNewTopicForm() {
  document.getElementById('new-topic-form').style.display = 'none';
  document.getElementById('new-topic-form').querySelector('form').reset();
}

function createNewTopic(event) {
  event.preventDefault();
  
  const category = document.getElementById('topic-category').value;
  const title = document.getElementById('topic-title').value;
  const content = document.getElementById('topic-content').value;
  
  // Get current user (check if logged in)
  const currentUser = localStorage.getItem('currentUser');
  let author = 'Anonymous User';
  
  if (currentUser) {
    const userData = JSON.parse(currentUser);
    author = userData.name || userData.email;
  }
  
  // Create new post
  const newPost = {
    id: posts.length + 1,
    title: title,
    content: content,
    author: author,
    category: category,
    categoryLabel: getCategoryLabel(category),
    timestamp: new Date().toISOString(),
    replies: 0,
    likes: 0
  };
  
  // Add to posts array
  posts.unshift(newPost);
  
  // Hide form and refresh display
  hideNewTopicForm();
  displayPosts();
  updateStats();
  
  // Show success message
  alert('Your discussion has been posted successfully!');
}

function getCategoryLabel(category) {
  const labels = {
    'math-9': 'Class 9',
    'math-10': 'Class 10',
    'math-11': 'Class 11',
    'math-12': 'Class 12',
    'general': 'General',
    'homework': 'Homework',
    'exam-prep': 'Exam Prep'
  };
  return labels[category] || 'General';
}

function showCategory(category) {
  currentCategory = category;
  currentPage = 1;
  
  // Update active button
  document.querySelectorAll('.category-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
  
  displayPosts();
}

function displayPosts() {
  const postsContainer = document.getElementById('forum-posts');
  let filteredPosts = posts;
  
  // Filter by category
  if (currentCategory !== 'all') {
    filteredPosts = posts.filter(post => post.category === currentCategory);
  }
  
  // Pagination
  const postsPerPage = 5;
  const startIndex = (currentPage - 1) * postsPerPage;
  const endIndex = startIndex + postsPerPage;
  const paginatedPosts = filteredPosts.slice(startIndex, endIndex);
  
  // Clear container
  postsContainer.innerHTML = '';
  
  // Display posts
  paginatedPosts.forEach(post => {
    const postElement = createPostElement(post);
    postsContainer.appendChild(postElement);
  });
  
  // Update pagination info
  const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
  document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
  
  // Update pagination buttons
  const prevBtn = document.querySelector('.pagination button:first-child');
  const nextBtn = document.querySelector('.pagination button:last-child');
  
  prevBtn.disabled = currentPage === 1;
  nextBtn.disabled = currentPage === totalPages || totalPages === 0;
}

function createPostElement(post) {
  const postDiv = document.createElement('div');
  postDiv.className = 'post-card';
  postDiv.onclick = () => openPost(post.id);
  
  const timeAgo = getTimeAgo(new Date(post.timestamp));
  
  postDiv.innerHTML = `
    <div class="post-header">
      <h3 class="post-title">${post.title}</h3>
      <span class="post-category">${post.categoryLabel}</span>
    </div>
    <div class="post-content">
      ${post.content}
    </div>
    <div class="post-meta">
      <div class="post-author">
        <span>👤 ${post.author}</span>
        <span>• ${timeAgo}</span>
      </div>
      <div class="post-stats">
        <span>💬 ${post.replies} replies</span>
        <span>👍 ${post.likes} likes</span>
      </div>
    </div>
  `;
  
  return postDiv;
}

function getTimeAgo(date) {
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  return `${Math.floor(diffInSeconds / 86400)} days ago`;
}

function openPost(postId) {
  const post = posts.find(p => p.id === postId);
  if (post) {
    alert(`Opening post: "${post.title}"\n\nThis would navigate to a detailed view of the post with replies and comments.`);
  }
}

function previousPage() {
  if (currentPage > 1) {
    currentPage--;
    displayPosts();
  }
}

function nextPage() {
  const postsPerPage = 5;
  let filteredPosts = posts;
  
  if (currentCategory !== 'all') {
    filteredPosts = posts.filter(post => post.category === currentCategory);
  }
  
  const totalPages = Math.ceil(filteredPosts.length / postsPerPage);
  
  if (currentPage < totalPages) {
    currentPage++;
    displayPosts();
  }
}

function updateStats() {
  // Update active users (simulated)
  document.getElementById('active-users').textContent = Math.floor(Math.random() * 50) + 20;
  
  // Update total posts
  document.getElementById('total-posts').textContent = posts.length;
}

// Simulate real-time updates
setInterval(() => {
  updateStats();
}, 30000); // Update every 30 seconds

document.addEventListener('DOMContentLoaded', () => {
    const forumInput = document.getElementById('forumInput');
    const forumSendBtn = document.getElementById('forumSendBtn');
    const forumUploadBtn = document.getElementById('forumUploadBtn');
    const forumMediaInput = document.getElementById('forumMediaInput');
    const forumMediaPreview = document.getElementById('forumMediaPreview');
    const forumMessages = document.getElementById('forumMessages');
    const emptyForumMsg = document.getElementById('emptyForumMsg');
    let selectedMediaFile = null;
    const API_URL = '/api/forum/messages';

    // Media upload logic
    forumUploadBtn.addEventListener('click', () => {
        forumMediaInput.click();
    });
    forumMediaInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        selectedMediaFile = file || null;
        forumMediaPreview.innerHTML = '';
        if (file) {
            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.style.maxWidth = '180px';
                img.style.maxHeight = '120px';
                img.style.borderRadius = '10px';
                img.onload = () => URL.revokeObjectURL(img.src);
                forumMediaPreview.appendChild(img);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.controls = true;
                video.style.maxWidth = '180px';
                video.style.maxHeight = '120px';
                video.style.borderRadius = '10px';
                video.onloadeddata = () => URL.revokeObjectURL(video.src);
                forumMediaPreview.appendChild(video);
            } else {
                forumMediaPreview.textContent = 'Unsupported file type.';
            }
        }
    });

    // Send message logic
    async function sendMessage() {
        const message = forumInput.value.trim();
        if (!message && !selectedMediaFile) return;
        forumSendBtn.disabled = true;
        try {
            let response;
            if (selectedMediaFile) {
                const formData = new FormData();
                formData.append('message', message);
                formData.append('media', selectedMediaFile);
                response = await fetch(API_URL, {
                    method: 'POST',
                    body: formData
                });
            } else {
                response = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
            }
            if (response.ok) {
                forumInput.value = '';
                selectedMediaFile = null;
                forumMediaInput.value = '';
                forumMediaPreview.innerHTML = '';
                fetchMessages();
            } else {
                alert('Failed to post message.');
            }
        } catch (error) {
            console.error('Error posting message:', error);
            alert('An error occurred. Please try again.');
        } finally {
            forumSendBtn.disabled = false;
        }
    }

    forumSendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        sendMessage();
    });
    forumInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function fetchMessages() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) throw new Error('Failed to fetch messages');
            const messages = await response.json();
            renderMessages(messages);
        } catch (error) {
            console.error('Error fetching messages:', error);
            forumMessages.innerHTML = '<div style="color:red; text-align:center;">Could not load messages.</div>';
        }
    }

    // Helper: get initials from username
    function getInitials(name) {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length === 1) return parts[0][0].toUpperCase();
        return (parts[0][0] + parts[parts.length-1][0]).toUpperCase();
    }
    // Helper: is this my message?
    function isOwnMessage(msg) {
        // You may want to compare with the logged-in username
        const myName = window.currentUsername || (window.username || '');
        return msg.username && myName && msg.username === myName;
    }
    // Helper: friendly time
    function friendlyTime(ts) {
        const date = new Date(ts);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000);
        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff/60)} min ago`;
        if (diff < 86400) return `${Math.floor(diff/3600)} hr ago`;
        return date.toLocaleString();
    }
    // Spinner
    function showSpinner() {
        forumMessages.innerHTML = '<div class="forum-spinner" aria-label="Loading messages"></div>';
    }
    // Auto-scroll
    function scrollToBottom() {
        forumMessages.scrollTop = forumMessages.scrollHeight;
    }
    // Emoji picker
    let emojiPicker = null;
    function showEmojiPicker() {
        if (emojiPicker) { emojiPicker.remove(); emojiPicker = null; return; }
        emojiPicker = document.createElement('div');
        emojiPicker.className = 'emoji-picker';
        emojiPicker.setAttribute('role', 'dialog');
        const emojis = ['😀','😂','😍','😎','👍','🙏','🎉','😢','😮','😡','❤️','🔥','🤔','😇','🥳','😅','😜','😏','😬','😱'];
        emojis.forEach(e => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = e;
            btn.onclick = () => {
                forumInput.value += e;
                forumInput.focus();
                emojiPicker.remove();
                emojiPicker = null;
            };
            emojiPicker.appendChild(btn);
        });
        document.querySelector('.chat-input-bar').appendChild(emojiPicker);
    }
    // Add emoji button
    let emojiBtn = document.getElementById('forumEmojiBtn');
    if (!emojiBtn) {
        emojiBtn = document.createElement('button');
        emojiBtn.id = 'forumEmojiBtn';
        emojiBtn.type = 'button';
        emojiBtn.className = 'btn btn-secondary';
        emojiBtn.style.padding = '0.5rem 0.8rem';
        emojiBtn.innerHTML = '<span style="font-size:1.3rem;">😊</span>';
        document.querySelector('.chat-input-bar').insertBefore(emojiBtn, forumInput);
    }
    emojiBtn.onclick = showEmojiPicker;
    // Drag & drop
    const chatInputBar = document.querySelector('.chat-input-bar');
    chatInputBar.addEventListener('dragover', e => { e.preventDefault(); chatInputBar.classList.add('dragover'); });
    chatInputBar.addEventListener('dragleave', e => { chatInputBar.classList.remove('dragover'); });
    chatInputBar.addEventListener('drop', e => {
        e.preventDefault();
        chatInputBar.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            forumMediaInput.files = e.dataTransfer.files;
            const event = new Event('change');
            forumMediaInput.dispatchEvent(event);
        }
    });
    // Simulate upload progress
    function showUploadProgress() {
        forumMediaPreview.innerHTML += '<div class="forum-upload-progress"><div class="forum-upload-progress-bar" style="width:0%"></div></div>';
        const bar = forumMediaPreview.querySelector('.forum-upload-progress-bar');
        let percent = 0;
        return setInterval(() => {
            percent += 10;
            bar.style.width = percent + '%';
            if (percent >= 100) clearInterval(progressIntv);
        }, 80);
    }
    // Render messages as chat bubbles
    function renderMessages(messages) {
        if (messages.length === 0) {
            emptyForumMsg.style.display = 'block';
            forumMessages.innerHTML = '';
        } else {
            emptyForumMsg.style.display = 'none';
            forumMessages.innerHTML = '';
            messages.forEach(msg => {
                const isOwn = isOwnMessage(msg);
                const postDiv = document.createElement('div');
                postDiv.className = 'forum-post';
                postDiv.setAttribute('role', 'listitem');
                // Avatar
                const avatar = document.createElement('div');
                avatar.className = 'forum-avatar';
                avatar.textContent = getInitials(msg.username);
                // Bubble
                const bubble = document.createElement('div');
                bubble.className = 'forum-bubble' + (isOwn ? ' own' : '');
                bubble.tabIndex = 0;
                // Username
                const uname = document.createElement('div');
                uname.style.fontWeight = '600';
                uname.style.fontSize = '1.01rem';
                uname.textContent = msg.username;
                bubble.appendChild(uname);
                // Message text
                const mtext = document.createElement('div');
                mtext.innerHTML = msg.message.replace(/\n/g, '<br>');
                bubble.appendChild(mtext);
                // Media (image/video)
                if (msg.media_url) {
                    if (msg.media_url.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
                        const img = document.createElement('img');
                        img.src = msg.media_url;
                        img.alt = 'attachment';
                        img.style.maxWidth = '180px';
                        img.style.maxHeight = '120px';
                        img.style.borderRadius = '10px';
                        img.style.marginTop = '0.5rem';
                        bubble.appendChild(img);
                    } else if (msg.media_url.match(/\.(mp4|webm|ogg)$/i)) {
                        const video = document.createElement('video');
                        video.src = msg.media_url;
                        video.controls = true;
                        video.style.maxWidth = '180px';
                        video.style.maxHeight = '120px';
                        video.style.borderRadius = '10px';
                        video.style.marginTop = '0.5rem';
                        bubble.appendChild(video);
                    }
                }
                // Timestamp
                const ts = document.createElement('span');
                ts.className = 'forum-timestamp';
                ts.textContent = friendlyTime(msg.timestamp);
                bubble.appendChild(ts);
                // Reply/quote UI
                if (msg.reply_to) {
                    const reply = document.createElement('div');
                    reply.className = 'forum-reply';
                    reply.textContent = msg.reply_to;
                    bubble.insertBefore(reply, mtext);
                }
                // Link preview (UI only)
                const urlMatch = msg.message.match(/https?:\/\/[\w\.-]+(\.[\w\.-]+)+[\w\-\._~:/?#[\]@!$&'()*+,;=.]+/);
                if (urlMatch) {
                    const preview = document.createElement('div');
                    preview.className = 'forum-link-preview';
                    preview.style.marginTop = '0.4rem';
                    preview.style.fontSize = '0.97rem';
                    preview.innerHTML = `<a href="${urlMatch[0]}" target="_blank" rel="noopener">${urlMatch[0]}</a>`;
                    bubble.appendChild(preview);
                }
                // Actions (edit/delete for own)
                if (isOwn) {
                    const actions = document.createElement('div');
                    actions.className = 'forum-actions-bar';
                    const editBtn = document.createElement('button');
                    editBtn.className = 'forum-action-btn';
                    editBtn.textContent = 'Edit';
                    editBtn.title = 'Edit message';
                    editBtn.onclick = () => alert('Edit not implemented yet');
                    const delBtn = document.createElement('button');
                    delBtn.className = 'forum-action-btn';
                    delBtn.textContent = 'Delete';
                    delBtn.title = 'Delete message';
                    delBtn.onclick = () => alert('Delete not implemented yet');
                    actions.appendChild(editBtn);
                    actions.appendChild(delBtn);
                    bubble.appendChild(actions);
                }
                // Reply button
                const replyBtn = document.createElement('button');
                replyBtn.className = 'forum-action-btn reply-btn';
                replyBtn.textContent = 'Reply';
                replyBtn.title = 'Reply to this message';
                replyBtn.onclick = () => alert('Reply not implemented yet');
                bubble.appendChild(replyBtn);
                // Layout: own messages right, others left
                if (isOwn) {
                    postDiv.appendChild(bubble);
                    postDiv.appendChild(avatar);
                } else {
                    postDiv.appendChild(avatar);
                    postDiv.appendChild(bubble);
                }
                forumMessages.appendChild(postDiv);
            });
            scrollToBottom();
        }
    }

    fetchMessages();
    setInterval(fetchMessages, 30000);

    const toggleBtn = document.getElementById('darkModeToggle');
      function setDarkMode(on) {
        if (on) {
          document.body.classList.add('dark-mode');
          localStorage.setItem('darkMode', 'on');
        } else {
          document.body.classList.remove('dark-mode');
          localStorage.setItem('darkMode', 'off');
        }
      }
      toggleBtn.addEventListener('click', () => {
        setDarkMode(!document.body.classList.contains('dark-mode'));
      });
      if (localStorage.getItem('darkMode') === 'on') {
        document.body.classList.add('dark-mode');
      }
});
