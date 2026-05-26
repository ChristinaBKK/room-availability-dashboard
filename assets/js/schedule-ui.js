// Schedule dashboard UI, alerts, and room filter interactions.
window.AppScheduleUi = {
    createScheduleUi({
        formatDate,
        normalizeDateFormat,
        getTodayInputDate,
        getBRoomInventory,
        isRoomBlocked,
        parseTime,
        getExamDetailsForRoom,
        loadScheduleForDate,
        getState,
        setState
    }) {
        function getSelectedDate() {
            const dateInput = document.getElementById('scheduleDate');
            if (!dateInput || !dateInput.value) return null;
            return dateInput.value.replace(/-/g, '/');
        }

        function updateExamRoomsDisplay() {
            const list = document.getElementById('examRoomsList');
            if (!list) return;

            const { examRooms } = getState();
            if (examRooms.size === 0) {
                list.textContent = 'No exam rooms identified yet';
                return;
            }

            const rooms = [...examRooms].sort();
            list.textContent = rooms.join(', ');
        }

        function populateFilters() {
            const { filtersInitialized, selectedRooms } = getState();
            const scheduleDate = document.getElementById('scheduleDate');
            const bookingRoom = document.getElementById('bookingRoom');
            const bookingDate = document.getElementById('bookingDate');
            const currentScheduleValue = scheduleDate.value;
            const currentBookingDateValue = bookingDate.value;
            const currentBookingRoom = bookingRoom.value;
            const today = getTodayInputDate();

            if (!filtersInitialized) {
                scheduleDate.value = today;
                bookingDate.value = today;
                setState({ filtersInitialized: true });
            } else {
                scheduleDate.value = currentScheduleValue || today;
                bookingDate.value = currentBookingDateValue || today;
            }

            const bRoomsOnly = getBRoomInventory()
                .map(room => ({ room, display: room }))
                .sort((a, b) => a.room.localeCompare(b.room));

            const nextSelectedRooms = new Set([...selectedRooms].filter(room => bRoomsOnly.some(entry => entry.room === room)));
            setState({ selectedRooms: nextSelectedRooms });
            const groups = {
                Seminar: bRoomsOnly.filter(room => room.room.includes('Seminar')),
                'Floor 1': bRoomsOnly.filter(room => /^B1/.test(room.room)),
                'Floor 2': bRoomsOnly.filter(room => /^B2/.test(room.room)),
                'Floor 3': bRoomsOnly.filter(room => /^B3/.test(room.room)),
                'Floor 4': bRoomsOnly.filter(room => /^B4/.test(room.room))
            };
            const panel = document.getElementById('roomFilterPanel');
            let html = '<div class="room-chip-group"><div class="room-chip-row">';
            html += `<button class="room-chip all-chip${nextSelectedRooms.size === 0 ? ' active' : ''}" data-room="" type="button">All Rooms</button>`;
            html += '</div></div>';
            for (const [groupName, rooms] of Object.entries(groups)) {
                if (!rooms.length) continue;
                html += `<div class="room-chip-group"><div class="room-chip-group-label">${groupName}</div><div class="room-chip-row">`;
                rooms.forEach(room => {
                    const label = room.display + (isRoomBlocked(room.room) ? ' ✕' : '');
                    html += `<button class="room-chip${nextSelectedRooms.has(room.room) ? ' active' : ''}" data-room="${room.room}" type="button">${label}</button>`;
                });
                html += '</div></div>';
            }
            panel.innerHTML = html;
            panel.querySelectorAll('.room-chip').forEach(chip => chip.addEventListener('click', onRoomChipClick));

            const availableRooms = bRoomsOnly.filter(room => !isRoomBlocked(room.room));
            bookingRoom.innerHTML = '<option value="">Select a room</option>' +
                availableRooms.map(room => `<option value="${room.room}">${room.display}</option>`).join('');
            bookingRoom.value = currentBookingRoom && availableRooms.some(room => room.room === currentBookingRoom) ? currentBookingRoom : '';

            const label = document.getElementById('roomFilterLabel');
            label.textContent = nextSelectedRooms.size === 0 ? 'All Rooms' :
                nextSelectedRooms.size === 1 ? [...nextSelectedRooms][0] :
                `${nextSelectedRooms.size} rooms selected`;
        }

        async function onScheduleDateChange() {
            await loadScheduleForDate(getSelectedDate(), true);
        }

        function isIBDPExam(session) {
            return session.isExam && (session.component || '').toUpperCase().startsWith('IBDP');
        }

        function detectConflicts(sessions) {
            const conflicts = [];
            const notices = [];
            const roomSessions = {};
            sessions.forEach(session => {
                if (!roomSessions[session.room]) roomSessions[session.room] = [];
                roomSessions[session.room].push(session);
            });

            for (const room in roomSessions) {
                const roomSessionsList = roomSessions[room];
                const sessionsByDate = {};
                roomSessionsList.forEach(session => {
                    if (!sessionsByDate[session.date]) sessionsByDate[session.date] = [];
                    sessionsByDate[session.date].push(session);
                });

                for (const date in sessionsByDate) {
                    const daySessions = sessionsByDate[date].sort((a, b) => parseTime(a.start) - parseTime(b.start));
                    for (let index = 0; index < daySessions.length; index++) {
                        for (let compareIndex = index + 1; compareIndex < daySessions.length; compareIndex++) {
                            const first = daySessions[index];
                            const second = daySessions[compareIndex];
                            const firstStart = parseTime(first.start);
                            const firstEnd = parseTime(first.end);
                            const secondStart = parseTime(second.start);
                            const secondEnd = parseTime(second.end);
                            if (firstStart < secondEnd && firstEnd > secondStart) {
                                if (isIBDPExam(first) && isIBDPExam(second)) continue;
                                const sameTeacher = first.teacher && second.teacher && first.teacher === second.teacher;
                                if (sameTeacher) {
                                    notices.push({ room, sessions: [first, second] });
                                } else {
                                    conflicts.push({ room, sessions: [first, second] });
                                }
                            }
                        }
                    }
                }
            }

            return { conflicts, notices };
        }

        function updateExamAlerts() {
            const selectedDate = getSelectedDate();
            if (!selectedDate) return;

            const { examDates } = getState();
            const examSection = document.getElementById('examAlertSection');
            const examList = document.getElementById('examAlertList');
            const examDayRooms = [];
            const protectionRooms = [];

            for (const [room, dates] of examDates) {
                if (!room.startsWith('B')) continue;

                if (dates.has(selectedDate)) {
                    const examInfo = getExamDetailsForRoom(room, selectedDate);
                    examDayRooms.push({ room, examInfo });
                    continue;
                }

                const [year, month, day] = selectedDate.split('/').map(Number);
                const checkDate = new Date(year, month - 1, day, 12, 0, 0);
                checkDate.setDate(checkDate.getDate() + 1);
                const nextDay = `${checkDate.getFullYear()}/${String(checkDate.getMonth() + 1).padStart(2, '0')}/${String(checkDate.getDate()).padStart(2, '0')}`;

                if (dates.has(nextDay)) {
                    const examInfo = getExamDetailsForRoom(room, nextDay);
                    protectionRooms.push({ room, examInfo, nextDay });
                }
            }

            if (examDayRooms.length === 0 && protectionRooms.length === 0) {
                examSection.style.display = 'none';
                return;
            }

            examSection.style.display = 'block';
            let html = '';

            if (examDayRooms.length > 0) {
                html += examDayRooms.map(roomInfo => {
                    let details = 'Exam scheduled';
                    if (roomInfo.examInfo) {
                        details = `Time: ${roomInfo.examInfo.time || 'N/A'}${roomInfo.examInfo.code ? ' | ' + roomInfo.examInfo.code : ''}${roomInfo.examInfo.component ? ' | ' + roomInfo.examInfo.component : ''}`;
                    }
                    return `
                        <div class="exam-item">
                            <div class="room">${roomInfo.room} <span class="tag tag-exam">Exam</span></div>
                            <div class="details">${details}</div>
                        </div>
                    `;
                }).join('');
            }

            if (protectionRooms.length > 0) {
                html += protectionRooms.map(roomInfo => `
                    <div class="exam-item">
                        <div class="room">${roomInfo.room} <span class="tag tag-exam">Exam Protection</span></div>
                        <div class="details">Exam on ${formatDate(roomInfo.nextDay)} - room cannot be booked today</div>
                    </div>
                `).join('');
            }

            examList.innerHTML = html;
        }

        function updateDashboard() {
            const { allScheduleData, allBookingsData, selectedRooms } = getState();
            const selectedDate = getSelectedDate();
            const selectedRoomList = selectedRooms.size > 0 ? [...selectedRooms] : null;

            if (!selectedDate) {
                document.getElementById('roomGrid').innerHTML = '<div class="no-session"><h2>Please select a date</h2></div>';
                return;
            }

            let allSessions = [...allScheduleData];
            allBookingsData.forEach(booking => {
                allSessions.push({
                    date: booking.date,
                    start: booking.start,
                    end: booking.end,
                    component: booking.title,
                    room: booking.room,
                    teacher: booking.teacher
                });
            });

            let filteredSessions = allSessions.filter(session => normalizeDateFormat(session.date) === selectedDate);
            if (selectedRoomList) filteredSessions = filteredSessions.filter(session => selectedRoomList.includes(session.room));

            const { conflicts, notices } = detectConflicts(allSessions);
            const selectedDateConflicts = conflicts.filter(conflict => normalizeDateFormat(conflict.sessions[0].date) === selectedDate);
            const selectedDateNotices = notices.filter(notice => normalizeDateFormat(notice.sessions[0].date) === selectedDate);

            const conflictSection = document.getElementById('conflictSection');
            if (selectedDateConflicts.length > 0) {
                conflictSection.style.display = 'block';
                document.getElementById('conflictList').innerHTML = selectedDateConflicts.map(conflict => `
                    <div class="conflict-item">
                        <div class="room">${conflict.room} (${conflict.sessions[0].start}-${conflict.sessions[0].end})</div>
                        <div class="details">${conflict.sessions.map(session => session.teacher ? `${session.teacher}: ${session.component}` : session.component).join('<br>')}</div>
                    </div>
                `).join('');
            } else {
                conflictSection.style.display = 'none';
            }

            const noticeSection = document.getElementById('noticeSection');
            if (selectedDateNotices.length > 0) {
                noticeSection.style.display = 'block';
                document.getElementById('noticeList').innerHTML = selectedDateNotices.map(notice => `
                    <div class="exam-item">
                        <div class="room">${notice.room} (${notice.sessions[0].start}-${notice.sessions[0].end})</div>
                        <div class="details">${notice.sessions.map(session => session.teacher ? `${session.teacher}: ${session.component}` : session.component).join('<br>')}</div>
                    </div>
                `).join('');
            } else {
                noticeSection.style.display = 'none';
            }

            const roomSessions = {};
            filteredSessions.forEach(session => {
                if (!roomSessions[session.room]) roomSessions[session.room] = [];
                roomSessions[session.room].push(session);
            });

            for (const room in roomSessions) {
                roomSessions[room].sort((a, b) => parseTime(a.start) - parseTime(b.start));
            }

            const bRoomInventory = getBRoomInventory();
            const totalBookableBRooms = bRoomInventory.filter(room => !isRoomBlocked(room)).length;
            const usedBRooms = Object.keys(roomSessions).filter(room => room.startsWith('B')).length;
            const usedBookableBRooms = Object.keys(roomSessions).filter(room => room.startsWith('B') && !isRoomBlocked(room)).length;
            const availableBookableBRooms = Math.max(0, totalBookableBRooms - usedBookableBRooms);

            document.getElementById('totalRooms').textContent = usedBRooms;
            document.getElementById('totalSessions').textContent = filteredSessions.length;
            document.getElementById('availableRooms').textContent = availableBookableBRooms;
            document.getElementById('conflictCount').textContent = selectedDateConflicts.length;
            document.getElementById('conflictCount').style.color = selectedDateConflicts.length > 0 ? '#ef4444' : '#667eea';
            const noticesBadge = document.getElementById('noticesCount');
            if (noticesBadge) {
                noticesBadge.textContent = selectedDateNotices.length;
                noticesBadge.style.color = selectedDateNotices.length > 0 ? '#f59e0b' : '#667eea';
            }

            const roomGrid = document.getElementById('roomGrid');
            const sortedRooms = Object.keys(roomSessions).filter(room => room.startsWith('B')).sort();

            if (sortedRooms.length === 0) {
                roomGrid.innerHTML = '<div class="no-session"><h2>No sessions scheduled for this date</h2></div>';
                return;
            }

            let html = '';
            html += sortedRooms.map(room => {
                const sessions = roomSessions[room];
                const hasExamProtection = sessions.some(session => session.isExamProtection);
                const hasExam = sessions.some(session => session.isExam && !session.isExamProtection);

                let headerTag = '';
                if (hasExam) {
                    headerTag = ' <span class="tag tag-exam" style="font-size:11px;">Exam</span>';
                } else if (hasExamProtection) {
                    headerTag = ' <span class="tag tag-protection" style="font-size:11px;">Exam Protection</span>';
                }

                return `
                    <div class="room-card">
                        <div class="room-card-header">
                            <h3>${room}${headerTag}</h3>
                            <span class="session-count">${sessions.length} sessions</span>
                        </div>
                        <div class="room-card-body">
                            ${sessions.map(session => {
                                const isExam = session.isExam || false;
                                const examTag = isExam && !(session.isExamProtection || false)
                                    ? '<span class="tag tag-exam">Exam</span>'
                                    : '';
                                return `
                                    <div class="session-item">
                                        <div class="time">${session.start} - ${session.end} ${examTag}</div>
                                        <div class="component">${session.component}</div>
                                        <div class="meta">${session.teacher ? `<span class="tag tag-general">${session.teacher}</span>` : ''}</div>
                                    </div>
                                `;
                            }).join('')}
                            ${hasExamProtection ? (() => {
                                const [year, month, day] = selectedDate.split('/').map(Number);
                                const tomorrow = new Date(year, month - 1, day);
                                tomorrow.setDate(tomorrow.getDate() + 1);
                                const tomorrowStr = `${tomorrow.getFullYear()}/${String(tomorrow.getMonth() + 1).padStart(2, '0')}/${String(tomorrow.getDate()).padStart(2, '0')}`;
                                const examSession = getExamDetailsForRoom(room, tomorrowStr);
                                if (examSession) {
                                    const examTime = examSession.start && examSession.end ? ` (${examSession.start}–${examSession.end})` : '';
                                    return `<div class="exam-protection-banner"><span class="tag tag-protection">Exam tomorrow: ${examSession.component}${examTime}</span></div>`;
                                }
                                return '<div class="exam-protection-banner"><span class="tag tag-protection">Exam tomorrow</span></div>';
                            })() : ''}
                        </div>
                    </div>
                `;
            }).join('');

            roomGrid.innerHTML = html;
        }

        function onRoomChipClick(event) {
            const { selectedRooms } = getState();
            const chip = event.currentTarget;
            const room = chip.dataset.room;
            const panel = document.getElementById('roomFilterPanel');
            const nextSelectedRooms = new Set(selectedRooms);

            if (room === '') {
                nextSelectedRooms.clear();
                panel.querySelectorAll('.room-chip').forEach(roomChip => roomChip.classList.remove('active'));
                chip.classList.add('active');
            } else {
                panel.querySelector('.all-chip').classList.remove('active');
                if (nextSelectedRooms.has(room)) {
                    nextSelectedRooms.delete(room);
                    chip.classList.remove('active');
                } else {
                    nextSelectedRooms.add(room);
                    chip.classList.add('active');
                }
                if (nextSelectedRooms.size === 0) {
                    panel.querySelector('.all-chip').classList.add('active');
                }
            }

            setState({ selectedRooms: nextSelectedRooms });
            const label = document.getElementById('roomFilterLabel');
            label.textContent = nextSelectedRooms.size === 0 ? 'All Rooms' :
                nextSelectedRooms.size === 1 ? [...nextSelectedRooms][0] :
                `${nextSelectedRooms.size} rooms selected`;
            updateDashboard();
        }

        function initScheduleUi() {
            const roomFilterBtn = document.getElementById('roomFilterBtn');
            if (roomFilterBtn) {
                roomFilterBtn.addEventListener('click', function(event) {
                    event.stopPropagation();
                    const panel = document.getElementById('roomFilterPanel');
                    const isOpen = panel.classList.contains('open');
                    panel.classList.toggle('open', !isOpen);
                    this.classList.toggle('open', !isOpen);
                });
            }

            document.addEventListener('click', function(event) {
                const wrap = document.getElementById('roomFilterWrap');
                if (wrap && !wrap.contains(event.target)) {
                    document.getElementById('roomFilterPanel').classList.remove('open');
                    document.getElementById('roomFilterBtn').classList.remove('open');
                }
            });
        }

        return {
            initScheduleUi,
            getSelectedDate,
            updateExamRoomsDisplay,
            populateFilters,
            onScheduleDateChange,
            updateExamAlerts,
            updateDashboard
        };
    }
};
