// Connection, loading, and refresh orchestration.
window.AppOrchestrator = {
    createAppOrchestrator({
        supabaseUrl,
        supabaseAnonKey,
        getTodayDisplayDate,
        normalizeDateFormat,
        loadExamMetadata,
        loadBookingCount,
        ensureDayDataLoaded,
        getSelectedDate,
        populateFilters,
        updateDashboard,
        renderAllBookings,
        getState,
        setState
    }) {
        function setStatus(dotClassName, text) {
            document.getElementById('statusDot').className = dotClassName;
            document.getElementById('statusText').textContent = text;
        }

        function updateLastUpdated() {
            document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
        }

        function startAutoRefresh() {
            const { autoRefreshInterval } = getState();
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            const nextInterval = setInterval(() => {
                if (!document.hidden) refreshActiveTabData(true);
            }, 30000);
            setState({ autoRefreshInterval: nextInterval });
        }

        function stopAutoRefresh() {
            const { autoRefreshInterval } = getState();
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                setState({ autoRefreshInterval: null });
            }
        }

        function initAutoRefresh() {
            const toggle = document.getElementById('autoRefreshToggle');
            toggle.addEventListener('change', function() {
                if (this.checked) {
                    startAutoRefresh();
                } else {
                    stopAutoRefresh();
                }
            });
            if (toggle.checked) {
                startAutoRefresh();
            }
        }

        async function testTableConnection(tableName) {
            try {
                const testUrl = supabaseUrl + '/rest/v1/' + tableName + '?select=id&limit=1';
                const response = await fetch(testUrl, {
                    method: 'GET',
                    mode: 'cors',
                    headers: {
                        apikey: supabaseAnonKey,
                        Authorization: 'Bearer ' + supabaseAnonKey,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    console.log(tableName + ' table accessible');
                    return true;
                }
                return false;
            } catch (error) {
                console.log(tableName + ' connection failed:', error);
                return false;
            }
        }

        async function checkConnection() {
            setStatus('status-dot loading', 'Loading data...');

            let connected = await testTableConnection('room_sessions');
            if (!connected) {
                connected = await testTableConnection('schedule');
            }

            if (connected) {
                setStatus('status-dot', 'Connected to database');
                document.getElementById('setupSection').style.display = 'none';
                loadAllData();
                return;
            }

            setStatus('status-dot error', 'Database connection failed');
            document.getElementById('setupSection').style.display = 'block';
        }

        async function loadAllData(force = false) {
            setStatus('status-dot loading', 'Loading data...');

            try {
                await loadExamMetadata(force);
                await loadBookingCount(force);
                await loadScheduleForDate(getSelectedDate() || getTodayDisplayDate(), force);
                setStatus('status-dot', 'Data loaded');
            } catch (error) {
                console.error('Load error:', error);
                setStatus('status-dot error', 'Failed to load data');
                document.getElementById('setupSection').style.display = 'block';
            }
        }

        async function loadScheduleForDate(dateStr, force = false) {
            const normalizedDate = normalizeDateFormat(dateStr || getTodayDisplayDate());
            const dayData = await ensureDayDataLoaded(normalizedDate, force);
            setState({
                allScheduleData: dayData.scheduleData,
                allBookingsData: dayData.bookingsData
            });
            populateFilters();
            updateDashboard();
            updateLastUpdated();
        }

        async function refreshActiveTabData(force = false) {
            const { activeTab } = getState();
            if (activeTab === 'bookings') {
                await loadBookingCount(force);
                await renderAllBookings(force);
                setStatus('status-dot', 'Bookings refreshed');
                updateLastUpdated();
                return;
            }

            await loadAllData(force);
        }

        return {
            initAutoRefresh,
            checkConnection,
            loadAllData,
            loadScheduleForDate,
            refreshActiveTabData
        };
    }
};
