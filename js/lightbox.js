/**
 * Lightweight image lightbox
 *
 * Click any image inside a .screenshot to view it full-size.
 */

document.addEventListener('DOMContentLoaded', () => {

    // Build overlay via DOM (not innerHTML, to avoid any parsing issues)
    const overlay = document.createElement('div');
    overlay.id = 'lightbox';
    overlay.style.cssText = 'display:none; position:fixed; top:0; left:0; width:100%; height:100%; z-index:9999; background:rgba(0,0,0,0.9); cursor:zoom-out; flex-direction:column; align-items:center; justify-content:center; padding:2rem;';

    const lbImg = document.createElement('img');
    lbImg.style.cssText = 'max-width:90vw; max-height:80vh; border-radius:0.5rem; object-fit:contain;';

    const lbCaption = document.createElement('p');
    lbCaption.style.cssText = 'color:#aaa; font-size:0.875rem; margin-top:1rem; text-align:center;';

    overlay.appendChild(lbImg);
    overlay.appendChild(lbCaption);
    document.body.appendChild(overlay);

    function open(src, alt) {
        lbImg.src = src;
        lbCaption.textContent = alt;
        overlay.style.display = 'flex';
    }

    function close() {
        overlay.style.display = 'none';
        lbImg.src = '';
    }

    // Click to close
    overlay.addEventListener('click', close);

    // Escape to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.style.display === 'flex') close();
    });

    // Attach to all .screenshot figures
    document.querySelectorAll('.screenshot').forEach(fig => {
        const img = fig.querySelector('img');
        if (!img) return;
        fig.style.cursor = 'zoom-in';
        fig.addEventListener('click', () => {
            open(img.currentSrc || img.src, img.alt || '');
        });
    });
});
