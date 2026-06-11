        const {
            SUPABASE_URL,
            SUPABASE_ANON_KEY,
            BLOCKED_ROOMS,
            KNOWN_B_ROOMS,
            ROOM_ALIASES
        } = window.AppConfig;
        const { SETUP_SQL } = window.AppSetup;
        const { createCommonUi } = window.AppCommonUi;
        const { createRoomExamUtils } = window.AppRoomExamUtils;
        const { createDataAccess } = window.AppDataAccess;
        const { createDataLoaders } = window.AppDataLoaders;
        const { createBookingsUi } = window.AppBookingsUi;
        const { createBookingsImportExport } = window.AppBookingsImportExport;
        const { createBookingDb } = window.AppBookingDb;
        const { createScheduleUi } = window.AppScheduleUi;
        const { createRoomViewUi } = window.AppRoomViewUi;
        const { createAppOrchestrator } = window.AppOrchestrator;
        const {
            updateBookingsBadge,
            closeModal,
            initScrollTopButton,
            showAlert
        } = createCommonUi({
            getState: () => ({
                bookingCount,
                pendingBooking
            }),
            setState: updates => {
                if (Object.prototype.hasOwnProperty.call(updates, 'pendingBooking')) pendingBooking = updates.pendingBooking;
            }
        });
        function exposeGlobals(bindings) {
            Object.assign(window, bindings);
        }
        const {
            normalizeRoom,
            isBRoom,
            getBRoomInventory,
            isRoomBlocked,
            hasExamOnDate,
            getProtectedDates,
            isBookingAllowed,
            getExamProtectionMessage,
            getExamDetailsForRoom
        } = createRoomExamUtils({
            blockedRooms: BLOCKED_ROOMS,
            knownBRooms: KNOWN_B_ROOMS,
            roomAliases: ROOM_ALIASES,
            formatDate,
            normalizeDateFormat,
            getAllRooms: () => allRooms,
            getExamDates: () => examDates,
            getAllExamSessions: () => allExamSessions
        });
        const {
            getRequestHeaders,
            fetchAllRows,
            fetchRowsForDate,
            mapScheduleRows,
            mapBookingRows
        } = createDataAccess({
            supabaseUrl: SUPABASE_URL,
            supabaseAnonKey: SUPABASE_ANON_KEY,
            getDateVariants,
            normalizeDateFormat,
            normalizeRoom
        });
        const {
            loadExamMetadata,
            ensureDayDataLoaded,
            loadBookingCount,
            loadBookingsList,
            loadBookingsForSelectedDates,
            invalidateCachedData
        } = createDataLoaders({
            supabaseUrl: SUPABASE_URL,
            fetchAllRows,
            fetchRowsForDate,
            mapScheduleRows,
            mapBookingRows,
            getRequestHeaders,
            normalizeDateFormat,
            getSortedSelectedBookingDates,
            updateBookingsBadge,
            getState: () => ({
                allExamSessions,
                examRooms,
                examDates,
                allRooms,
                bookingCount,
                dayDataCache,
                bookingsListLoaded,
                allBookingsListData
            }),
            setState: updates => {
                if (Object.prototype.hasOwnProperty.call(updates, 'allExamSessions')) allExamSessions = updates.allExamSessions;
                if (Object.prototype.hasOwnProperty.call(updates, 'examRooms')) examRooms = updates.examRooms;
                if (Object.prototype.hasOwnProperty.call(updates, 'examDates')) examDates = updates.examDates;
                if (Object.prototype.hasOwnProperty.call(updates, 'allRooms')) allRooms = updates.allRooms;
                if (Object.prototype.hasOwnProperty.call(updates, 'bookingCount')) bookingCount = updates.bookingCount;
                if (Object.prototype.hasOwnProperty.call(updates, 'bookingsListLoaded')) bookingsListLoaded = updates.bookingsListLoaded;
                if (Object.prototype.hasOwnProperty.call(updates, 'allBookingsListData')) allBookingsListData = updates.allBookingsListData;
            }
        });
        const { createBookingToDb } = createBookingDb({
            supabaseUrl: SUPABASE_URL,
            supabaseAnonKey: SUPABASE_ANON_KEY,
            getDateVariants,
            normalizeDateFormat,
            normalizeRoom,
            parseTime
        });
        let loadAllData;
        let loadScheduleForDate;
        let refreshActiveTabData;
        const {
            initBookingsDateFilter,
            initBookingForm,
            checkRoomAvailability,
            updateRoomSuggestions,
            confirmBooking,
            closeSuccessModal,
            deleteBooking,
            renderAllBookings,
            onBookingsDateAdd,
            onBookingsDatePick,
            onBookingsDateTodayOnly,
            onBookingsDateClear,
            removeBookingsFilterDate
        } = createBookingsUi({
            supabaseUrl: SUPABASE_URL,
            formatDate,
            normalizeDateFormat,
            displayDateToInputValue,
            getTodayDisplayDate,
            parseTime,
            getRequestHeaders,
            getSortedSelectedBookingDates,
            getBRoomInventory,
            isRoomBlocked,
            getExamProtectionMessage,
            ensureDayDataLoaded,
            loadBookingsForSelectedDates,
            invalidateCachedData,
            refreshActiveTabData: (...args) => refreshActiveTabData(...args),
            loadAllData: (...args) => loadAllData(...args),
            hasRoomTimeConflict,
            createBookingToDb,
            showAlert,
            closeModal,
            getState: () => ({
                selectedBookingDates,
                bookingsAddMode,
                selectedWeekdays,
                pendingBooking,
                activeTab
            }),
            setState: updates => {
                if (Object.prototype.hasOwnProperty.call(updates, 'selectedBookingDates')) selectedBookingDates = updates.selectedBookingDates;
                if (Object.prototype.hasOwnProperty.call(updates, 'bookingsAddMode')) bookingsAddMode = updates.bookingsAddMode;
                if (Object.prototype.hasOwnProperty.call(updates, 'selectedWeekdays')) selectedWeekdays = updates.selectedWeekdays;
                if (Object.prototype.hasOwnProperty.call(updates, 'pendingBooking')) pendingBooking = updates.pendingBooking;
                if (Object.prototype.hasOwnProperty.call(updates, 'activeTab')) activeTab = updates.activeTab;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewStartDate')) roomViewStartDate = updates.roomViewStartDate;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewEndDate')) roomViewEndDate = updates.roomViewEndDate;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewSelectedRooms')) roomViewSelectedRooms = updates.roomViewSelectedRooms;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewInitialized')) roomViewInitialized = updates.roomViewInitialized;
            }
        });
        const { exportBookings, importBookings } = createBookingsImportExport({
            loadBookingsList,
            showAlert,
            normalizeRoom,
            isRoomBlocked,
            parseTime,
            normalizeDateFormat,
            createBookingToDb,
            invalidateCachedData,
            loadAllData,
            getState: () => ({
                allScheduleData,
                allBookingsData
            })
        });
        window.exportBookings = exportBookings;
        window.importBookings = importBookings;
        const {
            initScheduleUi,
            getSelectedDate,
            updateExamRoomsDisplay,
            populateFilters,
            onScheduleDateChange,
            updateDashboard
        } = createScheduleUi({
            formatDate,
            normalizeDateFormat,
            getTodayInputDate,
            getBRoomInventory,
            isRoomBlocked,
            parseTime,
            getExamDetailsForRoom,
            loadScheduleForDate: (...args) => loadScheduleForDate(...args),
            getState: () => ({
                examRooms,
                filtersInitialized,
                selectedRooms,
                examDates,
                allScheduleData,
                allBookingsData
            }),
            setState: updates => {
                if (Object.prototype.hasOwnProperty.call(updates, 'filtersInitialized')) filtersInitialized = updates.filtersInitialized;
                if (Object.prototype.hasOwnProperty.call(updates, 'selectedRooms')) selectedRooms = updates.selectedRooms;
            }
        });
        const {
            initRoomViewUi,
            loadRoomViewRange
        } = createRoomViewUi({
            formatDate,
            normalizeDateFormat,
            getTodayInputDate,
            getBRoomInventory,
            isRoomBlocked,
            parseTime,
            ensureDayDataLoaded,
            getState: () => ({
                roomViewStartDate,
                roomViewEndDate,
                roomViewSelectedRooms,
                roomViewInitialized,
                dayDataCache
            }),
            setState: updates => {
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewStartDate')) roomViewStartDate = updates.roomViewStartDate;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewEndDate')) roomViewEndDate = updates.roomViewEndDate;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewSelectedRooms')) roomViewSelectedRooms = updates.roomViewSelectedRooms;
                if (Object.prototype.hasOwnProperty.call(updates, 'roomViewInitialized')) roomViewInitialized = updates.roomViewInitialized;
            }
        });
        const orchestrator = createAppOrchestrator({
            supabaseUrl: SUPABASE_URL,
            supabaseAnonKey: SUPABASE_ANON_KEY,
            getTodayDisplayDate,
            normalizeDateFormat,
            loadExamMetadata,
            loadBookingCount,
            ensureDayDataLoaded,
            getSelectedDate,
            populateFilters,
            updateDashboard,
            loadRoomViewRange: (...args) => loadRoomViewRange(...args),
            renderAllBookings,
            getState: () => ({
                autoRefreshInterval,
                activeTab
            }),
            setState: updates => {
                if (Object.prototype.hasOwnProperty.call(updates, 'autoRefreshInterval')) autoRefreshInterval = updates.autoRefreshInterval;
                if (Object.prototype.hasOwnProperty.call(updates, 'allScheduleData')) allScheduleData = updates.allScheduleData;
                if (Object.prototype.hasOwnProperty.call(updates, 'allBookingsData')) allBookingsData = updates.allBookingsData;
            }
        });
        ({
            initAutoRefresh,
            checkConnection,
            loadAllData,
            loadScheduleForDate,
            refreshActiveTabData
        } = orchestrator);
        exposeGlobals({
            closeModal,
            onBookingsDateAdd,
            onBookingsDatePick,
            onBookingsDateTodayOnly,
            onBookingsDateClear,
            removeBookingsFilterDate,
            checkRoomAvailability,
            confirmBooking,
            closeSuccessModal,
            deleteBooking,
            exportBookings,
            importBookings,
            onScheduleDateChange
        });

        // Initialize
        initApp();
        
        function initApp() {
            document.getElementById('setupSQL').textContent = SETUP_SQL;
            initScheduleUi();
            initRoomViewUi();
            initTabs();
            initBookingForm();
            initBookingsDateFilter();
            initScrollTopButton();
            initAutoRefresh();
            checkConnection();
        }
        
        function initTabs() {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    this.classList.add('active');
                    document.getElementById(this.dataset.tab + '-tab').classList.add('active');
                    activeTab = this.dataset.tab;
                    if (this.dataset.tab === 'room-view') loadRoomViewRange();
                    if (this.dataset.tab === 'bookings') renderAllBookings();
                    if (this.dataset.tab === 'info') updateExamRoomsDisplay();
                });
            });
            updateBookingsBadge();
        }
        
        function getSortedSelectedBookingDates() {
            return [...selectedBookingDates].sort((a, b) => b.localeCompare(a));
        }

        function hasRoomTimeConflict(room, date, start, end, extraSessions = [], baseSessions = null) {
            const normalizedRoom = normalizeRoom(room || '');
            const normalizedDate = normalizeDateFormat(date || '');
            if (!normalizedRoom || !normalizedDate || !start || !end) return false;

            const candidateStart = parseTime(start);
            const candidateEnd = parseTime(end);
            const allSessions = baseSessions || [
                ...allScheduleData,
                ...allBookingsData.map(b => ({ date: b.date, start: b.start, end: b.end, room: b.room })),
                ...extraSessions
            ];

            return allSessions.some(s =>
                normalizeRoom(s.room || '') === normalizedRoom &&
                normalizeDateFormat(s.date || '') === normalizedDate &&
                candidateStart < parseTime(s.end) &&
                candidateEnd > parseTime(s.start)
            );
        }
        
