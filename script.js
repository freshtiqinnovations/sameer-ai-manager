/* ========================================
   FRESHTIQ AUTOMATION - JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', function() {

  // ============= NAV SCROLL EFFECT =============
  const nav = document.querySelector('nav');
  if (nav) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
    });
  }

  // ============= HAMBURGER MENU =============
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
      });
    });
  }

  // ============= FADE-IN ON SCROLL =============
  const fadeElements = document.querySelectorAll('.fade-in');
  if (fadeElements.length) {
    const fadeObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          fadeObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    fadeElements.forEach(function(el) {
      fadeObserver.observe(el);
    });
  }

  // ============= TESTIMONIAL CAROUSEL =============
  const track = document.querySelector('.testimonials-track');
  const dots = document.querySelectorAll('.dot');
  const prevBtn = document.querySelector('.testimonial-arrow.prev');
  const nextBtn = document.querySelector('.testimonial-arrow.next');
  let currentIndex = 0;

  function updateCarousel() {
    if (!track) return;
    var totalSlides = track.children.length;
    if (totalSlides === 0) return;
    if (currentIndex < 0) currentIndex = totalSlides - 1;
    if (currentIndex >= totalSlides) currentIndex = 0;
    track.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';

    dots.forEach(function(d, i) {
      d.classList.toggle('active', i === currentIndex);
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      currentIndex--;
      updateCarousel();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      currentIndex++;
      updateCarousel();
    });
  }

  dots.forEach(function(dot, i) {
    dot.addEventListener('click', function() {
      currentIndex = i;
      updateCarousel();
    });
  });

  // Auto-rotate carousel
  var autoRotate;
  if (track && track.children.length > 1) {
    autoRotate = setInterval(function() {
      currentIndex++;
      updateCarousel();
    }, 5000);

    // Pause on hover
    var slider = document.querySelector('.testimonials-slider');
    if (slider) {
      slider.addEventListener('mouseenter', function() {
        clearInterval(autoRotate);
      });
      slider.addEventListener('mouseleave', function() {
        autoRotate = setInterval(function() {
          currentIndex++;
          updateCarousel();
        }, 5000);
      });
    }
  }

  // Initialize
  updateCarousel();

  // ============= COPY BUTTONS =============
  document.querySelectorAll('.copy-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var target = this.getAttribute('data-copy');
      if (target) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(target).then(function() {
            var original = btn.textContent;
            btn.textContent = 'Copied!';
            setTimeout(function() {
              btn.textContent = original;
            }, 2000);
          });
        } else {
          // Fallback
          var textarea = document.createElement('textarea');
          textarea.value = target;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
          var original = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(function() {
            btn.textContent = original;
          }, 2000);
        }
      }
    });
  });

});
