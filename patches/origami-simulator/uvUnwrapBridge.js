/**
 * Bridge for uv-unwrap.html → Origami Simulator integration.
 * Loads crease patterns from sessionStorage or postMessage when ?autoload=uv.
 */
(function () {
    var STORAGE_KEY = 'uvFoldPatternSvg';

    function svgToDataUrl(svgText) {
        return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgText)));
    }

    function notifyParentReady() {
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({ type: 'uv-fold-bridge-ready' }, window.location.origin);
        }
    }

    function loadSvgString(svgText) {
        if (!svgText || !globals || !globals.pattern || !globals.pattern.loadSVG) {
            return false;
        }
        try {
            globals.pattern.loadSVG(svgToDataUrl(svgText), false);
            if (globals.setCreasePercent) {
                globals.setCreasePercent(1);
            }
            notifyParentReady();
            return true;
        } catch (err) {
            console.error('uvUnwrapBridge: failed to load SVG', err);
            return false;
        }
    }

    function tryAutoloadFromStorage() {
        var params = new URLSearchParams(window.location.search);
        if (!params.has('autoload')) {
            return;
        }
        var svg = sessionStorage.getItem(STORAGE_KEY);
        if (svg) {
            loadSvgString(svg);
        } else {
            notifyParentReady();
        }
    }

    window.addEventListener('message', function (e) {
        if (e.origin !== window.location.origin) {
            return;
        }
        if (!e.data || e.data.type !== 'uv-fold-svg') {
            return;
        }
        loadSvgString(e.data.svg);
    });

    $(function () {
        if (!/[?&]autoload=/.test(window.location.search)) {
            return;
        }
        var attempts = 0;
        var timer = setInterval(function () {
            attempts++;
            if (globals && globals.pattern && globals.pattern.loadSVG) {
                clearInterval(timer);
                tryAutoloadFromStorage();
            } else if (attempts > 400) {
                clearInterval(timer);
                notifyParentReady();
            }
        }, 50);
    });
})();
