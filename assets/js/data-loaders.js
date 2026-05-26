// Stateful data loaders built on top of low-level data access helpers.
window.AppDataLoaders = {
    createDataLoaders({
        supabaseUrl,
        fetchAllRows,
        fetchRowsForDate,
        mapScheduleRows,
        mapBookingRows,
        getRequestHeaders,
        normalizeDateFormat,
        getSortedSelectedBookingDates,
        updateBookingsBadge,
        getState,
        setState
    }) {
        function getProtectionDatesByRoom() {
            const protectionDates = new Map();
            const { examDates } = getState();

            for (const [room, dates] of examDates) {
                if (!protectionDates.has(room)) {
                    protectionDates.set(room, new Set());
                }

                for (const dateStr of dates) {
                    const [year, month, day] = dateStr.split('/').map(Number);
                    const examDate = new Date(year, month - 1, day);
                    examDate.setDate(examDate.getDate() - 1);
                    const prevDate = `${examDate.getFullYear()}/${String(examDate.getMonth() + 1).padStart(2, '0')}/${String(examDate.getDate()).padStart(2, '0')}`;
                    protectionDates.get(room).add(prevDate);
                }
            }

            return protectionDates;
        }

        function rebuildRoomInventoryFromCaches() {
            const { dayDataCache, allExamSessions, allBookingsListData } = getState();
            const allRooms = new Set();

            for (const cachedDay of dayDataCache.values()) {
                cachedDay.scheduleData.forEach(session => allRooms.add(session.room));
                cachedDay.bookingsData.forEach(booking => allRooms.add(booking.room));
            }
            allExamSessions.forEach(session => allRooms.add(session.room));
            allBookingsListData.forEach(booking => allRooms.add(booking.room));

            setState({ allRooms });
        }

        async function loadExamMetadata(force = false) {
            const { allExamSessions } = getState();
            if (allExamSessions.length > 0 && !force) {
                return;
            }

            const examRows = await fetchAllRows(
                supabaseUrl + '/rest/v1/schedule?select=' + encodeURIComponent('date,start_time,end_time,class_name,room,teacher') + '&teacher=eq.EXAM&order=date,room,start_time'
            );

            const nextExamSessions = mapScheduleRows(examRows);
            const examRooms = new Set();
            const examDates = new Map();

            nextExamSessions.forEach(session => {
                const room = session.room;
                examRooms.add(room);
                if (!examDates.has(room)) {
                    examDates.set(room, new Set());
                }
                examDates.get(room).add(normalizeDateFormat(session.date));
            });

            setState({
                allExamSessions: nextExamSessions,
                examRooms,
                examDates
            });
        }

        async function ensureDayDataLoaded(dateStr, force = false) {
            const normalizedDate = normalizeDateFormat(dateStr);
            if (!normalizedDate) {
                return { scheduleData: [], bookingsData: [] };
            }

            const { dayDataCache } = getState();
            if (!force && dayDataCache.has(normalizedDate)) {
                return dayDataCache.get(normalizedDate);
            }

            await loadExamMetadata();

            const [roomSessionRows, scheduleRows, bookingRows] = await Promise.all([
                fetchRowsForDate('room_sessions', '*', normalizedDate, '&order=' + encodeURIComponent('room,start_time')),
                fetchRowsForDate('schedule', '*', normalizedDate, '&order=' + encodeURIComponent('room,start_time')),
                fetchRowsForDate('bookings', '*', normalizedDate, '&order=' + encodeURIComponent('start_time,room'))
            ]);

            const protectionDates = getProtectionDatesByRoom();
            const seen = new Set();
            const scheduleData = mapScheduleRows([...roomSessionRows, ...scheduleRows])
                .map(session => ({
                    ...session,
                    isExamProtection: !session.isExam && protectionDates.has(session.room) && protectionDates.get(session.room).has(normalizeDateFormat(session.date))
                }))
                .filter(session => {
                    const key = `${session.room}|${normalizeDateFormat(session.date)}|${session.start}|${session.end}|${session.component}`;
                    if (seen.has(key)) return false;
                    seen.add(key);
                    return true;
                });

            const bookingsData = mapBookingRows(bookingRows);
            const cached = { scheduleData, bookingsData };
            dayDataCache.set(normalizedDate, cached);
            rebuildRoomInventoryFromCaches();
            return cached;
        }

        async function loadBookingCount(force = false) {
            const { bookingCount } = getState();
            if (bookingCount > 0 && !force) {
                return bookingCount;
            }

            const response = await fetch(supabaseUrl + '/rest/v1/bookings?select=id', {
                method: 'HEAD',
                headers: getRequestHeaders({ Prefer: 'count=exact' })
            });

            if (!response.ok) {
                setState({ bookingCount: 0 });
                updateBookingsBadge();
                return 0;
            }

            const contentRange = response.headers.get('content-range') || '0/0';
            const [, total = '0'] = contentRange.split('/');
            const nextBookingCount = Number.parseInt(total, 10) || 0;
            setState({ bookingCount: nextBookingCount });
            updateBookingsBadge();
            return nextBookingCount;
        }

        async function loadBookingsList(force = false) {
            const { bookingsListLoaded, allBookingsListData } = getState();
            if (bookingsListLoaded && !force) {
                return allBookingsListData;
            }

            const bookingRows = await fetchAllRows(
                supabaseUrl + '/rest/v1/bookings?select=' + encodeURIComponent('*') + '&order=' + encodeURIComponent('date.desc,start_time.asc,room.asc')
            );

            const nextBookingsListData = mapBookingRows(bookingRows);
            setState({
                allBookingsListData: nextBookingsListData,
                bookingsListLoaded: true,
                bookingCount: nextBookingsListData.length
            });
            rebuildRoomInventoryFromCaches();
            updateBookingsBadge();
            return nextBookingsListData;
        }

        async function loadBookingsForSelectedDates() {
            const selectedDates = getSortedSelectedBookingDates();
            if (selectedDates.length === 0) {
                return [];
            }

            const results = await Promise.all(
                selectedDates.map(date => fetchRowsForDate('bookings', '*', date, '&order=' + encodeURIComponent('start_time,room')))
            );

            const merged = mapBookingRows(results.flat());
            const seenIds = new Set();
            return merged
                .filter(booking => {
                    if (booking.id == null) return true;
                    if (seenIds.has(booking.id)) return false;
                    seenIds.add(booking.id);
                    return true;
                })
                .sort((a, b) => b.date.localeCompare(a.date) || a.start.localeCompare(b.start) || a.room.localeCompare(b.room));
        }

        function invalidateCachedData() {
            const { dayDataCache } = getState();
            dayDataCache.clear();
            setState({
                allBookingsListData: [],
                bookingsListLoaded: false,
                bookingCount: 0
            });
        }

        return {
            loadExamMetadata,
            ensureDayDataLoaded,
            loadBookingCount,
            loadBookingsList,
            loadBookingsForSelectedDates,
            invalidateCachedData
        };
    }
};
