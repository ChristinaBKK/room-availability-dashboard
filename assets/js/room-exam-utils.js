// Room and exam helper utilities with explicit dependencies.
window.AppRoomExamUtils = {
    createRoomExamUtils({
        blockedRooms,
        knownBRooms,
        roomAliases,
        formatDate,
        normalizeDateFormat,
        getAllRooms,
        getExamDates,
        getAllExamSessions
    }) {
        function normalizeRoom(room) {
            if (!room) return room;
            const rawRoom = String(room).trim().toUpperCase();

            if (roomAliases[rawRoom]) return roomAliases[rawRoom];

            const match = rawRoom.match(/([A-Z]\d{4})/);
            if (match) return match[1];

            return rawRoom;
        }

        function isBRoom(room) {
            const normalized = normalizeRoom(room);
            return /^B\d{4}$/.test(normalized) || normalized.startsWith('B-Seminar Room');
        }

        function getBRoomInventory() {
            const rooms = new Set(knownBRooms);
            blockedRooms.forEach(room => {
                if (isBRoom(room)) rooms.add(normalizeRoom(room));
            });
            getAllRooms().forEach(room => {
                if (isBRoom(room)) rooms.add(normalizeRoom(room));
            });
            return [...rooms].sort((a, b) => a.localeCompare(b));
        }

        function isRoomBlocked(room) {
            const normalized = normalizeRoom(room);
            return blockedRooms.includes(normalized);
        }

        function hasExamOnDate(room, date) {
            const normalized = normalizeRoom(room);
            const examDates = getExamDates();
            return examDates.has(normalized) && examDates.get(normalized).has(date);
        }

        function getProtectedDates() {
            const protectedDates = new Set();
            const examDates = getExamDates();

            for (const dates of examDates.values()) {
                for (const dateStr of dates) {
                    protectedDates.add(dateStr);

                    const [year, month, day] = dateStr.split('/').map(Number);
                    const examDate = new Date(year, month - 1, day);
                    examDate.setDate(examDate.getDate() - 1);
                    const prevDate = `${examDate.getFullYear()}/${String(examDate.getMonth() + 1).padStart(2, '0')}/${String(examDate.getDate()).padStart(2, '0')}`;
                    protectedDates.add(prevDate);
                }
            }

            return protectedDates;
        }

        function isBookingAllowed(room, date) {
            const normalized = normalizeRoom(room);
            const protectedDates = getProtectedDates();
            const examDates = getExamDates();
            return !protectedDates.has(date) || !examDates.has(normalized);
        }

        function getExamProtectionMessage(room, date) {
            const normalized = normalizeRoom(room);
            const examDates = getExamDates();
            if (!examDates.has(normalized)) return null;

            const protectedDates = getProtectedDates();
            if (!protectedDates.has(date)) return null;

            const roomExamDates = [...examDates.get(normalized)];
            const [year, month, day] = date.split('/').map(Number);
            const checkDate = new Date(year, month - 1, day, 12, 0, 0);

            for (const examDateStr of roomExamDates) {
                const [ey, em, ed] = examDateStr.split('/').map(Number);
                const examDate = new Date(ey, em - 1, ed, 12, 0, 0);
                const examPrevDate = new Date(ey, em - 1, ed, 12, 0, 0);
                examPrevDate.setDate(examPrevDate.getDate() - 1);

                if (checkDate.getTime() === examDate.getTime()) {
                    return `Exam scheduled on ${formatDate(examDateStr)} - room protected`;
                }
                if (checkDate.getTime() === examPrevDate.getTime()) {
                    return `Day before exam on ${formatDate(examDateStr)} - room protected`;
                }
            }

            return null;
        }

        function getExamDetailsForRoom(room, date) {
            const normalized = normalizeRoom(room);
            const allExamSessions = getAllExamSessions();
            const examSession = allExamSessions.find(session =>
                normalizeRoom(session.room) === normalized &&
                normalizeDateFormat(session.date) === date &&
                session.isExam
            );
            return examSession || null;
        }

        return {
            normalizeRoom,
            isBRoom,
            getBRoomInventory,
            isRoomBlocked,
            hasExamOnDate,
            getProtectedDates,
            isBookingAllowed,
            getExamProtectionMessage,
            getExamDetailsForRoom
        };
    }
};
