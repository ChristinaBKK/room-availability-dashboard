// Room range dashboard UI and interactions.
window.AppRoomViewUi = {
    createRoomViewUi({
        formatDate,
        normalizeDateFormat,
        getTodayInputDate,
        getBRoomInventory,
        isRoomBlocked,
        parseTime,
        ensureDayDataLoaded,
        getState,
        setState
    }) {
        function toInputDateValue(dateStr) {
            return dateStr ? dateStr.replace(/\//g, '-') : '';
        }

        function getDateRange(startDate, endDate) {
            const dates = [];
            const startParts = startDate.split('/').map(Number);
            const endParts = endDate.split('/').map(Number);
            const cursor = new Date(startParts[0], startParts[1] - 1, startParts[2]);
            const lastDate = new Date(endParts[0], endParts[1] - 1, endParts[2]);

            while (cursor <= lastDate) {
                dates.push(`${cursor.getFullYear()}/${String(cursor.getMonth() + 1).padStart(2, '0')}/${String(cursor.getDate()).padStart(2, '0')}`);
                cursor.setDate(cursor.getDate() + 1);
            }

            return dates;
        }

        function getRoomInventory() {
            return getBRoomInventory()
                .map(room => ({ room, display: room }))
                .sort((a, b) => a.room.localeCompare(b.room));
        }

        function syncRoomViewFilters() {
            const panel = document.getElementById('roomViewFilterPanel');
            const label = document.getElementById('roomViewFilterLabel');
            if (!panel || !label) return;

            const { roomViewSelectedRooms } = getState();
            const rooms = getRoomInventory();
            const nextSelectedRooms = new Set([...roomViewSelectedRooms].filter(room => rooms.some(entry => entry.room === room)));
            setState({ roomViewSelectedRooms: nextSelectedRooms });

            const groups = {
                Seminar: rooms.filter(room => room.room.includes('Seminar')),
                'Floor 1': rooms.filter(room => /^B1/.test(room.room)),
                'Floor 2': rooms.filter(room => /^B2/.test(room.room)),
                'Floor 3': rooms.filter(room => /^B3/.test(room.room)),
                'Floor 4': rooms.filter(room => /^B4/.test(room.room))
            };

            let html = '<div class="room-view-chip-group"><div class="room-view-chip-row">';
            html += `<button class="room-view-chip room-view-all-chip${nextSelectedRooms.size === 0 ? ' active' : ''}" data-room="" type="button">All Rooms</button>`;
            html += '</div></div>';

            for (const [groupName, groupRooms] of Object.entries(groups)) {
                if (!groupRooms.length) continue;
                html += `<div class="room-view-chip-group"><div class="room-view-chip-group-label">${groupName}</div><div class="room-view-chip-row">`;
                groupRooms.forEach(room => {
                    const labelText = room.display + (isRoomBlocked(room.room) ? ' ✕' : '');
                    html += `<button class="room-view-chip${nextSelectedRooms.has(room.room) ? ' active' : ''}" data-room="${room.room}" type="button">${labelText}</button>`;
                });
                html += '</div></div>';
            }

            panel.innerHTML = html;
            panel.querySelectorAll('.room-view-chip').forEach(chip => chip.addEventListener('click', onRoomViewChipClick));

            label.textContent = nextSelectedRooms.size === 0 ? 'All Rooms' : nextSelectedRooms.size === 1 ? [...nextSelectedRooms][0] : `${nextSelectedRooms.size} rooms selected`;
        }

        function updateRoomViewSummary(roomCount, dateCount, sessionCount, occupiedCells) {
            const roomsEl = document.getElementById('roomViewRoomCount');
            const datesEl = document.getElementById('roomViewDateCount');
            const sessionsEl = document.getElementById('roomViewSessionCount');
            const cellsEl = document.getElementById('roomViewCellCount');

            if (roomsEl) roomsEl.textContent = String(roomCount);
            if (datesEl) datesEl.textContent = String(dateCount);
            if (sessionsEl) sessionsEl.textContent = String(sessionCount);
            if (cellsEl) cellsEl.textContent = String(occupiedCells);
        }

        function readRoomViewRange() {
            const startInput = document.getElementById('roomViewStartDate');
            const endInput = document.getElementById('roomViewEndDate');
            if (!startInput || !endInput) return null;

            let startDate = normalizeDateFormat(startInput.value || getTodayInputDate());
            let endDate = normalizeDateFormat(endInput.value || startDate);
            if (!startDate || !endDate) return null;

            if (startDate > endDate) {
                const swapped = startDate;
                startDate = endDate;
                endDate = swapped;
                startInput.value = toInputDateValue(startDate);
                endInput.value = toInputDateValue(endDate);
            }

            setState({ roomViewStartDate: startDate, roomViewEndDate: endDate });
            return { startDate, endDate };
        }

        function onRoomViewChipClick(event) {
            const { roomViewSelectedRooms } = getState();
            const chip = event.currentTarget;
            const room = chip.dataset.room;
            const panel = document.getElementById('roomViewFilterPanel');
            const nextSelectedRooms = new Set(roomViewSelectedRooms);

            if (room === '') {
                nextSelectedRooms.clear();
                panel.querySelectorAll('.room-view-chip').forEach(roomChip => roomChip.classList.remove('active'));
                chip.classList.add('active');
            } else {
                const allChip = panel.querySelector('.room-view-all-chip');
                if (allChip) allChip.classList.remove('active');

                if (nextSelectedRooms.has(room)) {
                    nextSelectedRooms.delete(room);
                    chip.classList.remove('active');
                } else {
                    nextSelectedRooms.add(room);
                    chip.classList.add('active');
                }

                if (nextSelectedRooms.size === 0 && allChip) {
                    allChip.classList.add('active');
                }
            }

            setState({ roomViewSelectedRooms: nextSelectedRooms });
            const label = document.getElementById('roomViewFilterLabel');
            if (label) {
                label.textContent = nextSelectedRooms.size === 0 ? 'All Rooms' : nextSelectedRooms.size === 1 ? [...nextSelectedRooms][0] : `${nextSelectedRooms.size} rooms selected`;
            }
            loadRoomViewRange();
        }

        function renderRoomViewContent(dates) {
            const content = document.getElementById('roomViewContent');
            if (!content) return;

            const { dayDataCache, roomViewSelectedRooms } = getState();
            const selectedRoomList = roomViewSelectedRooms.size > 0 ? [...roomViewSelectedRooms] : null;
            const roomInventory = getRoomInventory();
            const roomsToRender = roomInventory.filter(room => !selectedRoomList || selectedRoomList.includes(room.room));
            const roomData = new Map();
            let sessionCount = 0;
            let occupiedCells = 0;

            dates.forEach(date => {
                const cachedDay = dayDataCache.get(date) || { scheduleData: [], bookingsData: [] };
                const sessions = [
                    ...cachedDay.scheduleData.map(session => ({ ...session, source: 'schedule' })),
                    ...cachedDay.bookingsData.map(booking => ({
                        date: booking.date,
                        start: booking.start,
                        end: booking.end,
                        room: booking.room,
                        teacher: booking.teacher,
                        component: booking.title,
                        source: 'booking',
                        isExam: false,
                        isExamProtection: false
                    }))
                ];

                sessions.forEach(session => {
                    if (selectedRoomList && !selectedRoomList.includes(session.room)) return;
                    if (!roomData.has(session.room)) roomData.set(session.room, new Map());
                    if (!roomData.get(session.room).has(date)) roomData.get(session.room).set(date, []);
                    roomData.get(session.room).get(date).push(session);
                    sessionCount += 1;
                });
            });

            roomsToRender.forEach(room => {
                const dayMap = roomData.get(room.room);
                if (!dayMap) return;
                for (const sessions of dayMap.values()) {
                    if (sessions.length > 0) occupiedCells += 1;
                }
            });

            updateRoomViewSummary(roomsToRender.length, dates.length, sessionCount, occupiedCells);

            if (roomsToRender.length === 0) {
                content.innerHTML = '<div class="no-session"><h2>No rooms match the selected filters</h2></div>';
                return;
            }

            content.innerHTML = roomsToRender.map(room => {
                const dayMap = roomData.get(room.room) || new Map();
                const totalSessionsForRoom = [...dayMap.values()].reduce((total, sessions) => total + sessions.length, 0);

                return `
                    <div class="room-view-card">
                        <div class="room-view-card-header">
                            <h3>${room.room}${isRoomBlocked(room.room) ? ' <span class="tag tag-blocked">Blocked</span>' : ''}</h3>
                            <span class="session-count">${totalSessionsForRoom} sessions</span>
                        </div>
                        <div class="room-view-card-body">
                            <div class="room-view-date-grid">
                                ${dates.map(date => {
                                    const sessions = (dayMap.get(date) || []).slice().sort((a, b) => parseTime(a.start) - parseTime(b.start));
                                    const hasSessions = sessions.length > 0;
                                    return `
                                        <div class="room-view-day${hasSessions ? '' : ' empty'}">
                                            <div class="room-view-day-header">
                                                <span>${formatDate(date)}</span>
                                                <span class="room-view-day-count">${sessions.length}</span>
                                            </div>
                                            ${hasSessions ? sessions.map(session => {
                                                const tags = [];
                                                if (session.source === 'booking') tags.push('<span class="tag tag-general">Booking</span>');
                                                if (session.isExam) tags.push('<span class="tag tag-exam">Exam</span>');
                                                if (session.isExamProtection) tags.push('<span class="tag tag-protection">Protection</span>');
                                                if (session.teacher && session.source !== 'booking') tags.push(`<span class="tag tag-general">${session.teacher}</span>`);

                                                return `
                                                    <div class="room-view-session">
                                                        <div class="time">${session.start} - ${session.end}</div>
                                                        <div class="component">${session.component}</div>
                                                        <div class="meta">${tags.join('')}</div>
                                                    </div>
                                                `;
                                            }).join('') : '<div class="room-view-empty">No sessions</div>'}
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function loadRoomViewRange(force = false) {
            const range = readRoomViewRange();
            const content = document.getElementById('roomViewContent');
            if (!range || !content) {
                if (content) content.innerHTML = '<div class="no-session"><h2>Please select a date range</h2></div>';
                updateRoomViewSummary(0, 0, 0, 0);
                return;
            }

            const dates = getDateRange(range.startDate, range.endDate);
            await Promise.all(dates.map(date => ensureDayDataLoaded(date, force)));
            syncRoomViewFilters();
            renderRoomViewContent(dates);
        }

        function initRoomViewUi() {
            const startInput = document.getElementById('roomViewStartDate');
            const endInput = document.getElementById('roomViewEndDate');
            const filterBtn = document.getElementById('roomViewFilterBtn');
            const refreshBtn = document.getElementById('roomViewRefreshBtn');

            if (!startInput || !endInput || !filterBtn || !refreshBtn) {
                return;
            }

            if (!getState().roomViewInitialized) {
                const today = getTodayInputDate();
                startInput.value = today;
                endInput.value = today;
                setState({ roomViewInitialized: true, roomViewStartDate: normalizeDateFormat(today), roomViewEndDate: normalizeDateFormat(today) });
            } else {
                startInput.value = toInputDateValue(getState().roomViewStartDate || normalizeDateFormat(getTodayInputDate()));
                endInput.value = toInputDateValue(getState().roomViewEndDate || getState().roomViewStartDate || normalizeDateFormat(getTodayInputDate()));
            }

            startInput.addEventListener('change', () => loadRoomViewRange());
            endInput.addEventListener('change', () => loadRoomViewRange());

            filterBtn.addEventListener('click', function(event) {
                event.stopPropagation();
                const panel = document.getElementById('roomViewFilterPanel');
                const isOpen = panel.classList.contains('open');
                panel.classList.toggle('open', !isOpen);
                this.classList.toggle('open', !isOpen);
            });

            refreshBtn.addEventListener('click', () => loadRoomViewRange(true));

            document.addEventListener('click', function(event) {
                const wrap = document.getElementById('roomViewFilterWrap');
                if (wrap && !wrap.contains(event.target)) {
                    const panel = document.getElementById('roomViewFilterPanel');
                    if (panel) panel.classList.remove('open');
                    filterBtn.classList.remove('open');
                }
            });

            syncRoomViewFilters();
        }

        return {
            initRoomViewUi,
            loadRoomViewRange,
            syncRoomViewFilters
        };
    }
};