(function () {
  'use strict';
  var launch = document.querySelector('.walkthrough-launch');
  if (!launch) return;
  launch.addEventListener('click', function (event) {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    var player = document.createElement('iframe');
    player.title = 'DTT Ireland app walkthrough — narrated feature guide';
    player.src = 'https://www.youtube-nocookie.com/embed/NdzdM7hs1Lg?autoplay=1&rel=0';
    player.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    player.allowFullscreen = true;
    player.referrerPolicy = 'strict-origin-when-cross-origin';
    document.getElementById('walkthrough-player').replaceChildren(player);
    player.focus();
  });
})();
