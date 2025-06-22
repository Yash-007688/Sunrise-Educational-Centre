
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
