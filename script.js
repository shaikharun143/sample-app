// script.js
document.addEventListener('DOMContentLoaded', () => {
  // Select elements to animate (e.g., feature cards)
  const animateOnScroll = document.querySelectorAll('.feature-card');

  // Intersection Observer callback
  const observerCallback = (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
        // Optionally unobserve if one-time animation
        observer.unobserve(entry.target);
      }
    });
  };

  // Set up observer
  const observerOptions = {
    threshold: 0.1
  };
  const observer = new IntersectionObserver(observerCallback, observerOptions);
  animateOnScroll.forEach(elem => observer.observe(elem));
});
