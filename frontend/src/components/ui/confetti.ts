import confetti from 'canvas-confetti'

// ========================================
// Confetti Celebrations
// ========================================

// Standard celebration burst
export function celebrateSuccess() {
  const count = 200
  const defaults = {
    origin: { y: 0.7 },
    zIndex: 9999,
  }

  function fire(particleRatio: number, opts: confetti.Options) {
    confetti({
      ...defaults,
      ...opts,
      particleCount: Math.floor(count * particleRatio),
    })
  }

  fire(0.25, {
    spread: 26,
    startVelocity: 55,
    colors: ['#8b5cf6', '#ec4899', '#10b981'],
  })
  fire(0.2, {
    spread: 60,
    colors: ['#f59e0b', '#eab308', '#22c55e'],
  })
  fire(0.35, {
    spread: 100,
    decay: 0.91,
    scalar: 0.8,
    colors: ['#8b5cf6', '#ec4899', '#06b6d4'],
  })
  fire(0.1, {
    spread: 120,
    startVelocity: 25,
    decay: 0.92,
    scalar: 1.2,
    colors: ['#ffffff', '#f9fafb'],
  })
  fire(0.1, {
    spread: 120,
    startVelocity: 45,
    colors: ['#10b981', '#f59e0b', '#eab308'],
  })
}

// Streak milestone celebration (more intense)
export function celebrateStreak(streakCount: number) {
  const duration = 3000
  const animationEnd = Date.now() + duration

  const colors = ['#ff6b35', '#f7931e', '#ffcc02'] // Fire colors

  function frame() {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors,
      zIndex: 9999,
    })
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors,
      zIndex: 9999,
    })

    if (Date.now() < animationEnd) {
      requestAnimationFrame(frame)
    }
  }

  frame()

  // Big burst in the middle
  setTimeout(() => {
    confetti({
      particleCount: streakCount * 10,
      spread: 100,
      origin: { y: 0.6 },
      colors: [...colors, '#8b5cf6', '#ec4899'],
      zIndex: 9999,
    })
  }, duration / 2)
}

// All sections complete celebration
export function celebrateAllComplete() {
  const end = Date.now() + 2000

  const colors = ['#10b981', '#f59e0b', '#eab308'] // Health, Happiness, Hela colors

  ;(function frame() {
    confetti({
      particleCount: 4,
      angle: 60,
      spread: 80,
      origin: { x: 0, y: 0.6 },
      colors,
      shapes: ['circle', 'square'],
      zIndex: 9999,
    })
    confetti({
      particleCount: 4,
      angle: 120,
      spread: 80,
      origin: { x: 1, y: 0.6 },
      colors,
      shapes: ['circle', 'square'],
      zIndex: 9999,
    })

    if (Date.now() < end) {
      requestAnimationFrame(frame)
    }
  })()
}

// Fireworks effect for major achievements
export function fireworks() {
  const duration = 5000
  const animationEnd = Date.now() + duration
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 }

  function randomInRange(min: number, max: number) {
    return Math.random() * (max - min) + min
  }

  const interval: ReturnType<typeof setInterval> = setInterval(function () {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      return clearInterval(interval)
    }

    const particleCount = 50 * (timeLeft / duration)

    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      colors: ['#8b5cf6', '#ec4899', '#10b981'],
    })
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      colors: ['#f59e0b', '#eab308', '#06b6d4'],
    })
  }, 250)
}

// Emoji rain (fun celebration)
export function emojiRain() {
  const scalar = 2
  const shapes = [
    confetti.shapeFromText({ text: '💪', scalar }),
    confetti.shapeFromText({ text: '😊', scalar }),
    confetti.shapeFromText({ text: '💰', scalar }),
    confetti.shapeFromText({ text: '🔥', scalar }),
    confetti.shapeFromText({ text: '⭐', scalar }),
  ]

  const defaults = {
    spread: 360,
    ticks: 100,
    gravity: 0.5,
    decay: 0.94,
    startVelocity: 20,
    shapes,
    scalar,
    zIndex: 9999,
  }

  confetti({
    ...defaults,
    particleCount: 30,
    origin: { x: 0.2, y: 0.3 },
  })
  confetti({
    ...defaults,
    particleCount: 30,
    origin: { x: 0.8, y: 0.3 },
  })
  confetti({
    ...defaults,
    particleCount: 30,
    origin: { x: 0.5, y: 0.2 },
  })
}

// School pride (side cannons)
export function sideCannons() {
  const end = Date.now() + 1500

  const colors = ['#8b5cf6', '#ec4899', '#10b981', '#f59e0b']

  ;(function frame() {
    confetti({
      particleCount: 2,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors,
      zIndex: 9999,
    })
    confetti({
      particleCount: 2,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors,
      zIndex: 9999,
    })

    if (Date.now() < end) {
      requestAnimationFrame(frame)
    }
  })()
}
