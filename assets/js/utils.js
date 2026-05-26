// Shared date/time utilities used across app modules.
function formatDate(dateStr) {
    const parts = dateStr.includes('/') ? dateStr.split('/') : dateStr.split('-');
    const year = parts[0];
    const month = parts[1];
    const day = parts[2];
    const date = new Date(year, parseInt(month, 10) - 1, parseInt(day, 10));
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
}

function normalizeDateFormat(dateStr) {
    if (!dateStr) return '';
    const raw = String(dateStr).trim();
    if (!raw) return '';

    const parts = raw.includes('/') ? raw.split('/') : raw.includes('-') ? raw.split('-') : null;
    if (!parts || parts.length !== 3) return raw;

    const [y, m, d] = parts;
    return `${y}/${String(m).padStart(2, '0')}/${String(d).padStart(2, '0')}`;
}

function getDateVariants(dateStr) {
    const raw = String(dateStr || '').trim();
    const normalized = normalizeDateFormat(dateStr);
    if (!normalized && !raw) return [];
    const variants = new Set([
        normalized,
        normalized ? normalized.replace(/\//g, '-') : '',
        raw,
        raw ? raw.replace(/\//g, '-') : '',
        raw ? raw.replace(/-/g, '/') : ''
    ].filter(Boolean));
    return [...variants];
}

function parseTime(time) {
    const [hours, minutes] = time.split(':').map(Number);
    return hours * 60 + minutes;
}

function getTodayInputDate() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

function getTodayDisplayDate() {
    return getTodayInputDate().replace(/-/g, '/');
}

function displayDateToInputValue(displayDate) {
    return normalizeDateFormat(displayDate).replace(/\//g, '-');
}

Object.assign(window, {
    formatDate,
    normalizeDateFormat,
    getDateVariants,
    parseTime,
    getTodayInputDate,
    getTodayDisplayDate,
    displayDateToInputValue
});
