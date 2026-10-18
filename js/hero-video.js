(function () {
  var video = document.getElementById("hero-video");
  if (!video || !video.dataset.src) return;

  var still = video.parentElement && video.parentElement.querySelector(".hero-still");

  function reveal() {
    if (still) still.style.opacity = "0";
  }

  video.muted = true;
  video.defaultMuted = true;
  video.playsInline = true;
  video.setAttribute("muted", "");
  video.setAttribute("playsinline", "");
  video.setAttribute("webkit-playsinline", "");
  video.autoplay = true;
  video.preload = "auto";
  video.src = video.dataset.src;

  video.addEventListener("playing", reveal);
  video.addEventListener("timeupdate", function () {
    if (video.currentTime > 0) reveal();
  });

  function start() {
    var play = video.play();
    if (play && play.catch) play.catch(function () {});
  }

  start();
  video.addEventListener("loadeddata", start);
  video.addEventListener("canplay", start);

  function kick() {
    if (video.paused) start();
  }
  document.addEventListener("touchstart", kick, { passive: true });
  document.addEventListener("click", kick);
})();
