const teamMembers = [
	{ name: "Front-End Developer", role: "Web Development" },
	{ name: "Back-End Developer", role: "Lead Server & Database" },
	{ name: "Software Development ", role: "Full Stack Skills" },
	{ name:"Python Programming", role: "Programming Basics"  },

	
];

const cards = document.querySelectorAll(".card");
const dots = document.querySelectorAll(".dot");
const memberName = document.querySelector(".member-name");
const memberRole = document.querySelector(".member-role");
const upArrows = document.querySelectorAll(".nav-arrow.up");
const downArrows = document.querySelectorAll(".nav-arrow.down");
let currentIndex = 0;
let isAnimating = false;

function updateCarousel(newIndex) {
	if (isAnimating) return;
	isAnimating = true;

	currentIndex = (newIndex + cards.length) % cards.length;

	cards.forEach((card, i) => {
		const offset = (i - currentIndex + cards.length) % cards.length;

		card.classList.remove(
			"center",
			"up-1",
			"up-2",
			"down-1",
			"down-2",
			"hidden"
		);

		if (offset === 0) {
			card.classList.add("center");
		} else if (offset === 1) {
			card.classList.add("down-1");
		} else if (offset === 2) {
			card.classList.add("down-2");
		} else if (offset === cards.length - 1) {
			card.classList.add("up-1");
		} else if (offset === cards.length - 2) {
			card.classList.add("up-2");
		} else {
			card.classList.add("hidden");
		}
	});

	dots.forEach((dot, i) => {
		dot.classList.toggle("active", i === currentIndex);
	});

	memberName.style.opacity = "0";
	memberRole.style.opacity = "0";

	setTimeout(() => {
		memberName.textContent = teamMembers[currentIndex].name;
		memberRole.textContent = teamMembers[currentIndex].role;
		memberName.style.opacity = "1";
		memberRole.style.opacity = "1";
	}, 300);

	setTimeout(() => {
		isAnimating = false;
	}, 800);
}

upArrows.forEach(arrow => {
	arrow.addEventListener("click", () => {
		updateCarousel(currentIndex - 1);
	});
});

downArrows.forEach(arrow => {
	arrow.addEventListener("click", () => {
		updateCarousel(currentIndex + 1);
	});
});

dots.forEach((dot, i) => {
	dot.addEventListener("click", () => {
		updateCarousel(i);
	});
});

cards.forEach((card, i) => {
	card.addEventListener("click", () => {
		updateCarousel(i);
	});
});

document.addEventListener("keydown", (e) => {
	if (e.key === "ArrowUp") {
		updateCarousel(currentIndex - 1);
	} else if (e.key === "ArrowDown") {
		updateCarousel(currentIndex + 1);
	}
});

let touchStartX = 0;
let touchEndX = 0;
let scrollTimeout;
let isScrolling = false;

// Scroll event listener
//if u wnat u can timer to disappear that bottom right scroll button - by gopi
	
	

// Add scroll indicator
function createScrollIndicator() {
	const indicator = document.createElement('div');
	indicator.className = 'scroll-indicator';
	indicator.innerHTML = 'scroll';
	document.body.appendChild(indicator);
}

// Initialize scroll indicator
createScrollIndicator();

document.addEventListener("touchstart", (e) => {
	touchStartX = e.changedTouches[0].screenY;
});

document.addEventListener("touchend", (e) => {
	touchEndX = e.changedTouches[0].screenY;
	handleSwipe();
});

function handleSwipe() {
	const swipeThreshold = 50;
	const diff = touchStartX - touchEndX;

	if (Math.abs(diff) > swipeThreshold) {
		if (diff > 0) {
			updateCarousel(currentIndex + 1);
		} else {
			updateCarousel(currentIndex - 1);
		}
	}
}

updateCarousel(0);













const canvas = document.getElementById("bg");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];

class Particle {
  constructor(x, y, size, color, speedX, speedY) {
    this.x = x;
    this.y = y;
    this.size = size;
    this.color = color;
    this.speedX = speedX;
    this.speedY = speedY;
  }
  update() {
    this.x += this.speedX;
    this.y += this.speedY;
    if (this.size > 0.2) this.size -= 0.02;
  }
  draw() {
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
  }
}

function handleParticles() {
  for (let i = 0; i < particles.length; i++) {
    particles[i].update();
    particles[i].draw();
    if (particles[i].size <= 0.3) {
      particles.splice(i, 1);
      i--;
    }
  }
}

canvas.addEventListener("mousemove", (event) => {
  for (let i = 0; i < 5; i++) {
    particles.push(
      new Particle(
        event.x,
        event.y,
        Math.random() * 5 + 2,
        "rgba(255, 255, 255, 0.8)",
        (Math.random() - 0.5) * 2,
        (Math.random() - 0.5) * 2
      )
    );
  }
});

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  handleParticles();
  requestAnimationFrame(animate);
}
animate();

window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});










