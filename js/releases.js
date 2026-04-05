/**
 * CognisReleases — Dynamic GitHub release & download widget
 *
 * Fetches releases from a GitHub repo, identifies the latest stable and
 * pre-release versions, and renders download cards with platform-specific
 * asset links.
 *
 * Usage:
 *   <div id="releases"></div>
 *   <script src="/js/releases.js"></script>
 *   <script>
 *     CognisReleases.init({
 *       repo: 'Cognisn/spark',
 *       container: '#releases',
 *       pypi: 'cognisn-spark',           // optional — show pip install
 *       pypiExtras: ['postgresql', ...],  // optional — show extras
 *       platforms: [
 *         { label: 'macOS (Apple Silicon)', os: 'macos', arch: 'arm64', format: 'dmg', icon: 'apple' },
 *         { label: 'macOS (Intel)',         os: 'macos', arch: 'x86_64', format: 'dmg', icon: 'apple' },
 *         { label: 'Windows',              os: 'windows', arch: 'x86_64', format: 'exe', icon: 'windows' },
 *         { label: 'Linux (x86_64)',       os: 'linux', arch: 'x86_64', format: 'AppImage', icon: 'linux' },
 *         { label: 'Linux (ARM64)',        os: 'linux', arch: 'arm64', format: 'bin', icon: 'linux' },
 *       ]
 *     });
 *   </script>
 */

const CognisReleases = (() => {

    // ── SVG icons for each platform ──────────────────────────────────────

    const ICONS = {
        apple: '<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>',
        windows: '<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/></svg>',
        linux: '<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.368 1.884 1.43.39.03.8-.066 1.109-.199.69-.3 1.07-1.269 1.07-1.269.573-.445 1.224-1.086 1.585-1.951.186-.443.32-.896.185-1.29-.135-.39-.45-.669-.899-.869a2.51 2.51 0 00-.322-.129c.062-.31.1-.641.075-.985-.052-.566-.293-1.149-.635-1.692l-.016-.024c-.482-.733-1.108-1.378-1.678-1.846-.537-.443-1.063-.792-1.469-.903-.199-.068-.368-.073-.505-.073-.128 0-.225.022-.297.037h-.014l-.034.004c-.043-.057-.1-.106-.146-.169-.134-.178-.27-.39-.413-.665-.143-.276-.283-.554-.397-.858a8.66 8.66 0 00-.452-1.164c-.208-.404-.403-.731-.588-.993-.199-.275-.374-.434-.545-.564-.171-.129-.312-.194-.452-.248-.14-.06-.275-.098-.426-.144-.3-.098-.638-.197-.899-.466a.38.38 0 00-.065-.047c-.37-.234-.774-.26-1.137-.168z"/></svg>',
        package: '<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M21 16.5c0 .38-.21.71-.53.88l-7.9 4.44c-.16.12-.36.18-.57.18-.21 0-.41-.06-.57-.18l-7.9-4.44A.991.991 0 013 16.5v-9c0-.38.21-.71.53-.88l7.9-4.44c.16-.12.36-.18.57-.18.21 0 .41.06.57.18l7.9 4.44c.32.17.53.5.53.88v9zM12 4.15L6.04 7.5 12 10.85l5.96-3.35L12 4.15zM5 15.91l6 3.38v-6.71L5 9.21v6.7zm14 0v-6.7l-6 3.37v6.71l6-3.38z"/></svg>'
    };

    // ── Format helpers ───────────────────────────────────────────────────

    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        const mb = bytes / (1024 * 1024);
        return mb.toFixed(mb < 10 ? 1 : 0) + ' MB';
    }

    function formatDate(dateStr) {
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    }

    function formatFormatLabel(format) {
        const labels = {
            dmg: 'DMG installer',
            exe: 'NSIS installer',
            AppImage: 'AppImage',
            bin: 'Standalone binary',
            deb: 'Debian package',
            rpm: 'RPM package',
            msi: 'MSI installer',
            zip: 'ZIP archive',
            'tar.gz': 'Tarball'
        };
        return labels[format] || format;
    }

    // ── Asset matching ───────────────────────────────────────────────────

    /**
     * Match a platform config against release assets.
     *
     * Matching strategy (in priority order):
     *   1. Installer assets (DMG, EXE setup, AppImage) — preferred
     *   2. Standalone binaries — fallback
     *
     * The asset filename must contain the os and arch strings.
     * For format matching:
     *   - 'dmg'      → filename ends with .dmg
     *   - 'exe'      → filename ends with -setup.exe or .exe (prefer setup)
     *   - 'AppImage' → filename ends with .AppImage
     *   - 'bin'      → binary without extension matching os + arch
     */
    function matchAsset(assets, platform) {
        const { os, arch, format } = platform;
        const nameLower = (a) => a.name.toLowerCase();

        // Filter to assets containing the os and arch
        const candidates = assets.filter(a => {
            const n = nameLower(a);
            return n.includes(os.toLowerCase()) && n.includes(arch.toLowerCase());
        });

        if (candidates.length === 0) return null;

        // Try to find the preferred installer format
        let match = null;

        if (format === 'dmg') {
            match = candidates.find(a => a.name.endsWith('.dmg'));
        } else if (format === 'exe') {
            // Prefer the -setup.exe installer over raw .exe
            match = candidates.find(a => a.name.endsWith('-setup.exe'))
                 || candidates.find(a => a.name.endsWith('.exe'));
        } else if (format === 'AppImage') {
            // Match project AppImages (contain version), not tools like appimagetool
            match = candidates.find(a => a.name.endsWith('.AppImage') && !a.name.startsWith('appimagetool'));
        } else if (format === 'deb') {
            match = candidates.find(a => a.name.endsWith('.deb'));
        } else if (format === 'rpm') {
            match = candidates.find(a => a.name.endsWith('.rpm'));
        } else if (format === 'msi') {
            match = candidates.find(a => a.name.endsWith('.msi'));
        } else if (format === 'zip') {
            match = candidates.find(a => a.name.endsWith('.zip'));
        } else if (format === 'tar.gz') {
            match = candidates.find(a => a.name.endsWith('.tar.gz'));
        } else if (format === 'bin') {
            // Standalone binary — no extension, not an installer
            match = candidates.find(a => {
                const n = a.name;
                return !n.includes('.') || (!n.endsWith('.dmg') && !n.endsWith('.exe') && !n.endsWith('.AppImage'));
            });
        }

        return match || null;
    }

    // ── HTML rendering ───────────────────────────────────────────────────

    function renderReleaseSection(release, platforms, type) {
        const isPrerelease = type === 'prerelease';
        const badgeClass = isPrerelease ? 'release-badge--pre' : 'release-badge--stable';
        const badgeText = isPrerelease ? 'Pre-release' : 'Latest Release';

        // Build download table rows
        const downloadRows = platforms.map(p => {
            const asset = matchAsset(release.assets, p);
            if (!asset) return '';

            const icon = ICONS[p.icon] || ICONS.package;
            return `
                <tr>
                    <td class="release-table__platform">
                        <span class="release-table__icon">${icon}</span>
                        ${escapeHtml(p.label)}
                    </td>
                    <td class="release-table__format">${formatFormatLabel(p.format)}</td>
                    <td class="release-table__arch">${p.arch}</td>
                    <td class="release-table__size">${formatBytes(asset.size)}</td>
                    <td class="release-table__action">
                        <a href="${asset.browser_download_url}" class="btn btn-primary btn--sm" download>Download</a>
                    </td>
                </tr>`;
        }).filter(Boolean);

        // Release body — render first few lines as summary
        const body = release.body || '';
        const summary = renderMarkdownSummary(body);

        return `
            <div class="release-section${isPrerelease ? ' release-section--pre' : ''}">
                <div class="release-header">
                    <div class="release-header__title">
                        <span class="release-badge ${badgeClass}">${badgeText}</span>
                        <h3 class="release-version">${escapeHtml(release.name || release.tag_name)}</h3>
                    </div>
                    <div class="release-header__meta">
                        <span class="release-date">${formatDate(release.published_at)}</span>
                        <a href="${release.html_url}" target="_blank" rel="noopener" class="release-github-link">View on GitHub &rarr;</a>
                    </div>
                </div>
                ${summary ? `<div class="release-notes">${summary}</div>` : ''}
                ${downloadRows.length > 0 ? `
                    <div class="release-downloads">
                        <h4 class="release-downloads__heading">Downloads</h4>
                        <div class="release-table-wrap">
                            <table class="release-table">
                                <thead>
                                    <tr>
                                        <th>Platform</th>
                                        <th>Format</th>
                                        <th>Architecture</th>
                                        <th>Size</th>
                                        <th></th>
                                    </tr>
                                </thead>
                                <tbody>${downloadRows.join('')}</tbody>
                            </table>
                        </div>
                    </div>
                ` : ''}
            </div>`;
    }

    function renderPyPI(pypi, extras) {
        if (!pypi) return '';

        let extrasHtml = '';
        if (extras && extras.length > 0) {
            const lines = extras.map(e => `pip install ${pypi}[${e}]`).join('\n');
            extrasHtml = `
                <p style="margin-top: 1rem;">Optional extras:</p>
                <pre><code>${escapeHtml(lines)}</code></pre>`;
        }

        return `
            <div class="release-section release-section--pypi">
                <div class="release-header">
                    <div class="release-header__title">
                        <span class="release-badge release-badge--pypi">PyPI</span>
                        <h3 class="release-version">Install via pip</h3>
                    </div>
                </div>
                <pre><code>pip install ${escapeHtml(pypi)}</code></pre>
                ${extrasHtml}
            </div>`;
    }

    function renderError(message) {
        return `<div class="release-section release-section--error">
            <p style="color: var(--app-text-muted); font-style: italic;">${escapeHtml(message)}</p>
        </div>`;
    }

    function renderLoading() {
        return `<div class="release-section release-loading">
            <div class="release-loading__spinner"></div>
            <p>Loading releases&hellip;</p>
        </div>`;
    }

    // ── Markdown-lite summary renderer ───────────────────────────────────

    function renderMarkdownSummary(md) {
        if (!md) return '';

        // Extract highlights section if present
        const lines = md.split('\n');
        const highlights = [];
        let inHighlights = false;

        for (const line of lines) {
            if (/^###?\s+highlights?/i.test(line)) {
                inHighlights = true;
                continue;
            }
            if (inHighlights && /^###?\s+/.test(line)) break;
            if (inHighlights && line.startsWith('- ')) {
                // Strip **bold** markers and render as list items
                highlights.push(line.slice(2).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'));
            }
        }

        if (highlights.length === 0) return '';

        return '<ul>' + highlights.map(h => `<li>${h}</li>`).join('') + '</ul>';
    }

    // ── Safety ───────────────────────────────────────────────────────────

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ── Main ─────────────────────────────────────────────────────────────

    async function init(config) {
        const {
            repo,
            container,
            platforms = [],
            pypi = null,
            pypiExtras = []
        } = config;

        const el = document.querySelector(container);
        if (!el) {
            console.error(`CognisReleases: container "${container}" not found`);
            return;
        }

        el.innerHTML = renderLoading();

        try {
            const response = await fetch(`https://api.github.com/repos/${repo}/releases`, {
                headers: { 'Accept': 'application/vnd.github.v3+json' }
            });

            if (!response.ok) {
                throw new Error(`GitHub API returned ${response.status}`);
            }

            const releases = await response.json();

            // Filter out drafts
            const published = releases.filter(r => !r.draft);

            // Find latest stable (non-prerelease) and latest prerelease
            const stable = published.find(r => !r.prerelease) || null;
            const prerelease = published.find(r => r.prerelease) || null;

            let html = '';

            if (!stable && !prerelease) {
                html = renderError('No releases found for this project yet.');
            } else {
                if (stable) {
                    html += renderReleaseSection(stable, platforms, 'stable');
                }
                if (prerelease) {
                    // Don't show prerelease if it's the same tag as stable
                    if (!stable || prerelease.tag_name !== stable.tag_name) {
                        html += renderReleaseSection(prerelease, platforms, 'prerelease');
                    }
                }
            }

            // PyPI section
            html += renderPyPI(pypi, pypiExtras);

            el.innerHTML = html;

        } catch (err) {
            console.error('CognisReleases: failed to fetch releases', err);
            el.innerHTML = renderError(
                'Unable to load release information. Visit the GitHub repository for downloads.'
            ) + renderPyPI(pypi, pypiExtras);
        }
    }

    return { init };

})();
