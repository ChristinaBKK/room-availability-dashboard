// Booking persistence and overlap validation helpers.
window.AppBookingDb = {
    createBookingDb({
        supabaseUrl,
        supabaseAnonKey,
        getDateVariants,
        normalizeDateFormat,
        normalizeRoom,
        parseTime
    }) {
        async function createBookingToDb(booking) {
            const bookingDate = normalizeDateFormat(booking.date || '');
            const bookingRoom = normalizeRoom(booking.room || '');
            const bookingStart = booking.start_time;
            const bookingEnd = booking.end_time;

            if (!bookingRoom || !bookingDate || !bookingStart || !bookingEnd) {
                throw new Error('Booking data is incomplete');
            }

            const dateVariants = getDateVariants(bookingDate);
            const orFilter = dateVariants.map(date => `date.eq.${date}`).join(',');

            const [roomSessionsResp, scheduleResp, bookingsResp] = await Promise.all([
                fetch(
                    supabaseUrl + '/rest/v1/room_sessions?select=date,start_time,end_time,room&room=eq.' + encodeURIComponent(bookingRoom) + '&or=(' + encodeURIComponent(orFilter) + ')',
                    {
                        headers: {
                            apikey: supabaseAnonKey,
                            Authorization: 'Bearer ' + supabaseAnonKey
                        }
                    }
                ),
                fetch(
                    supabaseUrl + '/rest/v1/schedule?select=date,start_time,end_time,room&room=eq.' + encodeURIComponent(bookingRoom) + '&or=(' + encodeURIComponent(orFilter) + ')',
                    {
                        headers: {
                            apikey: supabaseAnonKey,
                            Authorization: 'Bearer ' + supabaseAnonKey
                        }
                    }
                ),
                fetch(
                    supabaseUrl + '/rest/v1/bookings?select=date,start_time,end_time,room&room=eq.' + encodeURIComponent(bookingRoom) + '&or=(' + encodeURIComponent(orFilter) + ')',
                    {
                        headers: {
                            apikey: supabaseAnonKey,
                            Authorization: 'Bearer ' + supabaseAnonKey
                        }
                    }
                )
            ]);

            const roomSessionRows = roomSessionsResp.ok ? await roomSessionsResp.json() : [];
            const scheduleRows = scheduleResp.ok ? await scheduleResp.json() : [];
            const bookingRows = bookingsResp.ok ? await bookingsResp.json() : [];
            const pool = [
                ...(Array.isArray(roomSessionRows) ? roomSessionRows : []).map(row => ({ date: row.date, start: row.start_time, end: row.end_time, room: row.room })),
                ...(Array.isArray(scheduleRows) ? scheduleRows : []).map(row => ({ date: row.date, start: row.start_time, end: row.end_time, room: row.room })),
                ...(Array.isArray(bookingRows) ? bookingRows : []).map(row => ({ date: row.date, start: row.start_time, end: row.end_time, room: row.room }))
            ];

            const bookingStartMinutes = parseTime(bookingStart);
            const bookingEndMinutes = parseTime(bookingEnd);
            const clash = pool.find(session =>
                normalizeRoom(session.room || '') === bookingRoom &&
                normalizeDateFormat(session.date || '') === bookingDate &&
                bookingStartMinutes < parseTime(session.end) &&
                bookingEndMinutes > parseTime(session.start)
            );

            if (clash) {
                throw new Error(`Room ${bookingRoom} is already booked at ${clash.start}-${clash.end}`);
            }

            const response = await fetch(supabaseUrl + '/rest/v1/bookings', {
                method: 'POST',
                headers: {
                    apikey: supabaseAnonKey,
                    Authorization: 'Bearer ' + supabaseAnonKey,
                    'Content-Type': 'application/json',
                    Prefer: 'return=representation'
                },
                body: JSON.stringify(booking)
            });

            const responseText = await response.text();

            if (!response.ok) {
                let errorMsg = 'Failed to create booking';
                try {
                    const err = JSON.parse(responseText);
                    errorMsg = err.message || err.details || JSON.stringify(err);
                } catch (error) {
                    if (responseText) errorMsg = responseText;
                }
                throw new Error(errorMsg);
            }

            try {
                return JSON.parse(responseText);
            } catch (error) {
                return responseText;
            }
        }

        return {
            createBookingToDb
        };
    }
};
