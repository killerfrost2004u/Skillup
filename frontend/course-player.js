/* frontend/course-player.js */

// Global variables initialized by track pages
// const API_KEY = "...";
// const PLAYLIST_ID = "...";

let player;
let lectures = [];
let currentIndex = 0;
let currentUser = null;
let progressCheckInterval;
let maxPercentageSeen = 0;

const videoIframe = document.getElementById("video-iframe");
const lectureList = document.getElementById("lecture-list");
const backBtn = document.getElementById("back-btn");
const nextBtn = document.getElementById("next-btn");
const toggleTheme = document.getElementById("toggle-theme");
const completionModal = document.getElementById("completion-modal");

// Load YouTube IFrame API
const tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// This function fires when API is ready
function onYouTubeIframeAPIReady() {
    // Initial player will be loaded once playlist is fetched
}

function initializePlayer(videoId) {
    if (player) {
        player.loadVideoById(videoId);
        return;
    }

    player = new YT.Player('video-iframe', {
        height: '450',
        width: '100%',
        videoId: videoId,
        playerVars: {
            'playsinline': 1,
            'modestbranding': 1,
            'rel': 0
        },
        events: {
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.PLAYING) {
        startProgressTracking();
    } else {
        stopProgressTracking();
    }
}

function startProgressTracking() {
    stopProgressTracking();
    progressCheckInterval = setInterval(() => {
        if (!player || !player.getCurrentTime) return;

        const currentTime = player.getCurrentTime();
        const duration = player.getDuration();
        if (duration > 0) {
            const percentage = (currentTime / duration) * 100;
            
            // Update circle only if it's the current video's progress (visual feedback)
            // But we specifically want the circle to reflect TOTAL course progress.
            // The requirement says: "circle dynamic based on how much you saw in this course"
            
            if (percentage > maxPercentageSeen) {
                maxPercentageSeen = percentage;
            }

            if (percentage >= 90) {
                markCurrentVideoCompleted();
            }
        }
    }, 1000);
}

function stopProgressTracking() {
    clearInterval(progressCheckInterval);
}

function markCurrentVideoCompleted() {
    const lecture = lectures[currentIndex];
    if (lecture && lecture.dataset.completed !== "true") {
        lecture.setAttribute("data-completed", "true");
        lecture.querySelector('.lecture-check i').style.color = '#4CAF50';
        saveVideoProgress(lecture.dataset.video, true);
        updateProgressCircle();
        unlockSequentialLectures();

        if ([...lectures].every((li) => li.dataset.completed === "true")) {
            completionModal.style.display = "block";
        }
    }
}

function unlockSequentialLectures() {
    lectures.forEach((lecture, index) => {
        if (index === 0) {
            lecture.classList.remove('locked');
        } else {
            const prevLecture = lectures[index - 1];
            if (prevLecture && prevLecture.dataset.completed === "true") {
                lecture.classList.remove('locked');
            } else {
                lecture.classList.add('locked');
            }
        }
    });
}

// User Management
function getCurrentUser() {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
}

async function checkVideoAccess() {
    const response = await fetchWithAuth(`/api/check-video-access/${PLAYLIST_ID}`);
    if (response && response.ok) {
        const data = await response.json();
        return data.has_access === true;
    }
    return false;
}

function redirectToLogin() {
    localStorage.setItem('redirect_url', window.location.href);
    window.location.href = 'log.html?show=register';
}

function showAccessModal() {
    let modal = document.getElementById('access-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'access-modal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3><i class="fas fa-lock"></i> Restricted Content</h3>
                <p>You need to be logged in to watch this video.</p>
                <div class="modal-buttons">
                    <button id="login-redirect-btn" class="modal-btn">
                        <i class="fas fa-sign-in-alt"></i> Login / Register
                    </button>
                    <button id="close-access-modal" class="modal-btn" style="background: #666;">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('login-redirect-btn').addEventListener('click', redirectToLogin);
        document.getElementById('close-access-modal').addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    modal.style.display = 'block';
}

async function loadVideoWithProtection(videoId) {
    const hasAccess = await checkVideoAccess();
    const overlay = document.getElementById('video-overlay');

    if (!hasAccess) {
        if (!overlay) {
            const newOverlay = document.createElement('div');
            newOverlay.id = 'video-overlay';
            newOverlay.className = 'video-overlay';
            newOverlay.innerHTML = `
                <i class="fas fa-lock"></i>
                <h3>Content Locked</h3>
                <p>Login or register to unlock this video</p>
                <div class="overlay-buttons">
                    <button onclick="redirectToLogin()" class="overlay-btn">
                        <i class="fas fa-sign-in-alt"></i> Login to Unlock
                    </button>
                </div>
            `;
            document.querySelector('.video-player').appendChild(newOverlay);
        } else {
            overlay.style.display = 'flex';
        }
        
        document.querySelectorAll('.lecture-item').forEach(item => item.classList.add('locked'));
        backBtn.disabled = true;
        nextBtn.disabled = true;
        return false;
    } else {
        if (overlay) overlay.style.display = 'none';
        initializePlayer(videoId);
        unlockSequentialLectures();
        backBtn.disabled = false;
        nextBtn.disabled = false;
        return true;
    }
}

async function saveVideoProgress(videoId, completed = false) {
    const user = getCurrentUser();
    if (!user || !user.user_id) return;

    try {
        await fetch(`${API_BASE_URL}/api/progress/save`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: user.user_id,
                playlist_id: PLAYLIST_ID,
                video_id: videoId,
                completed: completed
            })
        });
    } catch (error) {
        console.error('Error saving progress:', error);
    }
}

async function loadVideoProgress() {
    const user = getCurrentUser();
    if (user && user.user_id) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/progress/${user.user_id}/${PLAYLIST_ID}`);
            const data = await response.json();
            if (data.success) return data.videos || {};
        } catch (error) {
            console.error('Error loading progress:', error);
        }
    }
    return {};
}

async function initializeProgress() {
    currentUser = getCurrentUser();
    const savedProgress = await loadVideoProgress();

    lectures.forEach((lecture) => {
        const videoId = lecture.dataset.video;
        if (savedProgress[videoId] && savedProgress[videoId].completed) {
            lecture.setAttribute("data-completed", "true");
            lecture.querySelector('.lecture-check i').style.color = '#4CAF50';
        }
    });

    unlockSequentialLectures();
    updateProgressCircle();
}

function formatDuration(duration) {
    const match = duration.match(/PT(\d+H)?(\d+M)?(\d+S)?/);
    const hours = match[1] ? parseInt(match[1].replace("H","")) : 0;
    const minutes = match[2] ? parseInt(match[2].replace("M","")) : 0;
    const seconds = match[3] ? parseInt(match[3].replace("S","")) : 0;
    return hours > 0 
        ? `${hours}:${minutes.toString().padStart(2,"0")}:${seconds.toString().padStart(2,"0")}`
        : `${minutes}:${seconds.toString().padStart(2,"0")}`;
}

async function fetchPlaylistVideos() {
    let videos = [];
    let nextPageToken = "";
    try {
        do {
            const res = await fetch(`https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=${PLAYLIST_ID}&key=${API_KEY}&pageToken=${nextPageToken}`);
            const data = await res.json();
            const videoIds = data.items.map(item => item.snippet.resourceId.videoId).join(",");
            const detailsRes = await fetch(`https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=${videoIds}&key=${API_KEY}`);
            const detailsData = await detailsRes.json();

            data.items.forEach((item, i) => {
                const durationISO = detailsData.items[i].contentDetails.duration;
                videos.push({
                    title: item.snippet.title,
                    videoId: item.snippet.resourceId.videoId,
                    duration: formatDuration(durationISO),
                });
            });
            nextPageToken = data.nextPageToken || "";
        } while (nextPageToken);
    } catch (err) { console.error("YouTube API Error:", err); }
    return videos;
}

function populateLectureList(videos) {
    lectureList.innerHTML = "";
    videos.forEach((video, i) => {
        const li = document.createElement("li");
        li.className = "lecture-item";
        li.dataset.video = video.videoId;
        li.dataset.duration = video.duration;
        li.dataset.completed = "false";
        li.innerHTML = `
            <div class="lecture-icon"><i class="fas fa-play"></i></div>
            <div class="lecture-details">
                <span class="lecture-title">${video.title}</span>
                <span class="lecture-duration">${video.duration}</span>
            </div>
            <div class="lecture-check"><i class="fas fa-check"></i></div>
        `;
        li.addEventListener("click", () => {
            if (li.classList.contains('locked')) {
                alert("Please finish the previous video first!");
                return;
            }
            updateActiveLecture(i);
        });
        lectureList.appendChild(li);
    });
    lectures = document.querySelectorAll(".lecture-item");
}

async function updateActiveLecture(index) {
    const hasAccess = await checkVideoAccess();
    if (!hasAccess) {
        showAccessModal();
        return;
    }
    
    lectures.forEach((item, i) => item.classList.toggle("active", i === index));
    currentIndex = index;
    maxPercentageSeen = 0; // Reset for new video
    await loadVideoWithProtection(lectures[index].dataset.video);
}

async function updateProgressCircle() {
    const completed = document.querySelectorAll('.lecture-item[data-completed="true"]').length;
    const percent = lectures.length > 0 ? Math.round((completed / lectures.length) * 100) : 0;
    
    const circle = document.querySelector(".progress-circle circle:nth-child(2)");
    if (circle) {
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDashoffset = offset;
    }
    
    const text = document.getElementById("progress-text-circle");
    if (text) text.textContent = percent + "%";

    // Save overall progress to database
    const user = getCurrentUser();
    if (user && user.user_id) {
        try {
            await fetch(`${API_BASE_URL}/api/progress/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user.user_id,
                    playlist_id: PLAYLIST_ID,
                    overall_progress: percent,
                    completed_videos: completed,
                    total_videos: lectures.length
                })
            });
        } catch (error) { console.error('Error saving overall progress:', error); }
    }
}

// Event Listeners
backBtn.addEventListener("click", () => {
    if (currentIndex > 0) updateActiveLecture(currentIndex - 1);
});

nextBtn.addEventListener("click", () => {
    if (currentIndex < lectures.length - 1) {
        if (lectures[currentIndex + 1].classList.contains('locked')) {
            alert("Please watch at least 90% of the current video to unlock the next one!");
            return;
        }
        updateActiveLecture(currentIndex + 1);
    }
});

toggleTheme.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    toggleTheme.innerHTML = document.body.classList.contains("dark-mode")
      ? '<i class="fas fa-sun"></i> Light Mode'
      : '<i class="fas fa-moon"></i> Night Mode';
});

// Initialization
document.addEventListener('DOMContentLoaded', async function() {
    currentUser = getCurrentUser();
    const hasAccess = await checkVideoAccess();

    const videos = await fetchPlaylistVideos();
    populateLectureList(videos);
    
    if (lectures.length > 0) {
        if (hasAccess) {
            await initializeProgress();
            // Start with first video
            updateActiveLecture(0);
        } else {
            loadVideoWithProtection(lectures[0].dataset.video);
        }
    }
});
