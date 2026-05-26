// Bookings tab UI, filters, and booking form interactions.
window.AppBookingsUi = {
    createBookingsUi({
        supabaseUrl,
        formatDate,
        normalizeDateFormat,
        displayDateToInputValue,
        getTodayDisplayDate,
        parseTime,
        normalizeRoom,
        getRequestHeaders,
        getSortedSelectedBookingDates,
        getBRoomInventory,
        isRoomBlocked,
        getExamProtectionMessage,
        ensureDayDataLoaded,
        loadBookingsForSelectedDates,
        invalidateCachedData,
        refreshActiveTabData,
        loadAllData,
        hasRoomTimeConflict,
        createBookingToDb,
        showAlert,
        closeModal,
        getState,
        setState
    }) {
        function renderBookingsDateChips() {
            const chips = document.getElementById('bookingsDateChips');
            if (!chips) return;

            const dates = getSortedSelectedBookingDates();
            if (dates.length === 0) {
                chips.innerHTML = '<span class="bookings-filter-empty">No dates selected.</span>';
                return;
            }

            chips.innerHTML = dates.map(date => `
                <span class="bookings-filter-chip">
                    ${formatDate(date)}
                    <button type="button" onclick="removeBookingsFilterDate('${date}')" aria-label="Remove ${date}">x</button>
                </span>
            `).join('');
        }

        function setBookingsAddMode(enabled) {
            setState({ bookingsAddMode: enabled });
            const addBtn = document.getElementById('bookingsDateAddBtn');
            if (!addBtn) return;
            addBtn.textContent = enabled ? 'Pick Date to Add...' : 'Add Another Date';
            addBtn.classList.toggle('is-armed', enabled);
            addBtn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
        }

        function setBookingsDateFilterToTodayOnly() {
            const today = getTodayDisplayDate();
            setState({ selectedBookingDates: new Set([today]) });
            const picker = document.getElementById('bookingsDatePicker');
            if (picker) picker.value = displayDateToInputValue(today);
            setBookingsAddMode(false);
            renderBookingsDateChips();
        }

        function addBookingsFilterDate(dateStr) {
            const normalized = normalizeDateFormat(dateStr);
            if (!normalized) return;
            const { selectedBookingDates } = getState();
            const nextDates = new Set(selectedBookingDates);
            nextDates.add(normalized);
            setState({ selectedBookingDates: nextDates });
            renderBookingsDateChips();
        }

        function setBookingsFilterSingleDate(dateStr) {
            const normalized = normalizeDateFormat(dateStr);
            if (!normalized) return;
            setState({ selectedBookingDates: new Set([normalized]) });
            const picker = document.getElementById('bookingsDatePicker');
            if (picker) picker.value = displayDateToInputValue(normalized);
            setBookingsAddMode(false);
            renderBookingsDateChips();
        }

        async function removeBookingsFilterDate(dateStr) {
            const { selectedBookingDates, activeTab } = getState();
            const nextDates = new Set(selectedBookingDates);
            nextDates.delete(normalizeDateFormat(dateStr));
            setState({ selectedBookingDates: nextDates });
            renderBookingsDateChips();
            if (activeTab === 'bookings') {
                await renderAllBookings(true);
            }
        }

        function initBookingsDateFilter() {
            const picker = document.getElementById('bookingsDatePicker');
            if (!picker) return;
            setBookingsDateFilterToTodayOnly();
            setBookingsAddMode(false);
        }

        async function refreshBookingsTabAfterFilterChange() {
            const { activeTab } = getState();
            if (activeTab === 'bookings') {
                await renderAllBookings(true);
            }
        }

        async function onBookingsDateAdd() {
            const { bookingsAddMode } = getState();
            setBookingsAddMode(!bookingsAddMode);
        }

        async function onBookingsDatePick() {
            const { bookingsAddMode } = getState();
            const picker = document.getElementById('bookingsDatePicker');
            if (!picker || !picker.value) return;

            if (bookingsAddMode) {
                addBookingsFilterDate(picker.value);
                setBookingsAddMode(false);
            } else {
                setBookingsFilterSingleDate(picker.value);
            }
            await refreshBookingsTabAfterFilterChange();
        }

        async function onBookingsDateTodayOnly() {
            setBookingsDateFilterToTodayOnly();
            await refreshBookingsTabAfterFilterChange();
        }

        async function onBookingsDateClear() {
            setState({ selectedBookingDates: new Set() });
            setBookingsAddMode(false);
            renderBookingsDateChips();
            await refreshBookingsTabAfterFilterChange();
        }

        function initBookingForm() {
            document.getElementById('recurringCheck').addEventListener('change', function() {
                document.getElementById('recurringOptions').classList.toggle('visible', this.checked);
            });

            document.querySelectorAll('.weekday-chip').forEach(chip => {
                chip.addEventListener('click', function() {
                    this.classList.toggle('selected');
                    const day = parseInt(this.dataset.day, 10);
                    const { selectedWeekdays } = getState();
                    const nextWeekdays = selectedWeekdays.includes(day)
                        ? selectedWeekdays.filter(currentDay => currentDay !== day)
                        : [...selectedWeekdays, day];
                    setState({ selectedWeekdays: nextWeekdays });
                });
            });

            ['bookingDate', 'bookingStart', 'bookingEnd'].forEach(id => {
                document.getElementById(id).addEventListener('change', updateRoomSuggestions);
            });

            document.getElementById('bookingForm').addEventListener('submit', function(event) {
                event.preventDefault();
                submitBooking();
            });

            document.getElementById('roomSuggestions').addEventListener('click', function(event) {
                if (event.target.classList.contains('room-chip') && !event.target.classList.contains('unavailable') && !event.target.classList.contains('exam-blocked')) {
                    document.querySelectorAll('.room-chip').forEach(chip => chip.classList.remove('selected'));
                    event.target.classList.add('selected');
                    document.getElementById('bookingRoom').value = event.target.dataset.room;
                    document.getElementById('bookingRoomError').style.display = 'none';
                }
            });
        }

        async function checkRoomAvailability() {
            const room = document.getElementById('bookingRoom').value;
            const date = document.getElementById('bookingDate').value.replace(/-/g, '/');
            const start = document.getElementById('bookingStart').value;
            const end = document.getElementById('bookingEnd').value;
            const errorDiv = document.getElementById('bookingRoomError');

            if (!room || !date || !start || !end) {
                errorDiv.style.display = 'none';
                return true;
            }

            if (isRoomBlocked(room)) {
                errorDiv.innerHTML = `<span style="color:#ef4444;">Room ${room} is blocked from booking. Please select another room.</span>`;
                errorDiv.style.display = 'block';
                return false;
            }

            const examMsg = getExamProtectionMessage(room, date);
            if (examMsg) {
                errorDiv.innerHTML = `<span style="color:#f59e0b;">${examMsg}. Please select another room or date.</span>`;
                errorDiv.style.display = 'block';
                return false;
            }

            const dayData = await ensureDayDataLoaded(date);
            const daySessions = [
                ...dayData.scheduleData,
                ...dayData.bookingsData.map(booking => ({ date: booking.date, start: booking.start, end: booking.end, room: booking.room }))
            ];

            if (hasRoomTimeConflict(room, date, start, end, [], daySessions)) {
                errorDiv.innerHTML = `<span style="color:#ef4444;">Room ${room} is already booked on ${formatDate(date)} for an overlapping time. Please select a different room or time.</span>`;
                errorDiv.style.display = 'block';
                return false;
            }

            errorDiv.style.display = 'none';
            return true;
        }

        async function updateRoomSuggestions() {
            const date = document.getElementById('bookingDate').value.replace(/-/g, '/');
            const start = document.getElementById('bookingStart').value;
            const end = document.getElementById('bookingEnd').value;
            const suggestions = document.getElementById('roomSuggestions');

            if (!date || !start || !end) {
                suggestions.innerHTML = '<span style="color:#94a3b8;">Select date and time to see available rooms</span>';
                return;
            }

            const dayData = await ensureDayDataLoaded(date);
            const daySessions = [
                ...dayData.scheduleData,
                ...dayData.bookingsData.map(booking => ({ date: booking.date, start: booking.start, end: booking.end, room: booking.room }))
            ].filter(session => normalizeDateFormat(session.date) === normalizeDateFormat(date));

            const available = [];
            const unavailable = [];
            const examBlocked = [];
            const availableForBooking = getBRoomInventory().filter(room => !isRoomBlocked(room));

            availableForBooking.sort().forEach(room => {
                const examMsg = getExamProtectionMessage(room, date);
                if (examMsg) {
                    examBlocked.push({ room, reason: examMsg });
                    return;
                }

                const roomDaySessions = daySessions.filter(session => normalizeRoom(session.room) === normalizeRoom(room));
                let availableNow = true;
                for (const session of roomDaySessions) {
                    if (parseTime(start) < parseTime(session.end) && parseTime(end) > parseTime(session.start)) {
                        availableNow = false;
                        break;
                    }
                }

                if (availableNow) {
                    available.push(room);
                } else {
                    unavailable.push(room);
                }
            });

            let html = '';

            if (available.length > 0) {
                html += available.map(room => `<div class="room-chip" data-room="${room}">${room} ✓</div>`).join('');
            }

            if (examBlocked.length > 0) {
                html += '<br><span style="color:#92400e; font-size:12px; margin-top:10px; display:block;">Exam Protected:</span>';
                html += examBlocked.map(room => `<div class="room-chip exam-blocked" title="${room.reason}">${room.room} (Exam)</div>`).join('');
            }

            if (unavailable.length > 0) {
                html += `<span style="color:#94a3b8; margin-left:10px;">Occupied: ${unavailable.join(', ')}</span>`;
            }

            if (available.length === 0 && unavailable.length === 0 && examBlocked.length === 0) {
                html = '<span style="color:#94a3b8;">No rooms available for this time</span>';
            }

            suggestions.innerHTML = html;
        }

        async function submitBooking() {
            const room = document.getElementById('bookingRoom').value;
            const date = document.getElementById('bookingDate').value.replace(/-/g, '/');
            const start = document.getElementById('bookingStart').value;
            const end = document.getElementById('bookingEnd').value;
            const title = document.getElementById('bookingTitle').value;
            const teacher = document.getElementById('bookingTeacher').value;
            const isRecurring = document.getElementById('recurringCheck').checked;
            const { selectedWeekdays } = getState();

            if (!room || !date || !start || !end || !title || !teacher) {
                showAlert('Please fill in all required fields', 'error');
                return;
            }

            if (parseTime(start) >= parseTime(end)) {
                showAlert('End time must be after start time', 'error');
                return;
            }

            if (isRoomBlocked(room)) {
                showAlert(`Room ${room} is blocked from booking. Please select another room.`, 'error');
                return;
            }

            const examMsg = getExamProtectionMessage(room, date);
            if (examMsg) {
                showAlert(`${examMsg}. Please select another room or date.`, 'warning');
                return;
            }

            const dayData = await ensureDayDataLoaded(date);
            const daySessions = [
                ...dayData.scheduleData,
                ...dayData.bookingsData.map(booking => ({ date: booking.date, start: booking.start, end: booking.end, room: booking.room }))
            ];

            if (hasRoomTimeConflict(room, date, start, end, [], daySessions)) {
                showAlert(`Room ${room} already has an overlapping session in this time window`, 'error');
                return;
            }

            setState({ pendingBooking: { room, date, start, end, title, teacher, isRecurring, weekdays: [...selectedWeekdays] } });

            let message = `Book ${room} on ${formatDate(date)} from ${start} to ${end}`;
            if (isRecurring) {
                const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                const days = selectedWeekdays.map(day => dayNames[day]).join(', ');
                message += `<br><br>This will be a recurring booking on: ${days || 'No days selected'}`;
            }

            document.getElementById('modalBody').innerHTML = message;
            document.getElementById('confirmModal').classList.add('show');
        }

        async function confirmBooking() {
            const { pendingBooking, activeTab } = getState();
            if (!pendingBooking) return;

            const { room, date, start, end, title, teacher, isRecurring, weekdays } = pendingBooking;
            let createdCount = 0;

            try {
                if (isRecurring && weekdays.length > 0) {
                    const endDateInput = document.getElementById('recurringEnd').value;
                    let currentDate = new Date(date.replace(/\//g, '-'));
                    const lastDate = endDateInput ? new Date(endDateInput) : new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000);

                    const bookings = [];
                    const pendingSessions = [];
                    while (currentDate <= lastDate) {
                        if (weekdays.includes(currentDate.getDay())) {
                            const bookingDate = `${currentDate.getFullYear()}/${String(currentDate.getMonth() + 1).padStart(2, '0')}/${String(currentDate.getDate()).padStart(2, '0')}`;
                            const dayData = await ensureDayDataLoaded(bookingDate);
                            const daySessions = [
                                ...dayData.scheduleData,
                                ...dayData.bookingsData.map(booking => ({ date: booking.date, start: booking.start, end: booking.end, room: booking.room })),
                                ...pendingSessions
                            ];

                            if (!isRoomBlocked(room) && !getExamProtectionMessage(room, bookingDate) && !hasRoomTimeConflict(room, bookingDate, start, end, [], daySessions)) {
                                bookings.push({ room, date: bookingDate, start_time: start, end_time: end, title, teacher });
                                pendingSessions.push({ room, date: bookingDate, start, end });
                            }
                        }
                        currentDate.setDate(currentDate.getDate() + 1);
                    }

                    if (bookings.length === 0) {
                        showAlert('No bookings could be created - all dates are protected or blocked', 'warning');
                        closeModal();
                        return;
                    }

                    for (const booking of bookings) {
                        await createBookingToDb(booking);
                        createdCount++;
                    }
                } else {
                    const dayData = await ensureDayDataLoaded(date);
                    const daySessions = [
                        ...dayData.scheduleData,
                        ...dayData.bookingsData.map(booking => ({ date: booking.date, start: booking.start, end: booking.end, room: booking.room }))
                    ];

                    if (hasRoomTimeConflict(room, date, start, end, [], daySessions)) {
                        throw new Error(`Room ${room} already has an overlapping session at this time`);
                    }

                    await createBookingToDb({ room, date, start_time: start, end_time: end, title, teacher });
                    createdCount = 1;
                }

                closeModal();
                document.getElementById('bookingForm').reset();
                document.querySelectorAll('.weekday-chip').forEach(chip => chip.classList.remove('selected'));
                setState({ selectedWeekdays: [] });

                invalidateCachedData();
                await loadAllData(true);
                if (activeTab === 'bookings') {
                    await renderAllBookings(true);
                }

                const successMsg = createdCount > 1
                    ? `${createdCount} recurring bookings have been confirmed for room ${room}.`
                    : `Room ${room} has been successfully booked for ${formatDate(date)} from ${start} to ${end}.`;
                document.getElementById('successMessage').innerHTML = successMsg;
                document.getElementById('successModal').classList.add('show');
            } catch (error) {
                showAlert('Booking failed: ' + error.message, 'error');
            }
        }

        function closeSuccessModal() {
            document.getElementById('successModal').classList.remove('show');
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.querySelector('.tab[data-tab="bookings"]').classList.add('active');
            document.getElementById('bookings-tab').classList.add('active');
            setState({ activeTab: 'bookings' });
            renderAllBookings();
        }

        async function deleteBooking(id) {
            if (confirm('Are you sure you want to delete this booking?')) {
                const response = await fetch(supabaseUrl + '/rest/v1/bookings?id=eq.' + id, {
                    method: 'DELETE',
                    headers: getRequestHeaders()
                });

                if (!response.ok) {
                    showAlert('Failed to delete', 'error');
                    return;
                }

                showAlert('Booking deleted', 'success');
                invalidateCachedData();
                await refreshActiveTabData(true);
            }
        }

        async function renderAllBookings(force = false) {
            const list = document.getElementById('bookingsList');
            const { selectedBookingDates } = getState();
            renderBookingsDateChips();
            const bookings = await loadBookingsForSelectedDates(force);

            if (selectedBookingDates.size === 0) {
                list.innerHTML = '<p style="color:#64748b;">No dates selected. Add one or click "Today Only".</p>';
                return;
            }

            if (bookings.length === 0) {
                list.innerHTML = '<p style="color:#64748b;">No bookings found for selected date(s).</p>';
                return;
            }

            const groupedBookings = bookings
                .slice()
                .sort((a, b) => a.date.localeCompare(b.date) || a.start.localeCompare(b.start) || a.room.localeCompare(b.room))
                .reduce((groups, booking) => {
                    if (!groups[booking.date]) {
                        groups[booking.date] = [];
                    }
                    groups[booking.date].push(booking);
                    return groups;
                }, {});

            list.innerHTML = Object.entries(groupedBookings)
                .map(([date, dateBookings]) => `
                    <section class="booking-date-group">
                        <div class="booking-date-heading">${formatDate(date)} <span>(${dateBookings.length})</span></div>
                        <div class="booking-date-items">
                            ${dateBookings.map(booking => `
                                <article class="booking-entry">
                                    <div class="booking-entry-header">
                                        <div>
                                            <div class="title">${booking.title}</div>
                                            <div class="time">${booking.start} - ${booking.end}</div>
                                        </div>
                                        <div class="actions">
                                            <span class="room">${booking.room}</span>
                                            <button class="delete-btn" onclick="deleteBooking(${booking.id})">Delete</button>
                                        </div>
                                    </div>
                                    <div class="details">
                                        <span class="detail-item">Booked by: ${booking.teacher}</span>
                                    </div>
                                </article>
                            `).join('')}
                        </div>
                    </section>
                `).join('');
        }

        return {
            initBookingsDateFilter,
            initBookingForm,
            checkRoomAvailability,
            updateRoomSuggestions,
            submitBooking,
            confirmBooking,
            closeSuccessModal,
            deleteBooking,
            renderAllBookings,
            onBookingsDateAdd,
            onBookingsDatePick,
            onBookingsDateTodayOnly,
            onBookingsDateClear,
            removeBookingsFilterDate
        };
    }
};
