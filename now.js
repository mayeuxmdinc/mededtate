(function () {
  'use strict';

  // ===== State =====
  var currentPhase = 'entry';
  var timers = [];
  var soundOn = false;
  var currentAudio = null;

  // ===== Audio =====
  var btnSound = document.getElementById('btn-sound');
  var iconOn = document.getElementById('icon-sound-on');
  var iconOff = document.getElementById('icon-sound-off');

  if (btnSound) {
    soundOn = true;
    btnSound.addEventListener('click', function () {
      soundOn = !soundOn;
      btnSound.classList.toggle('active', soundOn);
      iconOn.style.display = soundOn ? 'block' : 'none';
      iconOff.style.display = soundOn ? 'none' : 'block';
      if (!soundOn && currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
    });
  }

  function playAudio(file) {
    if (!soundOn) return;
    if (currentAudio) {
      currentAudio.pause();
    }
    currentAudio = new Audio('audio/' + file);
    currentAudio.play().catch(function () {});
  }

  function stopAudio() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
  }

  function clearAllTimers() {
    timers.forEach(function (t) { clearTimeout(t); clearInterval(t); });
    timers = [];
    stopAudio();
  }

  // ===== Nav =====
  var btnBack = document.getElementById('btn-back');

  function updateNav(phase) {
    // Show back button on exercise screens and check-in
    var showBack = (phase === 'breathe' || phase === 'ground' || phase === 'scan' || phase === 'checkin');
    btnBack.style.display = showBack ? 'flex' : 'none';
  }

  btnBack.addEventListener('click', function () {
    showPhase('select');
  });

  // ===== Phase Transitions =====
  function showPhase(id) {
    clearAllTimers();
    document.querySelectorAll('.phase').forEach(function (el) {
      el.classList.remove('active');
    });
    var target = document.getElementById('phase-' + id);
    if (target) {
      target.classList.add('active');
    }
    currentPhase = id;
    updateNav(id);
  }

  // ===== Phase 0: Entry =====
  var btnReady = document.getElementById('btn-ready');
  btnReady.addEventListener('click', function () {
    showPhase('select');
  });

  // Auto-advance after 4 seconds
  var autoAdvance = setTimeout(function () {
    if (currentPhase === 'entry') {
      showPhase('select');
    }
  }, 4000);
  timers.push(autoAdvance);

  // ===== Phase 1: Mode Select =====
  document.querySelectorAll('.mode-card').forEach(function (card) {
    card.addEventListener('click', function () {
      var mode = card.getAttribute('data-mode');
      if (mode === 'breathe') startBreathing();
      else if (mode === 'ground') startGrounding();
      else if (mode === 'scan') startBodyScan();
    });
  });

  // ===== Phase 2A: Breathing =====
  function startBreathing() {
    showPhase('breathe');

    var circle = document.getElementById('breath-circle');
    var label = document.getElementById('breath-label');
    var count = document.getElementById('breath-count');
    var roundEl = document.getElementById('breath-round');
    var progress = document.getElementById('breath-progress');

    var phases = [
      { name: 'Inhale', css: 'inhale', duration: 4 },
      { name: 'Hold', css: 'hold-in', duration: 4 },
      { name: 'Exhale', css: 'exhale', duration: 4 },
      { name: 'Hold', css: 'hold-out', duration: 4 }
    ];

    var totalRounds = 5;
    var round = 0;
    var phaseIdx = 0;
    var totalPhases = totalRounds * phases.length;
    var completedPhases = 0;

    function runPhase() {
      if (round >= totalRounds) {
        showPhase('checkin');
        resetCheckin();
        return;
      }

      var p = phases[phaseIdx];
      label.textContent = p.name;
      circle.className = 'breath-circle ' + p.css;
      roundEl.textContent = 'Round ' + (round + 1) + ' of ' + totalRounds;

      // Voice cues
      if (p.css === 'inhale') playAudio('breathe_inhale.mp3');
      else if (p.css === 'exhale') playAudio('breathe_exhale.mp3');
      else if (p.css === 'hold-in' || p.css === 'hold-out') playAudio('breathe_hold.mp3');

      var sec = p.duration;
      count.textContent = sec;

      var countDown = setInterval(function () {
        sec--;
        if (sec > 0) {
          count.textContent = sec;
        }
      }, 1000);
      timers.push(countDown);

      var next = setTimeout(function () {
        clearInterval(countDown);
        completedPhases++;
        progress.style.width = ((completedPhases / totalPhases) * 100) + '%';

        phaseIdx++;
        if (phaseIdx >= phases.length) {
          phaseIdx = 0;
          round++;
        }
        runPhase();
      }, p.duration * 1000);
      timers.push(next);
    }

    progress.style.width = '0%';
    runPhase();
  }

  // ===== Phase 2B: Grounding =====
  function startGrounding() {
    showPhase('ground');

    var promptEl = document.getElementById('ground-prompt');
    var dotsEl = document.getElementById('ground-dots');

    var prompts = [
      'Name 5 things you can see right now.',
      'Name 4 things you can physically feel.',
      'Name 3 things you can hear.',
      'Name 2 things you can smell.',
      'Name 1 thing you can taste.',
      'Good. You\'re here. You\'re present.'
    ];

    // Build dots
    dotsEl.innerHTML = '';
    prompts.forEach(function () {
      var dot = document.createElement('span');
      dot.className = 'ground-dot';
      dotsEl.appendChild(dot);
    });
    var dots = dotsEl.querySelectorAll('.ground-dot');

    var idx = 0;

    function showPrompt() {
      if (idx >= prompts.length) {
        // Done
        var finishTimer = setTimeout(function () {
          showPhase('checkin');
          resetCheckin();
        }, 4000);
        timers.push(finishTimer);
        return;
      }

      promptEl.classList.remove('fade-out');
      promptEl.textContent = prompts[idx];
      dots[idx].classList.add('active');
      playAudio('ground_' + (idx + 1) + '.mp3');

      // Mark previous as done
      if (idx > 0) {
        dots[idx - 1].classList.remove('active');
        dots[idx - 1].classList.add('done');
      }

      var advanceTimer = setTimeout(function () {
        promptEl.classList.add('fade-out');
        var fadeTimer = setTimeout(function () {
          idx++;
          showPrompt();
        }, 500);
        timers.push(fadeTimer);
      }, 10000);
      timers.push(advanceTimer);
    }

    showPrompt();
  }

  // ===== Phase 2C: Body Scan =====
  function startBodyScan() {
    showPhase('scan');

    var instructionEl = document.getElementById('scan-instruction');

    var regions = [
      { id: 'feet', text: 'Bring your attention to your feet. Notice any tension. Let it soften.' },
      { id: 'legs', text: 'Move your awareness up to your legs. Let any tightness release.' },
      { id: 'abdomen', text: 'Focus on your abdomen. Notice it rise and fall with each breath.' },
      { id: 'chest', text: 'Bring attention to your chest. Let your breathing be natural and easy.' },
      { id: 'shoulders', text: 'Notice your shoulders. Let them drop. Release the weight you carry.' },
      { id: 'face', text: 'Soften your face. Unclench your jaw. Let your forehead relax.' }
    ];

    var idx = 0;

    function clearRegions() {
      document.querySelectorAll('.body-part').forEach(function (el) {
        el.classList.remove('active');
      });
    }

    function highlightRegion(regionId) {
      clearRegions();
      document.querySelectorAll('.body-part[data-region="' + regionId + '"]').forEach(function (el) {
        el.classList.add('active');
      });
    }

    function showRegion() {
      if (idx >= regions.length) {
        clearRegions();
        instructionEl.textContent = 'Well done. Your whole body has been heard.';
        playAudio('scan_done.mp3');
        var finishTimer = setTimeout(function () {
          showPhase('checkin');
          resetCheckin();
        }, 4000);
        timers.push(finishTimer);
        return;
      }

      var r = regions[idx];
      instructionEl.classList.remove('fade-out');
      instructionEl.textContent = r.text;
      highlightRegion(r.id);
      playAudio('scan_' + r.id + '.mp3');

      var advanceTimer = setTimeout(function () {
        instructionEl.classList.add('fade-out');
        var fadeTimer = setTimeout(function () {
          idx++;
          showRegion();
        }, 500);
        timers.push(fadeTimer);
      }, 20000);
      timers.push(advanceTimer);
    }

    showRegion();
  }

  // ===== Phase 3: Closing Check-in =====
  var responses = [
    'That\'s okay. Try another exercise, or tell your nurse.',
    'It takes time. Keep breathing slowly.',
    'You\'re doing well. Take a moment.',
    'That\'s great progress. Keep it going.',
    'Wonderful. You found your center.'
  ];

  function resetCheckin() {
    document.getElementById('checkin-response').textContent = '';
    document.getElementById('btn-another').style.display = 'none';
    document.getElementById('checkin-nurse').style.display = 'none';
    document.querySelectorAll('.checkin-emoji').forEach(function (btn) {
      btn.classList.remove('selected');
      btn.disabled = false;
    });
  }

  document.getElementById('checkin-emojis').addEventListener('click', function (e) {
    var btn = e.target.closest('.checkin-emoji');
    if (!btn) return;

    var level = parseInt(btn.getAttribute('data-level'), 10);

    document.querySelectorAll('.checkin-emoji').forEach(function (b) {
      b.classList.remove('selected');
      b.disabled = true;
    });
    btn.classList.add('selected');

    document.getElementById('checkin-response').textContent = responses[level - 1];
    document.getElementById('btn-another').style.display = 'inline-block';
    document.getElementById('checkin-nurse').style.display = 'block';
  });

  document.getElementById('btn-another').addEventListener('click', function () {
    showPhase('select');
  });

})();
