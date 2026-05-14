/* ================================================================
   XBert Site — Global JavaScript
   Mobile nav, scroll state, scroll reveal.
   ================================================================ */

if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
window.scrollTo(0, 0);

document.addEventListener('DOMContentLoaded', () => {

    /* Dynamic copyright year */
    const yearEl = document.querySelector('[data-year]');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    /* ------------------------------------------------
       Navbar Scroll State
       Adds .scrolled class when page is scrolled
       ------------------------------------------------ */
    const navbar = document.querySelector('.navbar');

    if (navbar) {
        const SCROLL_THRESHOLD = 40;

        const updateNavbar = () => {
            if (window.scrollY > SCROLL_THRESHOLD) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        };

        window.addEventListener('scroll', updateNavbar, { passive: true });
        updateNavbar();
    }


    /* ------------------------------------------------
       Mobile Nav Toggle
       Opens/closes mobile drawer + overlay
       ------------------------------------------------ */
    const navToggle = document.querySelector('.nav-toggle');
    const mobilePanel = document.querySelector('.mobile-nav-panel');
    const mobileOverlay = document.querySelector('.mobile-nav-overlay');

    if (navToggle && mobilePanel && mobileOverlay) {
        const toggleMobileNav = () => {
            const isOpen = mobilePanel.classList.contains('open');
            const shouldOpen = !isOpen;

            navToggle.classList.toggle('active', shouldOpen);
            navToggle.setAttribute('aria-expanded', String(shouldOpen));
            navbar && navbar.classList.toggle('mobile-open', shouldOpen);
            mobilePanel.classList.toggle('open', shouldOpen);
            mobileOverlay.classList.toggle('active', shouldOpen);
            document.body.style.overflow = isOpen ? '' : 'hidden';
        };

        navToggle.addEventListener('click', toggleMobileNav);
        mobileOverlay.addEventListener('click', toggleMobileNav);

        mobilePanel.querySelectorAll('a:not(.mobile-nav-dropdown > a)').forEach(link => {
            link.addEventListener('click', () => {
                if (mobilePanel.classList.contains('open')) {
                    toggleMobileNav();
                }
            });
        });
    }


    /* ------------------------------------------------
       Mobile Nav Accordion Dropdowns
       Toggles .open on mobile-nav-dropdown items
       ------------------------------------------------ */
    const mobileDropdowns = document.querySelectorAll('.mobile-nav-dropdown > a');

    mobileDropdowns.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const parent = trigger.parentElement;
            const wasOpen = parent.classList.contains('open');

            document.querySelectorAll('.mobile-nav-dropdown.open').forEach(dd => {
                dd.classList.remove('open');
            });

            if (!wasOpen) {
                parent.classList.add('open');
            }
        });
    });


    /* ------------------------------------------------
       Live Clock
       Updates any element with [data-live-clock="date|time"]
       to the user's current local date or time. Re-renders
       every minute so the time stays accurate without
       requiring a page refresh.
       ------------------------------------------------ */
    const clockEls = document.querySelectorAll('[data-live-clock]');

    if (clockEls.length > 0) {
        const dateFmt = new Intl.DateTimeFormat(undefined, {
            month: 'short',
            day: 'numeric'
        });
        const timeFmt = new Intl.DateTimeFormat(undefined, {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

        const updateClock = () => {
            const now = new Date();
            const date = dateFmt.format(now);
            const time = timeFmt.format(now);
            clockEls.forEach(el => {
                if (el.dataset.liveClock === 'date') el.textContent = date;
                else if (el.dataset.liveClock === 'time') el.textContent = time;
            });
        };

        updateClock();
        // Align next tick to the start of the next minute, then run every 60s.
        const msToNextMinute = (60 - new Date().getSeconds()) * 1000;
        setTimeout(() => {
            updateClock();
            setInterval(updateClock, 60 * 1000);
        }, msToNextMinute);
    }


    /* ------------------------------------------------
       Motion preference (shared by spinners + typewriter)
       ------------------------------------------------ */
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isMobileViewport = window.matchMedia('(max-width: 767px)').matches;


    /* ------------------------------------------------
       Visibility gate — pause JS-driven animations for
       sections that are off-screen. CSS animations are
       throttled by the browser natively; these helpers
       handle setInterval / async-loop work.
       ------------------------------------------------ */
    function observeVisibility(el, onEnter, onLeave, margin) {
        if (!('IntersectionObserver' in window)) { onEnter(); return; }
        new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) onEnter();
            else onLeave();
        }, { rootMargin: margin || '100px' }).observe(el);
    }

    const heroSection = document.querySelector('.section-hero');
    let heroVisible = true;
    let heroVisibleResolvers = [];

    if (heroSection) {
        observeVisibility(heroSection,
            () => {
                heroVisible = true;
                heroVisibleResolvers.forEach(r => r());
                heroVisibleResolvers = [];
            },
            () => { heroVisible = false; }
        );
    }

    function waitForHeroVisible() {
        if (heroVisible) return Promise.resolve();
        return new Promise(resolve => heroVisibleResolvers.push(resolve));
    }


    /* ------------------------------------------------
       Unicode Spinners
       CLI-style looping dot patterns for elements with
       [data-spinner]. Frame sets defined per pattern.
       ------------------------------------------------ */
    const SPINNER_FRAMES = {
        // Originals (used by hero eyebrow + kept for reference)
        braille:   ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'],
        dots:      ['⢀⠀','⡀⠀','⠄⠀','⠂⠀','⠁⠀','⠈⠀','⠐⠀','⠠⠀'],
        circle:    ['◐','◓','◑','◒'],
        line:      ['|','/','-','\\'],
        bouncing:  ['⠁','⠂','⠄','⡀','⠠','⠐','⠈'],
        sparkle:   ['⡏','⠟','⠻','⢹','⣸','⣴','⣦','⣇'],

        // Creative braille patterns -- single cell
        orbit:     ['⠁','⠈','⠐','⠠','⢀','⡀','⠄','⠂'],
        heartbeat: ['⠁','⠃','⡇','⣿','⡇','⠃','⠁','⠀','⠀'],
        pulseOut:  ['⠁','⠃','⠇','⡇','⡏','⡟','⡿','⣿','⠀'],
        rainfall:  ['⠉','⠒','⠤','⣀','⠀'],
        breathe:   ['⠀','⠂','⠆','⡆','⣶','⣷','⣿','⣷','⣶','⡆','⠆','⠂'],
        fillUp:    ['⠀','⣀','⣤','⣶','⣿'],
        drain:     ['⣿','⣶','⣤','⣀','⠀'],
        stack:     ['⠀','⡀','⡄','⡆','⡇','⣇','⣧','⣷','⣿'],
        glitch:    ['⡏','⠟','⢨','⣦','⠫','⡝','⢁','⣸','⠞','⣛'],

        // Creative braille patterns -- multi cell
        scanner:   ['⠁⠀⠀⠀','⠀⠁⠀⠀','⠀⠀⠁⠀','⠀⠀⠀⠁','⠀⠀⠁⠀','⠀⠁⠀⠀'],
        marquee:   ['⡀⠀⠀','⠀⡀⠀','⠀⠀⡀'],
        inbox:     ['⠁⠀','⠄⠀','⡀⠀','⠀⡀','⠀⠀'],
        flow:      ['⡀⠀⠀⠀','⠀⡀⠀⠀','⠀⠀⡀⠀','⠀⠀⠀⡀','⠀⠀⠀⠀'],

        // Non-braille explorations -- crosshair, compass, geometric morphs
        reticle:    ['⊕','⊗','⊛','✛','✜'],
        compass:    ['↑','↗','→','↘','↓','↙','←','↖'],
        plusX:      ['+','×','⊕','⊗','✛','✜'],
        dissolve:   ['█','▓','▒','░','▒','▓'],
        triSpin:    ['▲','▶','▼','◀'],
        chevrons:   ['►    ',' ►   ','  ►  ','   ► ','    ►'],
        bracketBar: ['[▱▱▱▱]','[▰▱▱▱]','[▰▰▱▱]','[▰▰▰▱]','[▰▰▰▰]','[▱▰▰▰]','[▱▱▰▰]','[▱▱▱▰]'],
        snake:      ['●●●○○','○●●●○','○○●●●','○○○●●','○○○○●','●○○○○','●●○○○'],

        // More explorations -- dice, asterisks, pendulum, media, log statuses
        dominoes:    ['⚀','⚁','⚂','⚃','⚄','⚅'],
        asterisks:   ['*','∗','✱','✲','✳','✴'],
        pendulum:    ['\\','|','/','|'],
        mediaCtrl:   ['▶','⏸','⏹','⏺'],
        rotate45:    ['□','◇','▢','◊'],
        battery:     ['[░░░░]','[▓░░░]','[▓▓░░]','[▓▓▓░]','[▓▓▓▓]'],
        matrix:      ['$#@!','%^&*','?+=-','/\\<>','01[]','{};:'],
        statusCycle: ['[OK ]','[...]','[ACK]','[RDY]'],

        // 20 more -- moons, signals, counters, clocks, terminal prompts
        moonPhase:   ['○','◐','●','◑'],
        wifi:        ['▁▁▁▁','▂▁▁▁','▂▃▁▁','▂▃▅▁','▂▃▅█','▂▃▅▁','▂▃▁▁','▂▁▁▁'],
        hexCount:    ['0x00','0x01','0x02','0x03','0x04','0x05','0x06','0x07','0x08','0x09','0x0A','0x0B','0x0C','0x0D','0x0E','0x0F'],
        binCount:    ['0000','0001','0010','0011','0100','0101','0110','0111'],
        clockTick:   ['◴','◷','◶','◵'],
        hexagonSpin: ['⬡','⬢','⬣','⬢'],
        greekLetter: ['Ω','π','λ','Σ','Δ','∇','Ψ','Φ'],
        sortBars:    ['▁▂▃▄▅','▅▁▂▃▄','▄▅▁▂▃','▃▄▅▁▂','▂▃▄▅▁'],
        hash:        ['#','▦','▧','▨','▩'],
        arrowStack:  ['→   ','→→  ','→→→ ','→→→→'],
        stairs:      ['▁    ','▁▔   ','▁▔▁  ','▁▔▁▔ ','▁▔▁▔▁'],
        tally:       ['|    ','||   ','|||  ','|||| ','|||||'],
        percentage:  ['  0%',' 25%',' 50%',' 75%','100%'],
        typingCursor:['_   ','x_  ','xy_ ','xyz_','xyz ','xy  ','x   ','    '],
        boxFlash:    ['■','□'],
        diamondPulse:['·','◇','◆','◇'],
        prompt:      ['$  ','$_ ','$ _'],
        arc:         ['(   ','((  ','((( ','(((('],
        pipeline:    ['─','│','┐','┌','└','┘','┤','├'],
        pixelGrid:   ['▦','▧','▨','▩'],

        // Waveforms -- each braille cell encodes 2 column heights (0-4 each),
        // so 6 cells = 12-sample waveform. Frames advance by shifting samples
        // left to give the appearance of the wave traveling through the cell.
        sineWave:   ['⣴⣿⣷⣄⠀⢀','⣿⣷⣄⠀⢀⣴','⣷⣄⠀⢀⣴⣿','⣄⠀⢀⣴⣿⣷','⠀⢀⣴⣿⣷⣄','⢀⣴⣿⣷⣄⠀'],
        squareWave: ['⣿⡇⠀⣿⡇⠀','⡇⠀⣿⡇⠀⣿','⠀⣿⡇⠀⣿⡇'],
        sawtooth:   ['⢀⣴⣷⣄⢀⣴','⣴⣷⣄⢀⣴⢀','⣷⣄⢀⣴⢀⣴','⣄⢀⣴⢀⣴⣷','⢀⣴⢀⣴⣷⣄','⣴⢀⣴⣷⣄⢀'],
        ecg:        ['⣀⣄⣸⢰⣀⣀','⣄⣸⢰⣀⣀⣀','⣸⢰⣀⣀⣀⣄','⢰⣀⣀⣀⣄⣸','⣀⣀⣀⣄⣸⢰','⣀⣀⣄⣸⢰⣀'],
        eq:         ['⣆⣧⣼⣰','⣼⣰⣧⣆','⣧⣆⣸⣴','⣰⣧⣆⣧'],
        fade:       ['⣷⣶⣶⣶','⣦⣤⣤⣄','⣤⣀⣀⣀','⣀⠀⠀⠀','⠀⠀⠀⣀','⣀⣀⣀⣀','⣄⣤⣤⣦','⣶⣶⣶⣷'],
        stadium:    ['⣿⣤⣀⠀','⣤⣿⣤⣀','⣀⣤⣿⣤','⠀⣀⣤⣿','⣀⠀⣀⣤','⣤⣀⠀⣀'],
        noise:      ['⣀⠀⡀⢀','⠀⣀⢀⡀','⡀⢀⠀⣀','⢀⡀⣀⠀']
    };
    const SPINNER_INTERVAL_MS = 120;

    const spinners = document.querySelectorAll('[data-spinner]');

    if (spinners.length > 0 && !prefersReducedMotion) {
        const sectionSpinners = new Map();
        spinners.forEach(el => {
            const set = SPINNER_FRAMES[el.dataset.spinner];
            if (!set) return;
            const section = el.closest('section') || document.body;
            if (!sectionSpinners.has(section)) sectionSpinners.set(section, []);
            sectionSpinners.get(section).push({ el, set, idx: 0 });
        });

        sectionSpinners.forEach((group, section) => {
            let ids = [];

            const start = () => {
                if (ids.length) return;
                ids = group.map(s => setInterval(() => {
                    s.idx = (s.idx + 1) % s.set.length;
                    s.el.textContent = s.set[s.idx];
                }, SPINNER_INTERVAL_MS));
            };

            const stop = () => {
                ids.forEach(id => clearInterval(id));
                ids = [];
            };

            observeVisibility(section, start, stop);
        });
    }


    /* ------------------------------------------------
       Typewriter
       Cycles the textContent of any [data-typewriter]
       element through a list of words, backspacing the
       current word and typing the next one. Timing is
       randomized per character so it reads like real
       terminal input rather than a robotic loop.

       Markup contract:
         <span data-typewriter='["word one","word two"]'>word one</span>
         <span class="hero-title-cursor"></span>   ← optional sibling

       The sibling cursor (if present) gets `.is-typing`
       added during keystroke phases so its blink pauses.
       ------------------------------------------------ */
    const TYPER_TYPE_MIN_MS       = 35;
    const TYPER_TYPE_MAX_MS       = 70;
    const TYPER_BACKSPACE_MIN_MS  = 32;
    const TYPER_BACKSPACE_MAX_MS  = 42;
    const TYPER_HOLD_FULL_MS      = 2500;
    const TYPER_HOLD_EMPTY_MIN_MS = 200;
    const TYPER_HOLD_EMPTY_MAX_MS = 400;
    const TYPER_HESITATION_MIN_MS = 120;
    const TYPER_HESITATION_MAX_MS = 280;
    const TYPER_HESITATION_EVERY_MIN = 4;
    const TYPER_HESITATION_EVERY_MAX = 8;

    const rand = (min, max) => min + Math.random() * (max - min);
    const randInt = (min, max) => Math.floor(rand(min, max + 1));
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    const typewriters = document.querySelectorAll('[data-typewriter]');

    if (typewriters.length > 0 && !prefersReducedMotion) {
        typewriters.forEach(el => {
            let words;
            try {
                words = JSON.parse(el.dataset.typewriter);
            } catch (e) {
                return;
            }
            if (!Array.isArray(words) || words.length === 0) return;

            const sibling = el.nextElementSibling;
            const cursor = sibling && sibling.classList.contains('hero-title-cursor')
                ? sibling
                : null;

            // Optional companion: a [data-toast-stack] element containing one
            // .hero-toast child per word, each tagged with data-toast-key
            // matching one of the words. The stack physically rotates so the
            // toast whose key matches the current H1 word is at the front.
            const stackEl = document.querySelector('[data-toast-stack]');
            const STACK_LEAVE_MS = 350;
            let stackOrder = null;

            if (stackEl) {
                // Build the stack array in word-cycle order. Any cards that
                // don't have a matching key in `words` are dropped so we
                // don't paint an orphan card behind the deck.
                stackOrder = words
                    .map(w => stackEl.querySelector(`[data-toast-key="${w}"]`))
                    .filter(Boolean);
            }

            const applyFeedPositions = () => {
                if (!stackOrder) return;
                stackOrder.forEach((card, i) => {
                    for (let j = 0; j < stackOrder.length; j++) {
                        card.classList.remove(`feed-pos-${j}`);
                    }
                    card.classList.add(`feed-pos-${i}`);
                });
            };

            const rotateStack = async () => {
                if (!stackOrder || stackOrder.length < 2) return;
                const leaving = stackOrder[0];

                // Phase 1: active card lifts up and off the top of the feed.
                leaving.classList.add('is-leaving');
                await sleep(STACK_LEAVE_MS);

                // Phase 2: rotate the order (active goes to the back of the
                // queue), then reapply slot classes. The leaving card snaps
                // invisibly into feed-pos-4 (bottom of the feed) where it
                // sits ready to ride back up the conveyor over the next
                // cycles.
                stackOrder.push(stackOrder.shift());
                leaving.classList.remove('is-leaving');
                applyFeedPositions();
            };

            // Find the starting index in `words` based on current textContent so
            // the loop picks up from whatever word is rendered server-side.
            const initial = el.textContent;
            let idx = words.indexOf(initial);
            if (idx === -1) idx = 0;

            const runLoop = async () => {
                while (true) {
                    await waitForHeroVisible();
                    await sleep(TYPER_HOLD_FULL_MS);

                    if (cursor) cursor.classList.add('is-typing');
                    // Kick off the stack rotation alongside the H1 backspace.
                    // Don't await it — it runs in parallel with the keystrokes.
                    rotateStack();

                    // Backspace current word in one continuous sweep — no hesitations.
                    while (el.textContent.length > 0) {
                        el.textContent = el.textContent.slice(0, -1);
                        await sleep(rand(TYPER_BACKSPACE_MIN_MS, TYPER_BACKSPACE_MAX_MS));
                    }

                    // Brief "ok, what next" beat before typing the next word.
                    await sleep(rand(TYPER_HOLD_EMPTY_MIN_MS, TYPER_HOLD_EMPTY_MAX_MS));

                    // Advance to the next word and type it out alongside the
                    // toast settling into its new front position.
                    idx = (idx + 1) % words.length;
                    const next = words[idx];

                    let untilHesitation = randInt(TYPER_HESITATION_EVERY_MIN, TYPER_HESITATION_EVERY_MAX);
                    for (let i = 0; i < next.length; i++) {
                        el.textContent = next.slice(0, i + 1);
                        await sleep(rand(TYPER_TYPE_MIN_MS, TYPER_TYPE_MAX_MS));
                        if (--untilHesitation <= 0) {
                            await sleep(rand(TYPER_HESITATION_MIN_MS, TYPER_HESITATION_MAX_MS));
                            untilHesitation = randInt(TYPER_HESITATION_EVERY_MIN, TYPER_HESITATION_EVERY_MAX);
                        }
                    }

                    if (cursor) cursor.classList.remove('is-typing');
                }
            };

            // Initial paint: assign every card its starting feed position so
            // the conveyor is visible immediately on page load.
            applyFeedPositions();
            runLoop();
        });
    }


    /* ------------------------------------------------
       Background Code Snippets
       Cycles a single [data-bg-snippet] element through
       a pool of small code fragments. Each snippet is
       placed at one of several "safe" hero positions,
       cascade-streams its lines in, holds for ~2s, then
       fades out and reappears elsewhere with new content.
       Reads as ambient code activity around the headline.
       ------------------------------------------------ */
    const SNIPPET_HOLD_MS         = 2200;
    const SNIPPET_FADE_MS         = 500;
    const SNIPPET_PAUSE_MS        = 400;
    const SNIPPET_TYPE_MIN_MS     = 18;
    const SNIPPET_TYPE_MAX_MS     = 38;
    const SNIPPET_LINE_BREAK_MS   = 90;

    const BG_SNIPPETS = [
        [
            '// inbound webhook',
            "router.post('/webhook', async (req) => {",
            '  const event = parse(req.body)',
            '  await agent.process(event)',
            '})',
        ],
        [
            '// rate limiter',
            "limiter.check({ key: 'agent.respond' })",
            'limiter.consume(1)',
        ],
        [
            '// memory shape',
            'type Memory = {',
            '  history: Event[]',
            '  context: Map<string, any>',
            '  embeddings: Vector[]',
            '}',
        ],
        [
            '// agent spawn',
            'const agent = new Agent({',
            "  voice: 'natural',",
            '  intents: routes,',
            '})',
        ],
        [
            '// follow-up scheduler',
            "scheduler.queue('followup', {",
            "  trigger: '24h',",
            "  template: 'recap',",
            '})',
        ],
        [
            '// embedding sync',
            "await embeddings.sync({ sources: 'all' })",
            'index.rebuild()',
        ],
        [
            '// transcript parser',
            'function extract(transcript) {',
            '  return tokenize(transcript)',
            '    .filter(intent.relevant)',
            '    .map(normalize)',
            '}',
        ],
        [
            '// session lifecycle',
            "session.on('start', initContext)",
            "session.on('end', archive)",
            "session.on('idle', recycle)",
        ],
        [
            '// handoff payload',
            'const payload = {',
            '  transcript,',
            '  summary,',
            '  next_action,',
            '}',
        ],
        [
            '// intent router',
            'switch (intent.type) {',
            "  case 'booking': return book(ctx)",
            "  case 'billing': return route('human')",
            '}',
        ],
    ];

    const isCommentLine = (text) => /^\s*\/\//.test(text);

    function createSnippetStage(stage, waitFn, opts) {
        const cfg = {
            streamCount: 3,
            staggerMs: 900,
            topMinPct: 4,
            topMaxPct: 80,
            leftMinPct: 2,
            leftMaxPct: 78,
            snippetWPx: 280,
            snippetHPx: 110,
            placementTries: 12,
            ...opts,
        };

        let sharedSnippetIdx = 0;
        const activeRects = new Map();

        const sw = () => stage.clientWidth  || window.innerWidth;
        const sh = () => stage.clientHeight || window.innerHeight;

        const rectsOverlap = (a, b) => !(
            a.x + a.w < b.x || b.x + b.w < a.x ||
            a.y + a.h < b.y || b.y + b.h < a.y
        );

        const pickRandomPosition = (selfEl) => {
            const stageW = sw(), stageH = sh();
            const minLeft = (cfg.leftMinPct / 100) * stageW;
            const maxLeft = (cfg.leftMaxPct / 100) * stageW;
            const minTop  = (cfg.topMinPct  / 100) * stageH;
            const maxTop  = (cfg.topMaxPct  / 100) * stageH;

            for (let attempt = 0; attempt < cfg.placementTries; attempt++) {
                const x = rand(minLeft, maxLeft);
                const y = rand(minTop,  maxTop);
                const candidate = { x, y, w: cfg.snippetWPx, h: cfg.snippetHPx };

                let collides = false;
                for (const [otherEl, otherRect] of activeRects) {
                    if (otherEl === selfEl) continue;
                    if (rectsOverlap(candidate, otherRect)) { collides = true; break; }
                }
                if (!collides) return candidate;
            }

            return {
                x: rand(minLeft, maxLeft),
                y: rand(minTop,  maxTop),
                w: cfg.snippetWPx,
                h: cfg.snippetHPx,
            };
        };

        const applyPosition = (el, rect) => {
            el.style.top    = `${rect.y}px`;
            el.style.left   = `${rect.x}px`;
            el.style.right  = 'auto';
            el.style.bottom = 'auto';
        };

        const setupSnippetDOM = (el, lines) => {
            el.replaceChildren(
                ...lines.map(line => {
                    const div = document.createElement('div');
                    div.className = 'bg-snippet-line' + (isCommentLine(line) ? ' is-comment' : '');
                    div.innerHTML = '&nbsp;';
                    return div;
                })
            );
        };

        const typeSnippet = async (el, lines) => {
            const lineEls = el.querySelectorAll('.bg-snippet-line');

            for (let li = 0; li < lines.length; li++) {
                const text = lines[li];
                const lineEl = lineEls[li];
                if (!lineEl) break;

                lineEl.textContent = '';

                const cursor = document.createElement('span');
                cursor.className = 'bg-snippet-cursor is-typing';
                lineEl.appendChild(cursor);

                if (text.length === 0) {
                    cursor.classList.remove('is-typing');
                    await sleep(SNIPPET_LINE_BREAK_MS * 2);
                    cursor.remove();
                    lineEl.innerHTML = '&nbsp;';
                    continue;
                }

                for (let i = 0; i < text.length; i++) {
                    cursor.before(document.createTextNode(text[i]));
                    await sleep(rand(SNIPPET_TYPE_MIN_MS, SNIPPET_TYPE_MAX_MS));
                }

                cursor.classList.remove('is-typing');
                await sleep(SNIPPET_LINE_BREAK_MS);
                cursor.remove();
            }

            for (let i = lineEls.length - 1; i >= 0; i--) {
                const node = lineEls[i];
                if (node && node.textContent && node.textContent !== '\u00a0') {
                    const finalCursor = document.createElement('span');
                    finalCursor.className = 'bg-snippet-cursor';
                    node.appendChild(finalCursor);
                    break;
                }
            }
        };

        const runStream = async (el) => {
            while (true) {
                await waitFn();
                const pool = cfg.snippets || BG_SNIPPETS;
                const snippet = pool[sharedSnippetIdx % pool.length];
                sharedSnippetIdx++;

                const rect = pickRandomPosition(el);
                activeRects.set(el, rect);

                applyPosition(el, rect);
                el.classList.remove('is-leaving');
                setupSnippetDOM(el, snippet);

                await typeSnippet(el, snippet);
                await sleep(SNIPPET_HOLD_MS);

                el.classList.add('is-leaving');
                await sleep(SNIPPET_FADE_MS + SNIPPET_PAUSE_MS);

                activeRects.delete(el);
            }
        };

        for (let i = 0; i < cfg.streamCount; i++) {
            const el = document.createElement('div');
            el.className = 'bg-snippet';
            stage.appendChild(el);
            setTimeout(() => runStream(el), i * cfg.staggerMs);
        }
    }

    const bgStage = document.querySelector('[data-bg-snippet-stage]');
    if (bgStage && !prefersReducedMotion && !isMobileViewport) {
        createSnippetStage(bgStage, waitForHeroVisible);
    }

    const teamBgStage = document.querySelector('[data-bg-snippet-stage-team]');
    const teamSection = document.querySelector('.section-ai-team');
    if (teamBgStage && teamSection && !prefersReducedMotion) {
        let teamVisible = false;
        let teamResolvers = [];

        observeVisibility(teamSection,
            () => { teamVisible = true; teamResolvers.forEach(r => r()); teamResolvers = []; },
            () => { teamVisible = false; },
            '200px'
        );

        function waitForTeamVisible() {
            if (teamVisible) return Promise.resolve();
            return new Promise(resolve => teamResolvers.push(resolve));
        }

        createSnippetStage(teamBgStage, waitForTeamVisible, {
            streamCount: 3,
            staggerMs: 1200,
        });
    }

    /* ------------------------------------------------
       Proof Card -- right-to-left typed code stream
       Flows down the right edge of the image card.
       Characters type out from right to left.
       ------------------------------------------------ */
    const proofCodeStage = document.querySelector('[data-proof-snippet-stage]');
    const proofSection = document.querySelector('.section-proof');
    if (proofCodeStage && proofSection && !prefersReducedMotion && !isMobileViewport) {
        let proofVisible = false;
        let proofResolvers = [];

        observeVisibility(proofSection,
            () => { proofVisible = true; proofResolvers.forEach(r => r()); proofResolvers = []; },
            () => { proofVisible = false; },
            '200px'
        );

        function waitForProofVisible() {
            if (proofVisible) return Promise.resolve();
            return new Promise(resolve => proofResolvers.push(resolve));
        }

        const PROOF_LINES = [
            '// loading customer journal',
            'customer.lookup(id=2941)',
            'interactions: 49 logged',
            'lifetime_value: $14,200',
            'sentiment_trend: positive',
            'last_contact: 2 days ago',
            '',
            '// reasoning over business policy',
            'policy.match("refund-eligibility")',
            'source: refund-policy v3.2',
            'conditions: amount < $500',
            'purchase_date: within 30d window',
            'decision: eligible per section 4.1',
            '',
            '// guardrail enforcement',
            'guardrail.check(scope="response")',
            'hipaa: enforced',
            'pii_fields: [REDACTED]',
            'legal_advice: blocked',
            'claim requires citation: true',
            'linked: policy-ref-4182',
            'status: safe to surface',
            '',
            '// threading conversation context',
            'history.load(customer=2941)',
            'prior_topic: billing inquiry',
            'resolution: credited $42.00',
            'applying context to live session',
            'tone: match prior preference',
            '',
            '// knowledge fabric query',
            'fabric.search("cancellation window")',
            'source: employee_handbook.pdf',
            'effective: 2024-01-15',
            'result: within 30-day grace',
            'confidence: 99.7%',
            'citation attached to response',
            '',
            '// churn risk scoring',
            'churn.evaluate(account=2941)',
            'engagement: declining 14d',
            'nps_last: 6',
            'open_tickets: 2 unresolved',
            'risk_score: 0.78 (high)',
            'alert: dispatched to account_mgr',
            '',
            '// nextiq domain filter',
            'nextiq.flow(model="gpt-4o")',
            'filter: domain_specific',
            'training: 17yr comms dataset',
            'business_context: injected',
            'response_quality: above baseline',
        ];

        const PROOF_TYPE_MIN = 12;
        const PROOF_TYPE_MAX = 28;
        const PROOF_LINE_PAUSE = 120;
        const MAX_VISIBLE_LINES = 22;

        const runProofStream = async () => {
            let lineIdx = 0;
            while (true) {
                await waitForProofVisible();

                const text = PROOF_LINES[lineIdx % PROOF_LINES.length];
                lineIdx++;

                const lineEl = document.createElement('div');
                lineEl.className = 'proof-code-line';
                proofCodeStage.appendChild(lineEl);

                const cursor = document.createElement('span');
                cursor.className = 'proof-code-cursor is-typing';
                lineEl.appendChild(cursor);

                for (let i = 0; i < text.length; i++) {
                    cursor.before(document.createTextNode(text[i]));
                    await sleep(rand(PROOF_TYPE_MIN, PROOF_TYPE_MAX));
                }

                cursor.classList.remove('is-typing');
                await sleep(PROOF_LINE_PAUSE);
                cursor.remove();

                const lines = proofCodeStage.querySelectorAll('.proof-code-line');
                if (lines.length > MAX_VISIBLE_LINES) {
                    const old = lines[0];
                    old.style.opacity = '0';
                    old.style.transition = 'opacity 0.4s';
                    setTimeout(() => old.remove(), 400);
                }
            }
        };
        runProofStream();
    }


    /* ------------------------------------------------
       Knowledge Fabric — Halftone Dot Layers
       Procedurally fills each [data-fabric-layer] SVG with
       a grid of circles whose opacity (and radius) follow a
       sine wave across the X axis with a vertical falloff
       toward the center row. The result is a soft halftone
       cloud that brightens in the middle and fades at the
       edges — the same look as the reference poster.

       Each layer's wave gets a phase offset based on its
       data-fabric-layer index so the three planes feel like
       the same wave caught at different moments instead of
       three identical clouds stacked on top of one another.

       Static visual content only — the floating animation
       is handled in CSS and respects prefers-reduced-motion
       on its own, so we always render the dots.
       ------------------------------------------------ */
    const fabricSection = document.querySelector('.section-fabric');
    const fabricLayers  = document.querySelectorAll('[data-fabric-layer]');

    if (fabricSection && fabricLayers.length > 0 && 'IntersectionObserver' in window) {
        let fabricReady = false;
        let pulseId = null;
        let statusId = null;
        let pulseIdx = 2;

        const fabricStatus = document.querySelector('[data-fabric-status]');
        const STATUS_PHRASES = [
            'LYR.STACK // RESOLVING',
            'SRC.TRACE // VERIFIED',
            'JOURNAL // 49 OF 49',
            'RBAC // ENFORCED',
            'CITATION // LINKED',
            'NEXT.IQ // ACTIVE',
            'KNOWLEDGE // SYNCED',
            'GOVERNED // SAFE',
        ];
        let statusIdx = 0;

        const startTimers = () => {
            if (!fabricReady) return;

            const svgs = document.querySelectorAll('.fabric-layer-svg');
            if (svgs.length === 3 && !prefersReducedMotion && !pulseId) {
                const pulseOnce = () => {
                    svgs.forEach(s => s.classList.remove('is-blue'));
                    svgs.forEach(s => s.parentElement.classList.remove('is-blue'));

                    const wrapper = svgs[pulseIdx].parentElement;
                    svgs[pulseIdx].classList.add('is-blue');
                    wrapper.classList.add('is-blue');
                    setTimeout(() => wrapper.classList.add('is-pulsing'), 250);
                    pulseIdx--;
                    if (pulseIdx < 0) pulseIdx = 2;
                };
                pulseOnce();
                pulseId = setInterval(pulseOnce, 1500);
            }

            if (fabricStatus && !prefersReducedMotion && !statusId) {
                statusId = setInterval(() => {
                    statusIdx = (statusIdx + 1) % STATUS_PHRASES.length;
                    fabricStatus.textContent = STATUS_PHRASES[statusIdx];
                }, 2800);
            }
        };

        const stopTimers = () => {
            if (pulseId) { clearInterval(pulseId); pulseId = null; }
            if (statusId) { clearInterval(statusId); statusId = null; }
        };

        observeVisibility(fabricSection, () => {
            if (!fabricReady) {
                initFabricDiagram(() => {
                    fabricReady = true;
                    startTimers();
                });
            } else {
                startTimers();
            }
        }, stopTimers, '200px');
    }

    // Streaming code snippets behind the diamond layers — same treatment as
    // the hero background, gated to fabric section visibility.
    const fabricBgStage = document.querySelector('[data-fabric-snippet-stage]');
    if (fabricBgStage && fabricSection && !prefersReducedMotion && !isMobileViewport) {
        let fabricSnippetVisible = false;
        let fabricSnippetResolvers = [];

        observeVisibility(fabricSection,
            () => {
                fabricSnippetVisible = true;
                fabricSnippetResolvers.forEach(r => r());
                fabricSnippetResolvers = [];
            },
            () => { fabricSnippetVisible = false; },
            '200px'
        );

        function waitForFabricVisible() {
            if (fabricSnippetVisible) return Promise.resolve();
            return new Promise(resolve => fabricSnippetResolvers.push(resolve));
        }

        const FABRIC_SNIPPETS = [
            // Knowledge Layer -- AI reasoning over policy
            [
                '// scanning policy database',
                'found: refund-policy v3.2',
                'conditions: amount < $500',
                'action: approve per section 4.1',
            ],
            [
                '// querying knowledge base',
                'source: employee_handbook.pdf',
                'matching query to procedures...',
                'confidence: 99.7%',
            ],
            [
                '// retrieving citations',
                'policy: cancellation-window',
                'effective: 2024-01-15',
                'result: within 30-day grace',
            ],
            [
                '// knowledge sync complete',
                'indexed: 2,847 documents',
                'embeddings: refreshed',
                'ready for inference',
            ],
            // Customer Journal Layer -- threading history
            [
                '// loading customer history',
                'interactions: 49 logged',
                'last contact: 2 days ago',
                'sentiment: positive',
            ],
            [
                '// threading conversation #50',
                'prior topic: billing inquiry',
                'resolution: credited $42.00',
                'applying context to live call',
            ],
            [
                '// journal entry written',
                'caller recognized: returning',
                'lifetime value: high',
                'preferred channel: phone',
            ],
            [
                '// stitching timeline',
                'first contact: 14 months ago',
                'resolution rate: 100%',
                'notes: prefers concise answers',
            ],
            // Guardian Layer -- access + compliance
            [
                '// checking access scope',
                'HIPAA: enforced',
                'PII fields: [REDACTED]',
                'audit log: entry written',
            ],
            [
                '// validating permissions',
                'role: support-tier-2',
                'data access: restricted',
                'compliance: verified',
            ],
            [
                '// guardrail check',
                'response contains no PII',
                'citation sources: governed',
                'safe to surface',
            ],
            [
                '// evidence gate',
                'claim: "refund eligible"',
                'source required: true',
                'linked: policy-ref-4182',
            ],
        ];

        const el = document.createElement('div');
        el.className = 'bg-snippet fabric-snippet-fixed';
        fabricBgStage.appendChild(el);

        let idx = 0;
        const runFabricLoop = async () => {
            while (true) {
                await waitForFabricVisible();
                const snippet = FABRIC_SNIPPETS[idx % FABRIC_SNIPPETS.length];
                idx++;

                el.classList.remove('is-leaving');
                el.replaceChildren(
                    ...snippet.map(line => {
                        const div = document.createElement('div');
                        div.className = 'bg-snippet-line' + (isCommentLine(line) ? ' is-comment' : '');
                        div.innerHTML = '&nbsp;';
                        return div;
                    })
                );

                const lineEls = el.querySelectorAll('.bg-snippet-line');
                for (let li = 0; li < snippet.length; li++) {
                    const text = snippet[li];
                    const lineEl = lineEls[li];
                    if (!lineEl) break;
                    lineEl.textContent = '';
                    const cursor = document.createElement('span');
                    cursor.className = 'bg-snippet-cursor is-typing';
                    lineEl.appendChild(cursor);
                    for (let ci = 0; ci < text.length; ci++) {
                        cursor.before(document.createTextNode(text[ci]));
                        await sleep(rand(SNIPPET_TYPE_MIN_MS, SNIPPET_TYPE_MAX_MS));
                    }
                    cursor.classList.remove('is-typing');
                    await sleep(SNIPPET_LINE_BREAK_MS);
                    cursor.remove();
                }

                const lastLine = lineEls[lineEls.length - 1];
                if (lastLine) {
                    const finalCursor = document.createElement('span');
                    finalCursor.className = 'bg-snippet-cursor';
                    lastLine.appendChild(finalCursor);
                }

                await sleep(SNIPPET_HOLD_MS);
                el.classList.add('is-leaving');
                await sleep(SNIPPET_FADE_MS + SNIPPET_PAUSE_MS);
            }
        };
        runFabricLoop();
    }

    /* ------------------------------------------------
       Journal Tooltip Cycle
       Sequentially reveals the micro-node tooltips when
       the customer journal enters view. Manual hover pauses
       the cycle so the user's target gets priority.
       ------------------------------------------------ */
    const journalThread = document.querySelector('.fabric-journal-thread');
    const journalTooltips = journalThread
        ? Array.from(journalThread.querySelectorAll('.journal-micro-pill[data-tooltip]'))
        : [];

    if (journalThread && journalTooltips.length > 0 && !prefersReducedMotion && !isMobileViewport) {
        const TOOLTIP_CYCLE_MS = 3200;
        let tooltipCycleId = null;
        let activeTooltipIdx = -1;
        let journalInView = false;
        let isUserHoveringTooltip = false;

        const clearActiveTooltip = () => {
            journalTooltips.forEach(pill => pill.classList.remove('is-active'));
        };

        const showNextTooltip = () => {
            clearActiveTooltip();
            activeTooltipIdx = (activeTooltipIdx + 1) % journalTooltips.length;
            journalTooltips[activeTooltipIdx].classList.add('is-active');
        };

        const stopTooltipCycle = () => {
            if (tooltipCycleId) {
                clearInterval(tooltipCycleId);
                tooltipCycleId = null;
            }
        };

        const startTooltipCycle = (showImmediately = false) => {
            if (tooltipCycleId || isUserHoveringTooltip) return;
            if (showImmediately) showNextTooltip();
            tooltipCycleId = setInterval(showNextTooltip, TOOLTIP_CYCLE_MS);
        };

        journalTooltips.forEach((pill, index) => {
            pill.addEventListener('mouseenter', () => {
                isUserHoveringTooltip = true;
                stopTooltipCycle();
                clearActiveTooltip();
                activeTooltipIdx = index;
                pill.classList.add('is-active');
            });

            pill.addEventListener('mouseleave', () => {
                isUserHoveringTooltip = false;
                if (journalInView) startTooltipCycle();
            });
        });

        observeVisibility(journalThread,
            () => {
                journalInView = true;
                startTooltipCycle(activeTooltipIdx === -1);
            },
            () => {
                journalInView = false;
                stopTooltipCycle();
                clearActiveTooltip();
            },
            '0px 0px -120px 0px'
        );
    }

    function initFabricDiagram(onReady) {
        const GRID      = 44;
        const ISO_X     = 18;
        const ISO_Y     = 10;
        const DOT_R_MIN = 1.4;
        const DOT_R_MAX = 5.6;
        const OPACITY_MIN = 0.15;
        const OPACITY_MAX = 1.0;
        const WAVE_AMP  = 28;
        const WAVE_FREQ = 1.6;
        const TWINKLE_PROB     = 0.16;
        const TWINKLE_POP_PROB = 0.015;
        const TWINKLE_DURATION = 5.5;

        const project = (col, row) => {
            const px = (col - row) * ISO_X;
            const py = (col + row) * ISO_Y;
            return [px, py];
        };
        const corners = [[0,0],[GRID-1,0],[0,GRID-1],[GRID-1,GRID-1]];
        let minPx = Infinity, maxPx = -Infinity, minPy = Infinity, maxPy = -Infinity;
        corners.forEach(([c,r]) => {
            const [px,py] = project(c,r);
            if (px < minPx) minPx = px;
            if (px > maxPx) maxPx = px;
            if (py < minPy) minPy = py;
            if (py > maxPy) maxPy = py;
        });
        const PAD = WAVE_AMP + DOT_R_MAX + 4;
        const vbW = (maxPx - minPx) + PAD * 2;
        const vbH = (maxPy - minPy) + PAD * 2 + WAVE_AMP;
        const offX = -minPx + PAD;
        const offY = -minPy + PAD;

        const twinklerRects = [];

        fabricLayers.forEach(svg => {
            const layerIdx = parseInt(svg.dataset.fabricLayer, 10) || 0;
            const phase = layerIdx * (Math.PI * 2 / 3);

            svg.setAttribute('viewBox', `0 0 ${vbW.toFixed(1)} ${vbH.toFixed(1)}`);
            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
            svg.setAttribute('shape-rendering', 'crispEdges');

            const twinkleDelays = [];
            let markup = '';
            for (let r = 0; r < GRID; r++) {
                for (let c = 0; c < GRID; c++) {
                    const [px, py] = project(c, r);
                    const normDepth = (c + r) / ((GRID - 1) * 2);
                    const depthScale = 0.2 + 0.8 * normDepth;
                    const normC = (c / (GRID - 1)) * 2 - 1;
                    const normR = (r / (GRID - 1)) * 2 - 1;
                    const dist  = Math.max(Math.abs(normC), Math.abs(normR));
                    const edgeFalloff = 1 - Math.pow(dist, 1.5);
                    const intensity = depthScale * (0.3 + 0.7 * edgeFalloff);
                    const waveY = Math.sin(normC * Math.PI * WAVE_FREQ + phase)
                                  * WAVE_AMP * intensity;

                    const cx = offX + px;
                    const cy = offY + py + waveY;
                    const radius  = DOT_R_MIN + intensity * (DOT_R_MAX - DOT_R_MIN);
                    const opacity = OPACITY_MIN + intensity * (OPACITY_MAX - OPACITY_MIN);

                    const roll = Math.random();
                    const canTwinkle = intensity > 0.3 && !prefersReducedMotion;
                    const isPop     = canTwinkle && roll < TWINKLE_POP_PROB;
                    const isTwinkle = !isPop && canTwinkle && roll < TWINKLE_PROB;

                    if (isPop || isTwinkle) {
                        twinkleDelays.push({
                            delay: (Math.random() * TWINKLE_DURATION).toFixed(2),
                            pop: isPop,
                        });
                    }

                    const twinkleAttr = isPop ? ' data-twinkle="pop"'
                                       : isTwinkle ? ' data-twinkle="1"'
                                       : '';
                    const side = radius * 2;
                    const rx = cx - radius;
                    const ry = cy - radius;
                    markup += `<rect x="${rx.toFixed(2)}" y="${ry.toFixed(2)}" width="${side.toFixed(2)}" height="${side.toFixed(2)}" fill="currentColor" opacity="${opacity.toFixed(3)}" class="fabric-dot"${twinkleAttr}/>`;
                }
            }
            svg.innerHTML = markup;
            twinklerRects.push({ svg, delays: twinkleDelays });
        });

        const fabricSvgs = document.querySelectorAll('.fabric-layer-svg');
        fabricSvgs.forEach(svg => {
            svg.parentElement.addEventListener('animationend', (e) => {
                if (e.pseudoElement === '::after') {
                    e.currentTarget.classList.remove('is-pulsing');
                }
            });
        });

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                twinklerRects.forEach(({ svg, delays }) => {
                    let i = 0;
                    svg.querySelectorAll('[data-twinkle]').forEach(rect => {
                        const info = delays[i++];
                        rect.classList.add(info.pop ? 'fabric-dot--twinkle-pop' : 'fabric-dot--twinkle');
                        rect.style.animationDelay = info.delay + 's';
                    });
                });

                if (onReady) onReady();
            });
        });
    }


    /* ------------------------------------------------
       Founder Video — Viewport Autoplay
       Wistia Aurora player only starts playing when the
       video scrolls into view, and pauses when it leaves.
       Mirrors the silent-autoplay UX (muted on first play,
       "Click For Sound" overlay handles unmute) so the
       feel of the original autoplay is preserved -- it
       just doesn't fire until the user actually sees it.
       Reduced-motion users get no auto-trigger at all.
       ------------------------------------------------ */
    const founderPlayer = document.querySelector('.founder-video-frame wistia-player');

    if (founderPlayer && 'IntersectionObserver' in window && !prefersReducedMotion) {
        let isInView = false;
        let hasMutedOnce = false;

        const tryPlay = () => {
            // Mute on first play so the browser doesn't block autoplay; after
            // that we leave audio state alone so the user's "Click For Sound"
            // choice persists across scroll-out/scroll-back cycles.
            if (!hasMutedOnce && typeof founderPlayer.mute === 'function') {
                founderPlayer.mute();
                hasMutedOnce = true;
            }
            founderPlayer.play?.();
        };

        const tryPause = () => {
            founderPlayer.pause?.();
        };

        const videoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                isInView = entry.isIntersecting;
                if (isInView) {
                    tryPlay();
                } else {
                    tryPause();
                }
            });
        }, { threshold: 0.5 });

        videoObserver.observe(founderPlayer);

        // If the player API isn't loaded yet when the user has already scrolled
        // the video into view, retry once Aurora fires its ready event so the
        // first play() actually lands instead of silently no-op'ing.
        founderPlayer.addEventListener('ready', () => {
            if (isInView) tryPlay();
        }, { once: true });
    }


    /* ------------------------------------------------
       Setup Interview Chat Animation
       Triggers staggered message appearance when the
       setup section scrolls into view.
       ------------------------------------------------ */
    /* Draw the dotted connector line between interview and rules panels */
    const connectorSvg = document.querySelector('.setup-connector');
    const connectorPath = document.querySelector('.setup-connector-path');
    const interviewPanel = document.querySelector('.setup-mockup--interview');
    const rulesPanel = document.querySelector('.setup-mockup--rules');

    function drawConnector() {
        if (!connectorSvg || !connectorPath || !interviewPanel || !rulesPanel) return;
        const container = connectorSvg.parentElement;
        const cRect = container.getBoundingClientRect();
        const iRect = interviewPanel.getBoundingClientRect();
        const rRect = rulesPanel.getBoundingClientRect();

        const x1 = iRect.right - cRect.left;
        const y1 = iRect.top - cRect.top + 16;
        const x2 = rRect.left - cRect.left + 40;
        const y2 = rRect.top - cRect.top;

        connectorPath.setAttribute('d',
            `M ${x1},${y1} L ${x2},${y1} L ${x2},${y2}`
        );
    }

    if (connectorSvg) {
        drawConnector();
        window.addEventListener('resize', drawConnector);
    }

    const setupMockup = document.querySelector('.setup-mockup--interview');
    const rulesMockup = document.querySelector('.setup-mockup--rules');
    if (setupMockup) {
        const statusDelays = [1800, 4400, 7000];

        function whenPlayerReady(player) {
            return new Promise(resolve => {
                if (player.getLottie && player.getLottie()) {
                    resolve();
                } else {
                    player.addEventListener('ready', resolve, { once: true });
                    player.addEventListener('load', resolve, { once: true });
                }
            });
        }

        observeVisibility(setupMockup, () => {
            if (!setupMockup.classList.contains('is-animating')) {
                setupMockup.classList.add('is-animating');
                if (rulesMockup) rulesMockup.classList.add('is-animating');

                const players = setupMockup.querySelectorAll('.setup-chat-status-icon');
                players.forEach((player, i) => {
                    const statusEl = player.closest('.setup-chat-status');
                    const textEl = statusEl.querySelector('span:last-child');
                    const doneText = statusEl.dataset.doneText;

                    whenPlayerReady(player).then(() => {
                        setTimeout(() => {
                            player.seek(0);
                            player.play();
                            setTimeout(() => {
                                player.pause();
                                if (doneText && textEl) textEl.textContent = doneText;
                            }, 4000);
                        }, statusDelays[i]);
                    });
                });
            }
        }, () => {}, '0px 0px -60px 0px');
    }


    /* Mobile integrations list toggle */
    const integrationsPanel = document.querySelector('.integrations-panel');
    const integrationsToggle = document.querySelector('[data-integrations-toggle]');

    if (integrationsPanel && integrationsToggle) {
        integrationsToggle.addEventListener('click', () => {
            const isExpanded = integrationsPanel.classList.toggle('is-expanded');
            integrationsToggle.setAttribute('aria-expanded', String(isExpanded));
            integrationsToggle.textContent = isExpanded
                ? 'Show fewer integrations'
                : 'Show more integrations';
        });
    }


    /* ------------------------------------------------
       Scroll Reveal
       Adds .revealed to .reveal elements when they
       enter the viewport via IntersectionObserver
       ------------------------------------------------ */
    const revealElements = document.querySelectorAll('.reveal');

    if (revealElements.length > 0 && 'IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.05,
            rootMargin: '0px 0px 40px 0px'
        });

        revealElements.forEach(el => revealObserver.observe(el));
    }

});
