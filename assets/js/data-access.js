// Supabase request and row-mapping helpers.
window.AppDataAccess = {
    createDataAccess({
        supabaseUrl,
        supabaseAnonKey,
        getDateVariants,
        normalizeDateFormat,
        normalizeRoom
    }) {
        function getRequestHeaders(extra = {}) {
            return {
                apikey: supabaseAnonKey,
                Authorization: 'Bearer ' + supabaseAnonKey,
                ...extra
            };
        }

        function buildDateOrFilter(dateStr) {
            return getDateVariants(normalizeDateFormat(dateStr))
                .map(date => `date.eq.${date}`)
                .join(',');
        }

        async function fetchAllRows(url) {
            const rows = [];
            let offset = 0;
            const limit = 1000;

            while (true) {
                const separator = url.includes('?') ? '&' : '?';
                const response = await fetch(`${url}${separator}offset=${offset}&limit=${limit}`, {
                    headers: getRequestHeaders()
                });

                if (!response.ok) break;

                const batch = await response.json();
                if (!Array.isArray(batch) || batch.length === 0) break;
                rows.push(...batch);

                if (batch.length < limit) break;
                offset += limit;
            }

            return rows;
        }

        async function fetchRowsForDate(tableName, selectClause, dateStr, orderClause = '') {
            const orFilter = buildDateOrFilter(dateStr);
            const response = await fetch(
                supabaseUrl + '/rest/v1/' + tableName + '?select=' + encodeURIComponent(selectClause) + '&or=(' + encodeURIComponent(orFilter) + ')' + orderClause,
                { headers: getRequestHeaders() }
            );

            if (!response.ok) {
                return [];
            }

            const rows = await response.json();
            return Array.isArray(rows) ? rows : [];
        }

        function mapScheduleRows(rows) {
            return rows.map(item => {
                let component = item.class_name || item.Class || item.title || '';
                const teacherVal = item.teacher || item.Teacher || '';
                const isExamFromSchedule = teacherVal.toUpperCase() === 'EXAM';

                if (isExamFromSchedule && component.toUpperCase().startsWith('EXAM:')) {
                    component = component.substring(5).trim();
                }

                return {
                    date: item.date || item.Date || '',
                    start: item.start_time || item['Start Time'] || '',
                    end: item.end_time || item['End Time'] || '',
                    component,
                    room: normalizeRoom(item.room || item.Room || ''),
                    teacher: isExamFromSchedule ? '' : teacherVal,
                    isExam: isExamFromSchedule,
                    isExamProtection: false
                };
            }).filter(item => item.date && item.room);
        }

        function mapBookingRows(rows) {
            return rows.map(item => ({
                id: item.id,
                date: item.date || '',
                start: item.start_time || '',
                end: item.end_time || '',
                room: normalizeRoom(item.room || ''),
                teacher: item.teacher || '',
                title: item.title || ''
            })).filter(item => item.date && item.room);
        }

        return {
            getRequestHeaders,
            buildDateOrFilter,
            fetchAllRows,
            fetchRowsForDate,
            mapScheduleRows,
            mapBookingRows
        };
    }
};
