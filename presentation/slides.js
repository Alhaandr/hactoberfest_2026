let currentSlideIndex = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;

const slideIndicator = document.getElementById('slide-indicator');
const progressBar = document.getElementById('progress-bar');
const btnPrev = document.getElementById('btn-prev');
const btnNext = document.getElementById('btn-next');

function updateSlide(newIndex) {
  if (newIndex < 0 || newIndex >= totalSlides) return;

  slides[currentSlideIndex].classList.remove('active');
  currentSlideIndex = newIndex;
  slides[currentSlideIndex].classList.add('active');

  // Update Indicator & Progress Bar
  slideIndicator.textContent = `Slide ${currentSlideIndex + 1} of ${totalSlides}`;
  const percentage = ((currentSlideIndex + 1) / totalSlides) * 100;
  progressBar.style.width = `${percentage}%`;

  // Button states
  btnPrev.disabled = currentSlideIndex === 0;
  btnNext.innerHTML = currentSlideIndex === totalSlides - 1 ? 'Finish' : `
    Next
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
  `;
}

function nextSlide() {
  if (currentSlideIndex < totalSlides - 1) {
    updateSlide(currentSlideIndex + 1);
  }
}

function prevSlide() {
  if (currentSlideIndex > 0) {
    updateSlide(currentSlideIndex - 1);
  }
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      console.warn(`Fullscreen error: ${err.message}`);
    });
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}

// Event Listeners
btnNext.addEventListener('click', nextSlide);
btnPrev.addEventListener('click', prevSlide);

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
    e.preventDefault();
    nextSlide();
  } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
    e.preventDefault();
    prevSlide();
  } else if (e.key === 'Home') {
    e.preventDefault();
    updateSlide(0);
  } else if (e.key === 'End') {
    e.preventDefault();
    updateSlide(totalSlides - 1);
  } else if (e.key.toLowerCase() === 'f') {
    e.preventDefault();
    toggleFullscreen();
  }
});

// Initialize First Slide State
updateSlide(0);

