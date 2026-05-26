// Booking import/export workflows.
window.AppBookingsImportExport = {
    createBookingsImportExport({
        loadBookingsList,
        showAlert,
        normalizeRoom,
        isRoomBlocked,
        parseTime,
        normalizeDateFormat,
        createBookingToDb,
        invalidateCachedData,
        loadAllData,
        getState
    }) {
        async function exportBookings() {
            const bookings = await loadBookingsList();

            if (bookings.length === 0) {
                showAlert('No bookings to export', 'error');
                return;
            }

            const data = JSON.stringify(bookings, null, 2);
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `room_bookings_${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            URL.revokeObjectURL(url);
            showAlert('Bookings exported successfully!', 'success');
        }

        function importBookings(event) {
            const file = event.target.files[0];
            if (!file) return;

            const ext = file.name.split('.').pop().toLowerCase();
            event.target.value = '';

            if (ext === 'json') {
                const reader = new FileReader();
                reader.onload = async function(loadEvent) {
                    try {
                        const imported = JSON.parse(loadEvent.target.result);
                        if (!Array.isArray(imported)) throw new Error('Invalid format - file must contain a JSON array');
                        await processImportedBookings(imported);
                    } catch (error) {
                        showAlert('Failed to import: ' + error.message, 'error');
                    }
                };
                reader.readAsText(file);
                return;
            }

            if (ext === 'xlsx' || ext === 'xls' || ext === 'csv') {
                if (typeof XLSX === 'undefined') {
                    showAlert('Excel parser not loaded yet - please wait a moment and try again', 'error');
                    return;
                }

                const reader = new FileReader();
                reader.onload = async function(loadEvent) {
                    try {
                        const data = new Uint8Array(loadEvent.target.result);
                        const workbook = XLSX.read(data, { type: 'array', cellDates: true });
                        const sheet = workbook.Sheets[workbook.SheetNames[0]];
                        const rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });

                        const imported = rows.map(row => {
                            const normalizedRow = {};
                            for (const key of Object.keys(row)) {
                                normalizedRow[key.toLowerCase().trim().replace(/\s+/g, '_')] = row[key];
                            }

                            let date = normalizedRow.date || '';
                            if (date instanceof Date) {
                                date = `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
                            } else {
                                date = String(date).trim().replace(/-/g, '/');
                            }

                            const toTime = value => {
                                if (value instanceof Date) {
                                    return `${String(value.getHours()).padStart(2, '0')}:${String(value.getMinutes()).padStart(2, '0')}`;
                                }
                                return String(value || '').trim();
                            };

                            return {
                                room: String(normalizedRow.room || '').trim(),
                                date,
                                start: toTime(normalizedRow.start || normalizedRow.start_time || ''),
                                end: toTime(normalizedRow.end || normalizedRow.end_time || ''),
                                title: String(normalizedRow.title || normalizedRow.booking_title || '').trim(),
                                teacher: String(normalizedRow.teacher || normalizedRow.your_name || normalizedRow.name || '').trim()
                            };
                        });

                        await processImportedBookings(imported);
                    } catch (error) {
                        showAlert('Failed to import: ' + error.message, 'error');
                    }
                };
                reader.readAsArrayBuffer(file);
                return;
            }

            showAlert('Unsupported file type. Please use .json, .xlsx, .xls, or .csv', 'error');
        }

        async function processImportedBookings(imported) {
            if (!Array.isArray(imported) || imported.length === 0) {
                showAlert('No rows found in file.', 'error');
                return;
            }

            const succeeded = [];
            const failed = [];
            const { allScheduleData, allBookingsData } = getState();
            const sessionPool = [
                ...allScheduleData.map(session => ({ room: session.room, date: normalizeDateFormat(session.date), start: session.start, end: session.end })),
                ...allBookingsData.map(booking => ({ room: booking.room, date: normalizeDateFormat(booking.date), start: booking.start, end: booking.end }))
            ];

            for (let index = 0; index < imported.length; index++) {
                const booking = imported[index];
                const row = index + 2;
                const reasons = [];

                if (!booking.room || !String(booking.room).trim()) reasons.push('missing <strong>room</strong>');
                if (!booking.date || !String(booking.date).trim()) reasons.push('missing <strong>date</strong>');
                if (!booking.start || !String(booking.start).trim()) reasons.push('missing <strong>start</strong> time');
                if (!booking.end || !String(booking.end).trim()) reasons.push('missing <strong>end</strong> time');
                if (!booking.title || !String(booking.title).trim()) reasons.push('missing <strong>title</strong>');
                if (!booking.teacher || !String(booking.teacher).trim()) reasons.push('missing <strong>teacher</strong>');

                const normalizedRoom = normalizeRoom(booking.room || '');
                if (booking.room && isRoomBlocked(normalizedRoom)) {
                    reasons.push(`room <strong>${normalizedRoom}</strong> is blocked from booking`);
                }

                if (booking.start && booking.end && parseTime(String(booking.start)) >= parseTime(String(booking.end))) {
                    reasons.push('start time is not before end time');
                }

                if (reasons.length === 0 && booking.room && booking.date && booking.start && booking.end) {
                    const bookingDate = normalizeDateFormat(String(booking.date));
                    const bookingStart = parseTime(String(booking.start));
                    const bookingEnd = parseTime(String(booking.end));
                    const clash = sessionPool.find(session =>
                        session.room === normalizedRoom &&
                        normalizeDateFormat(session.date) === bookingDate &&
                        bookingStart < parseTime(session.end) &&
                        bookingEnd > parseTime(session.start)
                    );

                    if (clash) {
                        reasons.push(`room <strong>${normalizedRoom}</strong> already has a booking or class on ${bookingDate} at ${clash.start}–${clash.end}`);
                    }
                }

                if (reasons.length > 0) {
                    failed.push({ row, data: booking, reasons });
                    continue;
                }

                const record = {
                    room: normalizedRoom,
                    date: booking.date,
                    start_time: booking.start,
                    end_time: booking.end,
                    title: String(booking.title).trim(),
                    teacher: String(booking.teacher).trim()
                };

                try {
                    await createBookingToDb(record);
                    succeeded.push({ row, record });
                    sessionPool.push({ room: normalizedRoom, date: normalizeDateFormat(booking.date), start: booking.start, end: booking.end });
                } catch (error) {
                    failed.push({ row, data: booking, reasons: [error.message || 'Database error'] });
                }
            }

            if (succeeded.length > 0) {
                invalidateCachedData();
                await loadAllData(true);
            }

            let html = '';
            const total = imported.length;
            const okCol = succeeded.length > 0 ? '#16a34a' : '#64748b';
            const failCol = failed.length > 0 ? '#dc2626' : '#64748b';

            html += `<div style="display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;">
                <div style="flex:1;min-width:120px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:12px 16px;text-align:center;">
                    <div style="font-size:28px;font-weight:700;color:${okCol};">${succeeded.length}</div>
                    <div style="font-size:12px;color:#475569;">Imported successfully</div>
                </div>
                <div style="flex:1;min-width:120px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px 16px;text-align:center;">
                    <div style="font-size:28px;font-weight:700;color:${failCol};">${failed.length}</div>
                    <div style="font-size:12px;color:#475569;">Failed / skipped</div>
                </div>
                <div style="flex:1;min-width:120px;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;text-align:center;">
                    <div style="font-size:28px;font-weight:700;color:#334155;">${total}</div>
                    <div style="font-size:12px;color:#475569;">Total rows</div>
                </div>
            </div>`;

            if (failed.length > 0) {
                html += `<div style="font-weight:600;color:#dc2626;margin-bottom:8px;">&#9888; Failed rows</div>`;
                html += `<table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px;">
                    <thead><tr>
                        <th style="background:#fef2f2;padding:7px 10px;text-align:left;border-bottom:1px solid #fecaca;color:#64748b;width:55px;">Row</th>
                        <th style="background:#fef2f2;padding:7px 10px;text-align:left;border-bottom:1px solid #fecaca;color:#64748b;width:90px;">Room</th>
                        <th style="background:#fef2f2;padding:7px 10px;text-align:left;border-bottom:1px solid #fecaca;color:#64748b;width:100px;">Date</th>
                        <th style="background:#fef2f2;padding:7px 10px;text-align:left;border-bottom:1px solid #fecaca;color:#64748b;">Reason(s)</th>
                    </tr></thead><tbody>`;
                failed.forEach(failedRow => {
                    html += `<tr>
                        <td style="padding:7px 10px;border-bottom:1px solid #fef2f2;color:#64748b;">${failedRow.row}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #fef2f2;">${failedRow.data.room || '<em style="color:#94a3b8">—</em>'}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #fef2f2;">${failedRow.data.date || '<em style="color:#94a3b8">—</em>'}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #fef2f2;color:#dc2626;">${failedRow.reasons.join('; ')}</td>
                    </tr>`;
                });
                html += '</tbody></table>';
            }

            if (succeeded.length > 0) {
                html += `<div style="font-weight:600;color:#16a34a;margin-bottom:8px;">&#10003; Successfully imported</div>`;
                html += `<table style="width:100%;border-collapse:collapse;font-size:13px;">
                    <thead><tr>
                        <th style="background:#f0fdf4;padding:7px 10px;text-align:left;border-bottom:1px solid #bbf7d0;color:#64748b;width:55px;">Row</th>
                        <th style="background:#f0fdf4;padding:7px 10px;text-align:left;border-bottom:1px solid #bbf7d0;color:#64748b;width:80px;">Room</th>
                        <th style="background:#f0fdf4;padding:7px 10px;text-align:left;border-bottom:1px solid #bbf7d0;color:#64748b;width:100px;">Date</th>
                        <th style="background:#f0fdf4;padding:7px 10px;text-align:left;border-bottom:1px solid #bbf7d0;color:#64748b;">Title</th>
                        <th style="background:#f0fdf4;padding:7px 10px;text-align:left;border-bottom:1px solid #bbf7d0;color:#64748b;">Time</th>
                    </tr></thead><tbody>`;
                succeeded.forEach(successRow => {
                    html += `<tr>
                        <td style="padding:7px 10px;border-bottom:1px solid #f0fdf4;color:#64748b;">${successRow.row}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #f0fdf4;">${successRow.record.room}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #f0fdf4;">${successRow.record.date}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #f0fdf4;">${successRow.record.title}</td>
                        <td style="padding:7px 10px;border-bottom:1px solid #f0fdf4;">${successRow.record.start_time}–${successRow.record.end_time}</td>
                    </tr>`;
                });
                html += '</tbody></table>';
            }

            document.getElementById('importReportBody').innerHTML = html;
            document.getElementById('importReportModal').classList.add('show');
        }

        return {
            exportBookings,
            importBookings
        };
    }
};
