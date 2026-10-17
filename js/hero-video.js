(function () {
  var video = document.getElementById("hero-video");
  if (!video || !video.dataset.src) return;

  var source = document.createElement("source");
  source.src = video.dataset.src;
  source.type = "video/mp4";
  video.appendChild(source);

  var still = video.parentElement && video.parentElement.querySelector(".hero-still");
  video.addEventListener("playing", function () {
    if (still) still.style.opacity = "0";
  });

  var start = function () {
    var play = video.play();
    if (play && play.catch) play.catch(function () {});
  };
  if (video.readyState >= 2) start();
  else video.addEventListener("canplay", start, { once: true });
  video.load();
})();
